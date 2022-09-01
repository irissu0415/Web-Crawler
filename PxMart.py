import requests
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from bs4 import BeautifulSoup
import datetime
import time
import csv
import os


class PxMart:
    def __init__(self):
        self.headless = ChromeOptions()
        self.headless.add_argument('--headless')
        self.driver = webdriver.Chrome('./chromedriver', options=self.headless)

    # 依商品類別建立存放圖片的資料庫
    def makeFolder(self):
        if not os.path.exists("./pxgo"):
            os.mkdir("./pxgo")

        for i in category_other:
            if not os.path.exists("./pxgo/{}".format(i)):
                os.mkdir("./pxgo/{}".format(i))

        if not os.path.exists("./pxgo/drink"):
            os.mkdir("./pxgo/drink")

    def get_content(self, category_url, category, category_drink):
        # 做出所有商品類別網址
        url_list = []
        for i in category_url:
            category_url = "https://shop.pxmart.com.tw/v2/official/SalePageCategory/{}?sortMode=Curator".format(i)
            url_list.append(category_url)

        # 抓取每個商品類別頁面裡的所有商品資訊
        all_info = []
        for i in url_list:
            index = url_list.index(i)
            self.driver.get(i)
            time.sleep(3)

            for a in range(2, 10):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            size = soup.select(
                'div[class="layout-center"] div[class="sc-LzMhO kskkfF"] div[class="sc-LzMhR ksJzSg"] div[class="sc-LzMgw ktrmiQ"]')[
                0].text
            size_num = int(size.strip("共 ").strip(" 項商品"))

            for j in range(size_num):
                name = soup.select('div[class="product-container--wrapper"] div[class="sc-fzXfPe loYluO"] div[class="sc-fzXfNR cknioF"]')[j].text
                global product_name
                product_name = name.strip(".").replace("/", "-").replace("*", "x")
                price = soup.select('div[class="product-container--wrapper"] div[class="sc-fzXfPf kNHGta"] div[class="sc-fzXfNS ckvESO"] div[class="sc-fzXfOr oATXM"]')[j].text
                product_price = int(price.strip("NT$").replace(",", ""))
                pic = soup.select('div[class="product-container--wrapper"] div[class="product-card__vertical__media-container"] figure[class="product-card__vertical__frame product-card__vertical__frame-square"] img')[j].get("src")
                product_pic = "https:" + pic
                url = soup.select('div[class="product-container--wrapper"] div[class="product-card__vertical product-card__vertical--hover"] a')[j].get("href")
                product_url = "https://shop.pxmart.com.tw" + url

                global pic_res
                pic_res = requests.get(url=product_pic)
                if category[index] in category_drink:
                    with open('./pxgo/drink/px_{}.jpg'.format(product_name), 'wb') as f:
                        f.write(pic_res.content)
                    product_info = {"Date": update_date, "Category": "drink", "Name": product_name,
                                    "Price": product_price, "URL": product_url}
                else:
                    with open('./pxgo/{}/px_{}.jpg'.format(category[index], product_name), 'wb') as f:
                        f.write(pic_res.content)
                    product_info = {"Date": update_date, "Category": category[index], "Name": product_name,
                                    "Price": product_price, "URL": product_url}

                all_info.append(product_info)
            time.sleep(10)
        self.driver.close()
        return all_info

    # 寫入CSV
    def saveCsv(self, info):
        column_name = ["Date", "Category", "Name", "Price", "URL"]
        with open("pxmart_{}.csv".format(update_date), "w", newline='', encoding='utf-8') as product_data:
            dict_writer = csv.DictWriter(product_data, fieldnames=column_name)
            dict_writer.writeheader()
            for data in info:
                dict_writer.writerow(data)


if __name__ == "__main__":
    data_date = datetime.datetime.now()
    update_date = data_date.date()

    # category_url為各商品類別代號；此處修改泡麵類別typo
    category_url = ["295", "305", "284", "307", "303", "581", "304", "582", "306", "580", "465", "320", "325", "532",
                    "727"]
    category = ["instant_noodles", "water", "cold", "tea", "coffee", "milk", "soda", "can", "vage", "powder_coffee",
                "powder_tea", "pad", "shampoo", "body_wash", "facial_cleanser"]
    category_drink = ["water", "cold", "tea", "soda", "vage", "coffee", "milk", "can", "powder_coffee", "powder_tea"]
    category_other = ["instant_noodles", "pad", "shampoo", "body_wash", "facial_cleanser"]

    pxmart = PxMart()
    pxmart.makeFolder()
    product_data = pxmart.get_content(category_url, category, category_drink)
    pxmart.saveCsv(product_data)