import logging
from typing import List

from sqlalchemy import and_
from telegram.bot import Bot, Update
from telegram.error import NetworkError, TelegramError
from telegram.ext import CommandHandler, Updater
from telegram.parsemode import ParseMode

from cdpnotify.persistence import CDPEntity

logger = logging.getLogger(__name__)

UPDATER = None


def init(token: str) -> None:
    """ Initialize rpc module """
    global UPDATER

    UPDATER = Updater(token=token, workers=0)

    # Register command handler and start telegram message polling
    handles = [
        CommandHandler('help', _help_callback),
        CommandHandler('watch', _watch_callback, pass_args=True),
        CommandHandler('unwatch', _unwatch_callback, pass_args=True),
    ]
    for handle in handles:
        UPDATER.dispatcher.add_handler(handle)
        UPDATER.start_polling(
            clean=True,
            bootstrap_retries=-1,
            timeout=30,
            read_latency=60,
        )
    logger.info(
        'rpc.telegram is listening for following commands: %s',
        [h.command for h in handles]
    )


def _watch_callback(bot: Bot, update: Update, args: List[str]) -> None:
    """ /watch callback """
    if not 0 < len(args) < 3:
        _help_callback(bot, update)
        return

    try:
        cdp_id = int(args[0])
        col_ratio = int(args[1].rstrip('%')) / 100 if len(args) == 2 else 2.0
    except ValueError:
        _help_callback(bot, update)
        return

    # Check if current user is already watching this CDP
    if CDPEntity.query.filter(
        and_(
            CDPEntity.telegram_user_id == update.message.from_user.id,
            CDPEntity.cdp_id == cdp_id,
        )
    ).first():
        send_msg(
            'Already watching `CDP-{}`!'.format(cdp_id),
            update.message.chat.id,
            bot=bot,
        )
        return

    CDPEntity.session.add(
        CDPEntity(
            telegram_user_id=update.message.from_user.id,
            telegram_chat_id=update.message.chat.id,
            notification_ratio=col_ratio,
            cdp_id=cdp_id,
        )
    )
    CDPEntity.session.flush()
    send_msg(
        'Sending you a private message if collateralization rate of `CDP-{}` drops below `{}%`'.format(
            cdp_id, int(col_ratio * 100),
        ),
        update.message.chat.id,
        bot=bot,
    )


def _unwatch_callback(bot: Bot, update: Update, args: List[str]) -> None:
    """ /unwatch callback """
    if len(args) != 1:
        _help_callback(bot, update)
        return

    try:
        cdp_id = int(args[0])
    except ValueError:
        _help_callback(bot, update)
        return

    # Check if current user is indeed watching this CDP
    entity = CDPEntity.query.filter(
        and_(
            CDPEntity.telegram_user_id == update.message.from_user.id,
            CDPEntity.cdp_id == cdp_id,
        )
    ).first()

    if entity:
        CDPEntity.query.filter(CDPEntity.id == entity.id).delete()
        CDPEntity.session.flush()
        msg = 'You are no longer watching `CDP-{}`'.format(cdp_id)
    else:
        msg = '`CDP-{}` is not on your watchlist!'.format(cdp_id)

    send_msg(msg, update.message.chat.id, bot=bot)


def _help_callback(bot: Bot, update: Update) -> None:
    """ /help callback """
    message = '*/watch <cdp_id> [<ratio>]:* Add a CDP with the given ID to your watchlist.\n' \
              'The bot will send you a private notification if the collateralization is below the given ratio `(default=200%)`\n' \
              '\n' \
              '*/unwatch <cdp_id>*: Remove CDP from your watchlist\n' \
              '*/help*: Show this message'

    send_msg(message, update.message.chat.id, bot=bot)


def send_msg(msg: str, user_id: str, bot: Bot = None) -> None:
    """ Sends a message to the given user or chat_id """
    bot = bot or UPDATER.bot

    try:
        try:
            bot.send_message(
                user_id,
                text=msg,
                parse_mode=ParseMode.MARKDOWN,
            )
        except NetworkError as network_err:
            # Sometimes the telegram server resets the current connection,
            # if this is the case we send the message again.
            logger.warning(
                'Telegram NetworkError: %s! Trying one more time.',
                network_err.message
            )
            bot.send_message(
                user_id,
                text=msg,
                parse_mode=ParseMode.MARKDOWN,
            )
    except TelegramError as telegram_err:
        logger.warning(
            'TelegramError: %s! Giving up on that message.',
            telegram_err.message
        )
