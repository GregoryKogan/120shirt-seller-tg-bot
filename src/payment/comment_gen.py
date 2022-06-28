import random
import string
import datetime


def gen_comment(user_id: int, amount: float, k: int = 10):
    random_str = "".join(
        random.choices(
            string.ascii_uppercase + string.digits + string.ascii_lowercase, k=k
        )
    )
    timestamp = int(round(datetime.datetime.now().timestamp()))
    return f"{user_id}${timestamp}${amount}${random_str}"
