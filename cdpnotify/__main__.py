import json
import logging
import os
import time
from typing import Dict

from cdpnotify import rpc, persistence, chain
from cdpnotify.persistence import CDPEntity

logger = logging.getLogger(__name__)

logger.debug('Loading config...')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s')
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.getLogger('telegram').setLevel(logging.INFO)

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'config.json')) as fp:
    CONF = json.load(fp)


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
    logger.info('Starting CDP Watchdog...')

    rpc.init(CONF['telegram_token'])
    persistence.init('sqlite:///cdps.sqlite')

    while True:
        eth_price = chain.get_eth_price_feed()
        logger.info('Current ETH/USD price: %s$', eth_price)

        # Check liquidation values for all known CDPs
        for entity in persistence.CDPEntity.query.all():
            try:
                logger.info('Checking CDP-%s liquidation values...', entity.cdp_id)
                cdp = chain.get_cdp_by_id(entity.cdp_id)
                chain.populate_liquidation_values(cdp)

                if 0 < cdp['col_ratio'] < entity.notification_ratio:
                    notify_user(cdp, entity)
                    persistence.CDPEntity.query.filter(
                        persistence.CDPEntity.id == entity.id
                    ).delete()
            except Exception:
                logger.exception('Exception occurred in main loop')

        persistence.CDPEntity.session.flush()
        time.sleep(15 * 4)  # Update on all 4 blocks


if __name__ == '__main__':
    main()
