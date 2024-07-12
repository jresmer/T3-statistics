import csv
from dao import DAO


SUKITA = "SUKITA UVA"
PEPSI = "PEPSI COLA"
PRODUCT = "Produto"
SODA = "REFRIGERANTE"
BRAND = "Marca"
PRODUCT_TYPE = "R10 - PET  2L"

with open("data.csv", "r") as file:

    dao = DAO()
    raw_data = csv.DictReader(file)
    row = True
    selected_data = {SUKITA: [], PEPSI: []}

    for _ in range(31808):

        row = next(raw_data)
        if row[PRODUCT] != SODA or row[PRODUCT_TYPE] == "":
            continue

        brand = row[BRAND]
        if brand not in selected_data.keys():
            continue
        
        price = row[PRODUCT_TYPE]
        seg = row["Seg"]
        channel = row["Canal"]
        store = row["Estabelecimento"]
        neighborhood = row["Bairro"]
        price = list(price)
        for i in range(len(price)):

            if price[i] == ",":
                price[i] = "."

        price = "".join(price)
        p_data = {"segment": seg,
                  "channel": channel,
                  "store": store,
                  "neighborhood": neighborhood,
                  "price": float(price)}
        selected_data[brand].append(p_data)

    dao.add(selected_data)
