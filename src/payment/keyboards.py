from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def select_amount_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("100", callback_data="pay 100")],
            [InlineKeyboardButton("300", callback_data="pay 300")],
            [InlineKeyboardButton("500", callback_data="pay 500")],
        ]
    )


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
