from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def pay_and_check_payment_keyboard(bill):
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Оплатить", url=bill.pay_url)],
            [
                InlineKeyboardButton(
                    "Проверить оплату", callback_data=f"check_payment {bill.bill_id}"
                )
            ],
        ]
    )


def check_payment_keyboard(bill_id: str):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Проверить оплату", callback_data=f"check_payment {bill_id}"
                )
            ],
        ]
    )


def buy_again_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Мои заказы", callback_data="my_orders")],
            [InlineKeyboardButton("Заказать ещё", callback_data="order")],
        ]
    )
