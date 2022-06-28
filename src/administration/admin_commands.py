from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS, SIZES
from db_communicator import db


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
