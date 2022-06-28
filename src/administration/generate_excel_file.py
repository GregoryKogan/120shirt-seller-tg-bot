import xlsxwriter


def gen_file(orders_data, users_data, checks_data):
    workbook = xlsxwriter.Workbook("src/assets/SellData.xlsx")
    write_orders_sheet(workbook, orders_data)
    write_users_sheet(workbook, users_data)
    write_checks_sheet(workbook, checks_data)
    workbook.close()


def write_orders_sheet(workbook, orders_data):
    orders_sheet = workbook.add_worksheet(name="Orders")
    headers = [
        "id",
        "user_id",
        "telegram_username",
        "amount",
        "bill_id",
        "created_at",
        "size_name",
        "name",
        "email",
        "phone",
        "delivery_type",
        "address",
        "postcode",
        "instagram",
    ]

    for col in range(len(headers)):
        orders_sheet.write(0, col, headers[col])

    for row, order in enumerate(orders_data, start=1):
        for col in range(len(order)):
            orders_sheet.write(row, col, order[col])


def write_users_sheet(workbook, users_data):
    users_sheet = workbook.add_worksheet(name="Users")
    headers = [
        "id",
        "user_id",
        "telegram_username",
        "name",
        "email",
        "phone",
        "address",
        "postcode",
        "instagram",
    ]

    for col in range(len(headers)):
        users_sheet.write(0, col, headers[col])

    for row, user in enumerate(users_data, start=1):
        users_sheet.write(row, 0, user[0])
        users_sheet.write(row, 1, user[1])
        users_sheet.write(row, 2, user[2])
        users_sheet.write(row, 3, user[4])
        users_sheet.write(row, 4, user[5])
        users_sheet.write(row, 5, user[6])
        users_sheet.write(row, 6, user[8])
        users_sheet.write(row, 7, user[9])
        users_sheet.write(row, 8, user[10])


def write_checks_sheet(workbook, checks_data):
    checks_sheet = workbook.add_worksheet(name="Checks")
    headers = ["id", "user_id", "amount", "bill_id", "comment", "created_at", "status"]

    for col in range(len(headers)):
        checks_sheet.write(0, col, headers[col])

    for row, check in enumerate(checks_data, start=1):
        for col in range(len(check)):
            checks_sheet.write(row, col, check[col])
