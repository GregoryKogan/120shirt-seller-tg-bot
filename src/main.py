import logging
from time import sleep
from telegram import (
    Update,
    constants,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)
from payment.endpoints import pay, check_payment, my_orders
from questionnaire.dialog import conv_handler
from api_keys import BOT_TOKEN
from db_communicator import db
from administration.admin_commands import *

logging.basicConfig(
    filename="logs.log",
    encoding="utf-8",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not db.users_table.exists(update.effective_user.id):
        db.users_table.add_user(
            update.effective_user.id, f"@{update.effective_user.username}"
        )

    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open("src/assets/siesta for a real man.png", "rb"),
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='<b>T-SHIRT "SIESTA FOR A REAL MAN"</b>\n\n- ткань: 100% хлопок, 230г плотность\n- шелкография\n- оверсайз\n\nУход:\n- стирать при 30° и наизнанку, отжим не выше 400',
        parse_mode=constants.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Заказать", callback_data="order")]]
        ),
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="pong!",
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Не понимаю вас..."
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Извините, я не знаю такой команды",
    )


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "my_orders":
        await my_orders(update, context)
    elif query.data.startswith("pay"):
        await pay(update, context, query_data=query.data)
    elif query.data.startswith("check_payment"):
        await check_payment(update, context, query_data=query.data)


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    ping_handler = CommandHandler("ping", ping)
    update_stock_handler = CommandHandler("stock", update_stock)
    get_orders_handler = CommandHandler("orders", get_orders)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    callback_query_handler = CallbackQueryHandler(handle_callback_query)

    application.add_handler(start_handler)
    application.add_handler(ping_handler)
    application.add_handler(update_stock_handler)
    application.add_handler(get_orders_handler)
    application.add_handler(conv_handler)
    application.add_handler(callback_query_handler)
    application.add_handler(unknown_handler)
    application.add_handler(echo_handler)

    while True:
        try:
            application.run_polling()
        except Exception as e:
            logger.error(e)
            sleep(5)
