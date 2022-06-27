import logging
from telegram import (
    Update,
    constants,
    KeyboardButton,
    ReplyKeyboardMarkup,
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
from pyqiwip2p import QiwiP2P

from api_keys import BOT_TOKEN, QIWI_P2P_SECRET
from config import BILL_LIFETIME
from db_communicator import DBCommunicator
from comment_gen import gen_comment

db = DBCommunicator()
p2p = QiwiP2P(QIWI_P2P_SECRET)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not db.users_table.user_exists(update.effective_user.id):
        db.users_table.add_user(update.effective_user.id)

    buttons = [[InlineKeyboardButton("Заплатить", callback_data="select_amount")]]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Это бот для демонстрации оплаты по QIWI",
        reply_markup=InlineKeyboardMarkup(buttons),
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

    if query.data == "select_amount":
        await select_amount(update=update, context=context)
    elif query.data.startswith("pay"):
        await pay(update=update, context=context, query_data=query.data)
    elif query.data.startswith("check_payment"):
        await check_payment(update=update, context=context, query_data=query.data)


async def select_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("100", callback_data="pay 100")],
        [InlineKeyboardButton("300", callback_data="pay 300")],
        [InlineKeyboardButton("500", callback_data="pay 500")],
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Сколько рублей вы хотите заплатить?",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE, query_data: str):
    amount = 0
    try:
        amount = int(query_data[len("pay ") :])
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите целое число",
        )
        return
    if amount < 50:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Минимальная сумма платежа - 50 рублей",
        )
        return

    comment = gen_comment(update.effective_user.id, amount)
    bill = p2p.bill(amount=amount, comment=comment, lifetime=BILL_LIFETIME)
    db.checks_table.add_check(update.effective_user.id, amount, bill.bill_id)

    buttons = [
        [InlineKeyboardButton("Оплатить", url=bill.pay_url)],
        [
            InlineKeyboardButton(
                "Проверить оплату", callback_data=f"check_payment {bill.bill_id}"
            )
        ],
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Сформирован чек на оплату {amount} рублей. Он будет действителен {BILL_LIFETIME} минут.\nОплатить можно по ссылке: {bill.pay_url}.\n\n<b>Убедитесь, что при оплате указан комментрий:</b>\n<code>{comment}</code>",
        parse_mode=constants.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def check_payment(
    update: Update, context: ContextTypes.DEFAULT_TYPE, query_data: str
):
    bill_id = query_data[len("check_payment ") :]
    bill_data = db.checks_table.get_check(bill_id)
    if bill_data is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Чек не найден",
        )
    elif p2p.check(bill_id=bill_id).status == "PAID":
        money = db.users_table.user_get_money(update.effective_user.id)
        db.users_table.user_set_money(update.effective_user.id, money + bill_data[2])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Оплата прошла успешно!",
        )
    else:
        buttons = [
            [
                InlineKeyboardButton(
                    "Проверить оплату", callback_data=f"check_payment {bill_id}"
                )
            ],
        ]
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Чек не оплачен",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler("start", start)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    callback_query_handler = CallbackQueryHandler(handle_callback_query)

    application.add_handler(start_handler)
    application.add_handler(unknown_handler)
    application.add_handler(echo_handler)
    application.add_handler(callback_query_handler)

    application.run_polling()
