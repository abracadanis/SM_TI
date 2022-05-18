import requests
import json
import os
import pandas as pd
import datetime
import xlsxwriter



urlTI = "https://tradeit.gg/api/v2/inventory/data?gameId=252490&offset=0&sortType=Popularity&searchValue=&minPrice=0&maxPrice=100000&fresh=true&limit=3000"

payload={}
headers = {
  'authority': 'skinsmonkey.com',
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'ru-RU,ru;q=0.9,sk-SK;q=0.8,sk;q=0.7,en-US;q=0.6,en;q=0.5',
  'cache-control': 'no-cache',
  'dnt': '1',
  'pragma': 'no-cache',
  'referer': 'https://skinsmonkey.com/ru/trade',
  'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'
}

list_of_items_sm = []
names = []
prices_TI = []
prices_SM = []
percentage_TI_SM = []
percentage_SM_TI = []
number_of_items_SM = []
number_of_items_TI = []

def collect():
    response = requests.request("GET", urlTI, headers=headers, data=payload)

    items_TI = json.loads(response.text)['items']

    offset = 0
    while True:
        url_SM = f'https://skinsmonkey.com/api/inventory?limit=300&offset={offset}&appId=252490&virtual=false&sort=price-desc&featured=false'
        response = requests.request("GET", url_SM, headers=headers, data=payload)

        dataSM = json.loads(response.text)
        assets_SM = dataSM.get('assets')

        offset += 300

        for item in assets_SM:
            list_of_items_sm.append(item)

        if len(assets_SM) < 300:
            break

    check_names = []
    for item in items_TI:
        for asset in list_of_items_sm:
            if item.get('name').lower() == asset.get('item').get('marketName').lower():
                flag = 1
                for name in check_names:
                    if name == item.get('name'):
                        flag = 0
                if flag:
                    check_names.append(item.get('name'))
                    names.append(item.get('name'))
                    price1 = float(str(item.get('price'))[:-2] + "." + str(item.get('price'))[-2:])
                    prices_TI.append(round(price1*0.898, 2))
                    price2 = float(str(asset.get('item').get('price'))[:-2] + "." + str(asset.get('item').get('price'))[-2:])
                    prices_SM.append(round(price2*0.865, 2))
                    percentage_TI_SM.append(price1/price2 * 100 - 100)
                    percentage_SM_TI.append(price2/price1 * 100 - 100)
                    number_of_items_SM.append(asset.get('overstock').get('stock'))
                    number_of_items_TI.append(asset.get('overstock').get('stock'))

    df = pd.DataFrame({'Name': names,
                       'Price TI': prices_TI,
                       'Price SM': prices_SM,
                       'Number of items (SM)': number_of_items_SM,
                       'TI > SM': percentage_TI_SM,
                       'SM > TI': percentage_SM_TI
                       })
    writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='welcome', index=False)
    writer.save()


def main():
    collect()


if __name__ == '__main__':
    main()
