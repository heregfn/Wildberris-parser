import aiohttp
from fake_useragent import UserAgent
import asyncio
import pandas as pd
import time

ua = UserAgent()
heandlers = {
        "user-agent": ua.ie
    }

async def pars(url):
    async with aiohttp.ClientSession(headers=heandlers) as session:
        time1 = time.time()
        response = await session.get(url)
        answer = await response.json(encoding=response.get_encoding(), content_type=None)
        a = response.get_encoding()
        total_count = answer.get("data").get("total")
        filters = answer.get("data").get("filters")
        ids = []
        for loop in filters:
            items = loop.get('items')
            for item in items:
                id = item.get("id")
                if id is not ids:
                    ids.append(id)
        time2 = time.time() - time1
        print(f"Потраченно на получение Id: {time2}")
    await Get_id_seller(ids, total_count)

async def idsa(id, data, loop, session, total_count):
    try:
        async with session.get(
    f"https://catalog.wb.ru/catalog/children/catalog?appType=1&couponsGeo=2,12,7,3,6,13,21&curr=rub&dest=-1113276,-79379,-1104258,-5803327&emp=0&fsupplier={id}&kind=3;5&lang=ru&locale=ru&page=1&pricemarginCoeff=1.0&reg=0&regions=64,58,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48&sort=priceup&spp=0&subject=2;108;3497") as response:
            answer = await response.json(encoding=response.get_encoding(), content_type=None)
            id1 = answer.get("data").get("products")[0].get("id")
            name = answer.get("data").get("products")[0].get("name")
            brand = answer.get("data").get("products")[0].get("brand")
            url = f"https://www.wildberries.ru/catalog/{id1}/detail.aspx?targetUrl=XS"
            try:
                async with session.get(f"https://wbx-content-v2.wbstatic.net/sellers/{id1}.json") as response:
                    answer = await response.json(encoding=response.get_encoding(), content_type=None)
                    name1 = answer.get("supplierName")
                    ogrn = answer.get("ogrn")
            except Exception as e:
                print(e)
            data.append({
                "category": "children",
                "name": name,
                "brand": brand,
                "orgonization": name1,
                "ogrn": ogrn,
                "url": url
            })
            print(f'{total_count}/{loop}')
    except Exception as e:
        print(e)


async def Get_id_seller(ids, total_count):
    time1 = time.time()
    data = []
    tasks = []
    loop = 1
    total_count = len(ids)
    async with aiohttp.ClientSession(headers=heandlers) as session:
        for id in ids:
            task = asyncio.ensure_future(idsa(id, data, loop, session, total_count))
            tasks.append(task)
            loop = loop + 1
        responses = asyncio.gather(*tasks)
        await responses
    time2 = time.time() - time1
    print(f"Потраченно на получение Товаров: {time2}")
    with open('data_product.txt', 'w', encoding="utf-8") as fp:
        for item in data:
            try:
                fp.write(f"{item}\n")
            except Exception as e:
                print(e)
        List_to_xls(data)
        print('Done')


def List_to_xls(data):
    category = []
    name = []
    brand = []
    orgonization = []
    ogrn = []
    url = []
    id = []
    loop = 1
    for d in data:
        categor = d.get("category")
        nam = d.get("name")
        bran = d.get("brand")
        orgonizatio = d.get("orgonization")
        ogr = d.get("ogrn")
        ur = d.get("url")
        category.append(categor)
        name.append(nam)
        brand.append(bran)
        orgonization.append(orgonizatio)
        ogrn.append(ogr)
        url.append(ur)
        id.append(loop)
        loop = loop + 1

    df = pd.DataFrame({
        "№ п/п (порядковый номер)": id,
        "Наименование категории товара": category,
        "Наименование товара": name,
        "Название бренда": brand,
        "Название юр.лица": orgonization,
        "ОРГН Юр.лица": ogrn,
        "Ссылка на карточку товара": url
    })
    df.to_excel('./Parsings.xlsx')

if __name__ == '__main__':
    a = 1
    asyncio.run(pars("https://catalog.wb.ru/catalog/children/v4/filters?filters=fsupplier&kind=3;5&subject=2;108;3497&spp=0&regions=64,58,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48&pricemarginCoeff=1.0&reg=0&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=2,12,7,3,6,13,21&dest=-1113276,-79379,-1104258,-5803327"))