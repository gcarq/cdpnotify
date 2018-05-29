import json
import logging
import os
import time
from decimal import Decimal
from typing import Dict

from web3 import Web3, HTTPProvider
from web3.utils.encoding import pad_bytes

from cdpnotify import rpc, persistence

# See https://github.com/makerdao/sai
#     http://developer.makerdao.com/dai/1/api/
from cdpnotify.persistence import CDPEntity


logger = logging.getLogger(__name__)

w3, tub, pip, vox = None, None, None, None


def load_abi(filename: str) -> Dict:
    """ Loads an ABI definition with the given filename from abis/ """
    logger.debug('Loading ABI for %s...', filename)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'abis', filename)) as fp:
        return json.load(fp)


def get_eth_price_feed() -> float:
    """ Returns the current ETH/USD price rate from the given feed """

    logger.debug('Fetching ETH price feed...')
    price = int.from_bytes(
        pip.functions.read().call(),
        byteorder='big',
    )
    return w3.fromWei(price, 'ether')


def get_cdp_by_id(cdp_id: int) -> Dict:
    """ Returns a CDP for the given CDP id """

    logger.debug('Fetching CDP (id=%s)...', cdp_id)
    # Convert to bytes and apply padding to match bytes32
    padded_cdp_id = pad_bytes(b'\x00', 32, w3.toBytes(cdp_id))
    lad, ink, art, ire = tub.functions.cups(padded_cdp_id).call()
    return {
        'id': cdp_id,
        'lad': lad,  # CDP owner
        'ink': w3.fromWei(ink, 'ether'),  # Locked collateral (in SKR)
        'art': w3.fromWei(art, 'ether'),  # Outstanding normalised debt (tax only)
        'ire': w3.fromWei(ire, 'ether'),  # Outstanding normalised debt
    }


def populate_liquidation_values(cdp: Dict) -> None:
    """ Calculates liquidation price and liquidation ratio and updates the given CDP dict """

    logger.debug('Populating liquidation values...')
    # Check if CDP is closed
    if cdp['lad'] == '0x0000000000000000000000000000000000000000':
        logger.debug('CDP is closed')
        return

    if cdp['ink'] > 0 and cdp['art'] > 0:
        # Calculate collateralization ratio
        cdp['col_ratio'] = cdp['ink'] * tub.functions.tag().call() \
            / (cdp['art'] * vox.functions.par().call())

        # Calculate liquidation price
        cdp['liq_price'] = cdp['art'] * tub.functions.mat().call() \
            / tub.functions.per().call() / cdp['ink']

    else:
        cdp['col_ratio'] = Decimal(0.0)
        cdp['liq_price'] = Decimal(0)

    logger.info(
        'CDP-%s: col_ratio=%s%%, liq_price=%s$',
        cdp['id'], round(cdp['col_ratio'] * 100, 2), round(cdp['liq_price'], 2),
    )


def notify_user(cdp: Dict, entity: CDPEntity) -> None:
    """ Sends a warn notification to the given user """
    logger.debug('Sending notification to user...')
    msg = '`CDP-{}` collateralization ratio is below `{}%`:\n' \
          'Ratio: `{}%`\n' \
          'Liquidation price: `{}$`'.format(
            cdp['id'],
            int(entity.notification_ratio * 100),
            round(cdp['col_ratio'] * 100, 2),
            round(cdp['liq_price'], 2),
          )
    rpc.send_msg(msg, entity.telegram_user_id)


def main():
    global w3, tub, pip, vox

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s - %(message)s')
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('telegram').setLevel(logging.INFO)

    logger.info('Starting CDP Watchdog...')

    logger.debug('Loading config...')
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'config.json')) as fp:
        config = json.load(fp)

    rpc.init(config['telegram_token'])
    persistence.init('sqlite:///cdps.sqlite')

    # web3.py instance
    w3 = Web3(HTTPProvider(config['hosted_node_url']))

    tub = w3.eth.contract(address=config['tub_address'], abi=load_abi('tub.json'))

    # get the gem price feed contract address and instantiate as contract
    pip = w3.eth.contract(
        address=tub.functions.pip().call(),
        abi=load_abi('pip.json'),
    )

    vox = w3.eth.contract(
        address=tub.functions.vox().call(),
        abi=load_abi('vox.json'),
    )

    while True:
        eth_price = get_eth_price_feed()
        logger.info('Current ETH/USD price: %s$', eth_price)

        # Check liquidation values for all known CDPs
        for entity in persistence.CDPEntity.query.all():
            logger.info('Checking CDP-%s liquidation values...', entity.cdp_id)
            cdp = get_cdp_by_id(entity.cdp_id)
            populate_liquidation_values(cdp)

            if 0 < cdp['col_ratio'] < entity.notification_ratio:
                notify_user(cdp, entity)
                persistence.CDPEntity.query.filter(
                    persistence.CDPEntity.id == entity.id
                ).delete()

        persistence.CDPEntity.session.flush()
        time.sleep(15 * 4)  # Update on all 4 blocks


if __name__ == '__main__':
    main()
