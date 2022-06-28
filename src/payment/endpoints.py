from payment.keyboards import *
from telegram import Update, constants
from telegram.ext import ContextTypes
from db_communicator import db
from pyqiwip2p import AioQiwiP2P
from config import BILL_LIFETIME
from api_keys import QIWI_P2P_SECRET
from payment.comment_gen import gen_comment

p2p = AioQiwiP2P(auth_key=QIWI_P2P_SECRET)


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE, query_data: str):
    amount = 0
    try:
        amount = int(query_data[len("pay ") :])
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Введите целое число"
        )
        return
    if amount < 50:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Минимальная сумма платежа - 50 рублей",
        )
        return

    comment = gen_comment(update.effective_user.id, amount)
    bill = await p2p.bill(amount=amount, comment=comment, lifetime=BILL_LIFETIME)
    db.checks_table.add_check(update.effective_user.id, amount, bill.bill_id, comment)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Сформирован чек на оплату {bill.amount} рублей. Он будет действителен {BILL_LIFETIME} минут.\nОплатить можно по ссылке: {bill.pay_url}.\n\n<b>Убедитесь, что при оплате указан комментрий:</b>\n<code>{comment}</code>",
        parse_mode=constants.ParseMode.HTML,
        reply_markup=pay_and_check_payment_keyboard(bill),
    )


async def check_payment(
    update: Update, context: ContextTypes.DEFAULT_TYPE, query_data: str
):
    bill_id = query_data[len("check_payment ") :]
    bill_db_record = db.checks_table.get_check(bill_id)
    if bill_db_record is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Чек не найден",
        )
        return

    if bill_db_record["status"] == "PAID":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Оплата прошла успешно!",
        )
        return

    bill = await p2p.check(bill_id=bill_id)

    if bill.status == "PAID":
        db.checks_table.pay_check(bill_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Оплата прошла успешно!",
        )
        return
    elif bill.status == "EXPIRED":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="У чека закончился срок годности",
            reply_markup=check_payment_keyboard(bill_id),
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Чек не оплачен",
            reply_markup=check_payment_keyboard(bill_id),
        )
