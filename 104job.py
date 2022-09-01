import requests
from bs4 import BeautifulSoup
import time
import random
import json
import csv


url_a = "https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword=Data%20analyst&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&order=15&asc=0&page="
url_b = "&mode=s&jobsource=2018indexpoc&langFlag=0&langStatus=0&recommendJob=1&hotJob=1"

header_str = """Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7
Connection: keep-alive
Cookie: __auc=73ed55af181d0e225266170ab77; _gcl_au=1.1.1233434767.1657066891; luauid=212280991; _hjDonePolls=823010; _hjSessionUser_601941=eyJpZCI6IjczNmI4ZGM0LTQxOTctNWUxOS1iMzk5LTQ5OTc1YmZmZDIwZCIsImNyZWF0ZWQiOjE2NTcwNjY5NzI1ODksImV4aXN0aW5nIjp0cnVlfQ==; _gaexp=GAX1.3.Kf9mni78Qdi0oS-SgI41PA.19256.2; _gid=GA1.3.1811179872.1657527830; ALGO_EXP_6019=B; ALGO_EXP_12509=E; c_job_view_job_info_nabi=7j2yp%2C2016001007%2C2007001007%2C2004001010; TS016ab800=01180e452d98893b79952233e8b6883cdcbc9106d15392bdc5386ce6e49908ed9dd21be25302325e08a438e63de7ca930ee5f5e256; lup=212280991.5035849152215.5001489413863.1.4640712161167; lunp=5001489413863; __asc=24c2269e181f6165776ee4fb91c; _dc_gtm_UA-15276226-1=1; _ga=GA1.3.681381586.1657066891; _gat_UA-15276226-1=1; _ga_FJWMQR9J2K=GS1.1.1657691069.12.0.1657691074.55; _ga_W9X1GB1SVR=GS1.1.1657691069.12.0.1657691074.55; _ga_WYQPBGBV8Z=GS1.1.1657691069.12.0.1657691074.55
Host: www.104.com.tw
Referer: https://www.104.com.tw/jobs/search/?keyword=Data%20analyst&order=1&jobsource=2018indexpoc&ro=0
sec-ch-ua: ".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"""

headers = {r.split(": ")[0]: r.split(": ")[1] for r in header_str.split("\n")}

all_job_data = []

for page in range(1, 10+1):
    url = url_a + str(page) + url_b
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.select('div[id="js-job-content"] article[class="b-block--top-bord job-list-item b-clearfix js-job-item"] div[class="b-block__left"] h2[class="b-tit"] a')

    # 取得個職缺詳細內容網址
    job_url_list = []
    each_url = []
    for i in title:
        job_url = i['href'].replace('//', 'https://')
        res = requests.get(job_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        contents = soup.select_one('link[rel="alternate"]')
        job_no = contents['href'].split("jobNo=")[1]
        job_ajax = "https://www.104.com.tw/job/ajax/content/{}".format(job_no)
        job_url_list.append(job_ajax)
        job = {"職缺網址": job_url}
        each_url.append(job)

    job_data_list = []
    for i in job_url_list:
        res = requests.get(i, headers=headers)
        data = res.json()  # 動態網頁需使用json
        job_name = data['data']['header']['jobName']  # job name
        company = data['data']['header']['custName']  # company
        # address_region = data['data']['jobDetail']['addressRegion']  # 取出公司地址
        # address_detail = data['data']['jobDetail']['addressDetail']
        # address = address_region + address_detail
        jd = data['data']['jobDetail']['jobDescription']  # JD
        welfare = data['data']['welfare']['welfare']  # welfare
        contact = data['data']['contact']  # contact info
        contact.pop('suggestExam')
        contact_info = []
        for j in contact:
            if contact[j] != '' and contact[j] != []:
                contact_info.append(contact[j])

        # 若要新增公司地址，job_data中需新增地址項目
        job_data = {"職缺名稱": job_name, "公司名稱": company, "工作內容": jd, "福利": welfare, "聯絡資訊": contact_info}
        job_data_list.append(job_data)

    for url, data in zip(each_url, job_data_list):
        data.update(url)
        all_job_data.append(data)
    time.sleep(random.randint(2,4))

column_name = ["職缺名稱", "公司名稱", "工作內容", "福利", "聯絡資訊", "職缺網址"]
with open("104Job_data.csv", "w", newline='', encoding='utf-8') as job_info:
    dict_writer = csv.DictWriter(job_info, fieldnames=column_name)
    dict_writer.writeheader()
    for data in all_job_data:
        dict_writer.writerow(data)
