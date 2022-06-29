from payment.keyboards import *
from telegram import Update, constants
from telegram.ext import ContextTypes
from db_communicator import db
from pyqiwip2p import AioQiwiP2P
from config import BILL_LIFETIME, CONTACT_LINK
from api_keys import QIWI_P2P_SECRET
from payment.comment_gen import gen_comment
from administration.admin_commands import notify_owner_about_new_order

p2p = AioQiwiP2P(auth_key=QIWI_P2P_SECRET)


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE, query_data: str):
    amount = 0
    try:
        amount = float(query_data[len("pay ") :])
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Введите число"
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
            text=f"Оплата прошла успешно!\nМы с вами свяжемся. Если есть какие-либо вопросы, можете задать их нам: {CONTACT_LINK}",
            reply_markup=buy_again_keyboard(),
        )
        return

    bill = await p2p.check(bill_id=bill_id)

    if bill.status == "PAID":
        if not db.orders_table.exists(bill_id):
            db.orders_table.add_order(update.effective_chat.id, bill_id)
            await notify_owner_about_new_order(
                update, context, update.effective_chat.id, bill_id
            )
        db.checks_table.pay_check(bill_id)
        db.sizes_table.decrease_quantity(bill_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Оплата прошла успешно!\nМы с вами свяжемся. Если есть какие-либо вопросы, можете задать их нам: {CONTACT_LINK}",
            reply_markup=buy_again_keyboard(),
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


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = db.orders_table.get_user_orders(update.effective_user.id)
    pretty_orders = "Заказы: "
    for order in orders:
        pretty_orders += "\n\n-------------"
        pretty_orders += f"\nРазмер: {order['size_name']}"
        pretty_orders += f"\nТелефон: {order['phone']}"
        if order["delivery_type"] == "courier":
            pretty_orders += "\nТип доставки: курьером"
        else:
            pretty_orders += "\nТип доставки: самовывоз"
        if order["delivery_type"] == "courier":
            pretty_orders += f"\nАдрес: {order['address']}"
            pretty_orders += f"\nПочтовый индекс: {order['postcode']}"
        pretty_orders += f"\nИтого: {order['amount']}р."

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=pretty_orders,
    )
