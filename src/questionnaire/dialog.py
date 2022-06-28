from questionnaire.keyboards import *
from telegram import Update, constants
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
from db_communicator import db
from questionnaire.data_preview import get_user_data_preview, get_check_data


(
    SIZE,
    NAME,
    EMAIL,
    PHONE,
    DELIVERY_TYPE,
    ADDRESS,
    POSTCODE,
    INSTAGRAM,
    VERIFICATION,
) = range(9)


async def start_conversation(update, context):
    size_stock_data = db.sizes_table.get_stock_data()
    pretty_stock_data = "В наличии:\n"
    for size_name in size_stock_data:
        pretty_stock_data += f"{size_name}: {size_stock_data[size_name]}\n"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"/cancel если хотите отменить заполнение данных\n\n{pretty_stock_data}\nКакой размер вам нужен?",
        reply_markup=select_size_keyboard(),
    )

    return SIZE


async def get_size(update, _):
    size_stock_data = db.sizes_table.get_stock_data()
    selected_size = update.message.text
    if size_stock_data[selected_size] == 0:
        await update.message.reply_text(
            "К сожалению, этого размера нет в наличии. Можете выбрать другой.",
            reply_markup=select_size_keyboard(),
        )
        return SIZE

    db.users_table.update_user(update.effective_user.id, "size_name", selected_size)
    await update.message.reply_text("Как к вам обращаться?")
    return NAME


async def get_name(update, _):
    db.users_table.update_user(update.effective_user.id, "name", update.message.text)
    await update.message.reply_text("Укажите ваш email")
    return EMAIL


async def get_email(update, _):
    db.users_table.update_user(update.effective_user.id, "email", update.message.text)
    await update.message.reply_text("Укажите ваш номер телефона")
    return PHONE


async def get_phone(update, _):
    db.users_table.update_user(update.effective_user.id, "phone", update.message.text)
    await update.message.reply_text(
        "Выберите способ получения заказа\n- Самовывоз из (...)\n- Доставка по России (400 руб)",
        reply_markup=select_delivery_type_keyboard(),
    )
    return DELIVERY_TYPE


async def get_delivery_type(update, _):
    del_type = "pickup" if update.message.text == "Самовывоз" else "courier"
    db.users_table.update_user(update.effective_user.id, "delivery_type", del_type)
    if del_type == "courier":
        await update.message.reply_text("Укажите адрес доставки")
        return ADDRESS
    else:
        await update.message.reply_text(
            "Можете указать свой Instagram\n/skip если не хотите"
        )
        return INSTAGRAM


async def get_address(update, _):
    db.users_table.update_user(update.effective_user.id, "address", update.message.text)
    await update.message.reply_text("Укажите ваш почтовый индекс")
    return POSTCODE


async def get_postcode(update, _):
    db.users_table.update_user(
        update.effective_user.id, "postcode", update.message.text
    )
    await update.message.reply_text(
        "Можете указать свой Instagram\n/skip если не хотите"
    )
    return INSTAGRAM


async def get_instagram(update, _):
    db.users_table.update_user(
        update.effective_user.id, "instagram", update.message.text
    )
    await update.message.reply_text(
        f"{get_user_data_preview(update.effective_user.id)}\n\nУбедитесь, что все данные внесены корректно",
        reply_markup=verify_data_keyboard(),
    )
    return VERIFICATION


async def skip_instagram(update, _):
    db.users_table.update_user(update.effective_user.id, "instagram", None)
    await update.message.reply_text(
        f"{get_user_data_preview(update.effective_user.id)}\n\nУбедитесь, что все данные внесены корректно",
        reply_markup=verify_data_keyboard(),
    )
    return VERIFICATION


async def get_verification(update, _):
    if update.message.text == "Все верно":
        message, amount = get_check_data(update.effective_user.id)
        await update.message.reply_text(
            text=message,
            reply_markup=go_to_payment(amount),
        )
        return ConversationHandler.END
    else:
        size_stock_data = db.sizes_table.get_stock_data()
        pretty_stock_data = "В наличии:\n"
        for size_name in size_stock_data:
            pretty_stock_data += f"{size_name}: {size_stock_data[size_name]}\n"
        await update.message.reply_text(
            text=f"{pretty_stock_data}\nКакой размер вам нужен?",
            reply_markup=select_size_keyboard(),
        )
        return SIZE


async def cancel(update, _):
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_conversation, pattern="order")],
    states={
        SIZE: [MessageHandler(filters.Regex("^(S|M|L|XL)$"), get_size)],
        NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_name)],
        EMAIL: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_email)],
        PHONE: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_phone)],
        DELIVERY_TYPE: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), get_delivery_type)
        ],
        ADDRESS: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_address)],
        POSTCODE: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_postcode)],
        INSTAGRAM: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), get_instagram),
            CommandHandler("skip", skip_instagram),
        ],
        VERIFICATION: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), get_verification)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
