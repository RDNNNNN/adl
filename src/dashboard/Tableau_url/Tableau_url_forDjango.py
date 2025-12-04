# -*- coding: utf-8 -*-
import os
# import requests
# import pyquery
import json
import functools
import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select  # 處理下拉
from selenium.webdriver.chrome.service import Service
# __________________________________________________________________


class ChromeDriver():
    '''driver管理'''

    def __init__(self, driverpath='win'):
        '''chrome設定'''
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')  # 让Chrome在root权限下跑
        chrome_options.add_argument("--window-size=1920,1024")  # 太寬會有chrome的render報錯
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--headless')  # 不用打开图形界面
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('log-level=3')  # console的訊息不用顯示
        #
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        chrome_options.add_argument(f"user-agent={ua}")
        # ____________________________________________
        self.options = chrome_options
        self.driverpath = os.path.join(os.getcwd(), 'chromedriver.exe')

    # 進入with
    def __enter__(self):
        print("回傳driver")
        self.driver = webdriver.Chrome(self.driverpath, options=self.options)
        return self.driver

    # 離開with
    def __exit__(self, ex_type, ex_value, ex_traceback):
        self.driver.close()
        self.driver.quit()
        print("關閉driver")


def log(func):
    '''log紀錄執行'''
    @functools.wraps(func)
    def warpper(*args, **kwargs):
        print("執行開始:", func.__name__,  func.__doc__)
        st = time.perf_counter()
        func(*args, **kwargs)
        et = time.perf_counter()
        print(f"執行完畢: {et-st} 秒")
        print("==================================================")
    #
    return warpper


@log
def open_chrome(driver):
    '''開啟Chrome'''
    driver.implicitly_wait(25)
    driver.get(table_url)
    print('連結頁面: ' + table_url)


@log
def get_wbhref(driver):
    '''讀取視覺化項的連結'''
    workbooks = "div._workbookGridItem_og5pf_13"
    for _ in range(4):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, workbooks)))
    workbooks = driver.find_elements_by_css_selector(workbooks)
    for wb in workbooks:
        a = wb.find_element_by_css_selector("a._thumbnailLink_1wqq6_102")
        href = a.get_attribute("href")
        hrefs.append(href)


@log
def get_metahref(driver):
    '''抓元資料連結'''
    dic_for_trade_date = {
        '概況': 'sheet0',
        '進出口': 'sheet4',
        '進出口 (2)': '2',
        '進出口 (3)': '3',
    }
    for href in hrefs:
        driver.get(href)
        sleep(5)
        #
        h1 = "h1"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, h1)))
        h1 = driver.find_element_by_css_selector(h1).text
        wb_dict[h1] = {
            "href": href,
            "meta": {}
        }
        #

        if "國家" in h1:
            for i in range(2):
                sheet_name = f'國家別 ({i+1})' if i > 0 else '國家別'
                sheet_href = href if i == 0 else href.replace('sheet0', '2')
                wb_dict[h1]["meta"][sheet_name] = {"href": sheet_href}
        elif "貿易總覽" in h1:
            for sheet_name, sheet_href_page in dic_for_trade_date.items():
                sheet_href = href.replace('sheet0', sheet_href_page)
                wb_dict[h1]["meta"][sheet_name] = {"href": sheet_href}
        else:
            sheet_name = driver.find_element_by_css_selector('p').text
            sheet_href = href
            wb_dict[h1]["meta"][sheet_name] = {"href": sheet_href}
            # print(h2 + '_' + sheet_name)


@log
def get_embed(driver):
    '''抓嵌入連結'''
    for h1, obj in wb_dict.items():
        for sheet_name, obj_href in obj["meta"].items():
            meta_href = obj_href["href"]
            driver.get(meta_href)
            sleep(5)
            try:
                driver.find_element_by_id('onetrust-accept-btn-handler').click()
            except: pass
            print("抓嵌入連結: ", h1, sheet_name)

            try:
                # --點共享
                shareIcon = 'button._tile_tm02q_117'
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, shareIcon)))
                shareIcon = driver.find_elements_by_css_selector(shareIcon)[2]
                shareIcon.click()
                sleep(1)
                # --嵌入連結
                iframe = "iframe"
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, iframe)))
                iframe = driver.find_element_by_css_selector(iframe)
                
                driver.switch_to.frame(iframe) # 嵌入碼在iframe內
                embed_link = 'div.fbyweya > input.f12ptpmq'
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, embed_link)))
                embed_link = driver.find_element_by_css_selector(embed_link).get_attribute("value").replace('en-US', 'zh-TW').replace('taps')
                # --存入字典
                obj_href["embed"] = embed_link
            except Exception as err:
                obj_href["embed"] = "Error: 嵌入碼抓取問題"
                print(str(err))


@log
def save_json():
    '''存json'''
    # 存在views.py旁邊的Tableau_url目錄裡
    jn_path = os.path.join(os.getcwd(), jn)
    #
    with open(jn_path, 'w', encoding='utf-8') as f:
        json.dump(wb_dict, f, ensure_ascii=False, indent=4)


@log
def runall():
    '''開始執行selenium爬蟲'''
    # B.抓頁面資料
    with ChromeDriver() as driver:
        open_chrome(driver)
        get_wbhref(driver)
        get_metahref(driver)
        get_embed(driver)

    # C.存json
    save_json()


# A.init變數
table_url = "https://public.tableau.com/app/profile/coastat/vizzes#!/"
hrefs = []
wb_dict = {}
wb_dict_forweb = {}
jn = "Tableau_url.json"