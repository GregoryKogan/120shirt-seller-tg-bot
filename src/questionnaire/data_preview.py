from db_communicator import db
from config import SHIRT_PRICE, DELIVERY_PRICE


def get_user_data_preview(user_id: int) -> str:
    user_data = db.users_table.get(user_id)
    if user_data is None:
        return ""

    data = ""
    data += f"Размер: {user_data['size_name']}\n"
    data += f"Имя: {user_data['name']}\n"
    data += f"Email: {user_data['email']}\n"
    data += f"Телефон: {user_data['phone']}\n"
    if user_data["delivery_type"] == "courier":
        data += "Тип доставки: курьером\n"
    else:
        data += "Тип доставки: самовывоз\n"
    if user_data["delivery_type"] == "courier":
        data += f"Адрес: {user_data['address']}\n"
        data += f"Почтовый индекс: {user_data['postcode']}\n"
    if user_data["instagram"] is not None:
        data += f"Instagram: {user_data['instagram']}"
    else:
        data += "Instagram: не указан"

    return data


def get_check_data(user_id: int) -> (str, float):
    user_data = db.users_table.get(user_id)
    if user_data is None:
        return ""

    total_price = SHIRT_PRICE
    data = f"Футболка '120' - {SHIRT_PRICE}р."
    if user_data["delivery_type"] == "courier":
        data += f"\nДоставка по России - {DELIVERY_PRICE}р."
        total_price += DELIVERY_PRICE
    data += f"\n\nИТОГО: {total_price}р."
    return data, total_price
