import datetime
import json
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS, SIZES
from db_communicator import db
from administration.generate_excel_file import gen_file


async def update_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    try:
        quantities = list(map(int, context.args))
    except ValueError:
        s = "".join(f"{str(5 + i)} " for i in range(len(SIZES)))[:-1]
        await update.message.reply_text(
            text=f"Введите {len(SIZES)} целые числа. Например:\n'/stock {s}'",
        )
        return

    if len(quantities) != len(SIZES):
        s = "".join(f"{str(5 + i)} " for i in range(len(SIZES)))[:-1]
        await update.message.reply_text(
            text=f"Введите {len(SIZES)} целые числа. Например:\n'/stock {s}'",
        )
        return

    for i in range(len(SIZES)):
        size_name = SIZES[i]
        quantity = quantities[i]
        db.sizes_table.set_quantity(size_name, quantity)

    await update.message.reply_text(
        text=str(db.sizes_table.get_stock_data()),
    )


async def get_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Создаётся Excel файл..."
    )

    orders_data = db.orders_table.get_all_orders()
    users_data = db.users_table.get_all_users()
    checks_data = db.checks_table.get_all_checks()
    gen_file(orders_data, users_data, checks_data)

    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open("src/assets/SellData.xlsx", "rb"),
        filename="SellData.xlsx",
    )


async def notify_owner_about_new_order(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, bill_id: str
):
    created_at = datetime.datetime.now().isoformat()
    user_data = db.users_table.get(user_id)
    check_data = db.checks_table.get_check(bill_id)

    new_order_data = {
        "user_id": user_id,
        "telegram_username": user_data["telegram_username"],
        "amount": check_data["amount"],
        "bill_id": bill_id,
        "created_at": created_at,
        "size_name": user_data["size_name"],
        "name": user_data["name"],
        "email": user_data["email"],
        "phone": user_data["phone"],
        "delivery_type": user_data["delivery_type"],
        "address": user_data["address"],
        "postcode": user_data["postcode"],
        "instagram": user_data["instagram"],
    }

    pretty_data = json.dumps(new_order_data, indent=2, ensure_ascii=False)

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin_id, text=f"Новый заказ!\n\n{pretty_data}"
        )
