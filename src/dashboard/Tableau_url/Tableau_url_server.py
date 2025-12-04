# -*- coding: utf-8 -*-
import os
import requests
import pyquery
import json
import functools
import re
import time
from time import sleep
from datetime import datetime
from pprint import pprint as pp
#
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


class logger():
    total = 0 

    @classmethod
    def log(cls, func):
        '''log紀錄執行'''
        @functools.wraps(func)
        def warpper(*args, **kwargs):
            print("=================================== 執行開始 ===================================")
            print('>>>', func.__name__, ':::', func.__doc__)
            st = time.perf_counter()
            val = func(*args, **kwargs)
            et = time.perf_counter()
            cls.total += et-st
            print(f"執行完畢: {et-st:.02f} 秒")
            print(f"執行累計: {cls.total:.02f} 秒")
            #
            return val
        #
        return warpper


class ChromeDriver:
    '''driver管理'''

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        #
        self.driver = webdriver.Chrome(self.driverpath, options=self.chrome_options)
        chrome_version = self.driver.capabilities['browserVersion']
        driver_version = self.driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
        print(f'瀏覽器版本 = {chrome_version}')
        print(f'driver版本 = {driver_version}')
        if chrome_version[0:2] != driver_version[0:2]:
            raise ValueError(f'driver版本({driver_version})與瀏覽器({chrome_version})不一致')

    @logger.log
    def __enter__(self):
        '''進入with，回傳self'''
        return self

    @logger.log
    def __exit__(self, ex_type, ex_value, ex_traceback):
        '''離開with，關閉driver'''
        if self.quit:
            self.driver.close()
            self.driver.quit()

    @logger.log
    def login(self):
        '''進行登入'''
        self.driver.implicitly_wait(25)
        self.driver.get(self.url['login'])
        # (1)輸入帳密
        username_selector = "input[name=username]"
        password_selector = "input[name=password]"
        WebDriverWait(self.driver, 5, 0.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, username_selector)))
        username_input = self.driver.find_element_by_css_selector(username_selector)
        password_input = self.driver.find_element_by_css_selector(password_selector)
        #
        self.driver.execute_script(f"document.querySelector('{username_selector}').value='{self.username}'")
        self.driver.execute_script(f"document.querySelector('{password_selector}').value='{self.password}'")
        # (2)直接按登入不行，要模擬人工輸入
        username_input.send_keys(Keys.LEFT)
        username_input.send_keys(Keys.SPACE)
        username_input.send_keys(Keys.BACKSPACE)
        username_input.send_keys(Keys.ENTER)
        #
        password_input.send_keys(Keys.LEFT)
        password_input.send_keys(Keys.SPACE)
        password_input.send_keys(Keys.BACKSPACE)
        password_input.send_keys(Keys.ENTER)

    @logger.log
    def get_wbhref(self):
        '''【瀏覽>預設值】，抓工作簿名稱及連結'''
        # 進入【瀏覽】
        self.driver.find_element_by_css_selector('li[data-itemvalue=explore]').click()
        # 點國家等三個資料夾
        for href in self.url['hrefs']:
            self.driver.find_element_by_css_selector(f'a[href="{href}"]').click()
            # 收集工作簿的卡片名稱及連結
            wb_cards = self.driver.find_elements_by_css_selector("div[data-tb-test-id*='workbook-']")
            for wb_card in wb_cards:
                wbName = wb_card.find_element_by_css_selector("span[data-tb-test-id=workbook-name]").text
                wbHref = wb_card.find_element_by_css_selector("a[href*='/#/site/stattab/workbooks/']").get_attribute("href")
                self.wbdata[wbName] = {'href': f'{wbHref}/views', 'meta': {}}
            # 點回瀏覽
            self.driver.find_element_by_css_selector('li[data-itemvalue=explore]').click()

    @logger.log
    def get_metahref(self):
        '''點進工作簿card，抓底下元資料的名稱及連結'''
        for wbName in self.wbdata:
            self.driver.get(self.wbdata[wbName]['href'])
            sleep(1.5)  # 不能太快!
            #
            meta_cards = self.driver.find_elements_by_css_selector("div[data-tb-test-id*='view-']")
            for meta_card in meta_cards:
                metaName = meta_card.find_element_by_css_selector("span[data-tb-test-id='view-name']").text
                metaHref = meta_card.find_element_by_css_selector("a[href*='/#/site/stattab/redirect_to_view/']").get_attribute("href")
                self.wbdata[wbName]['meta'][metaName] = {'href': f'{metaHref}'}

    @logger.log
    def get_embed(self):
        '''抓每個元資料的嵌入連結'''
        view_prefix = self.url['view_prefix']
        for wbName, wb_dict in self.wbdata.items():
            for metaName, meta_dict in wb_dict['meta'].items():
                print(f'{wbName}__{metaName}')
                self.driver.get(meta_dict['href'])
                sleep(1.5)  # 不能太快!
                embed_id = (self.driver.current_url).replace(view_prefix, '').replace('/', '&#47;').split("?:iid")[0]
                embed_id = f'''
                    <script type='text/javascript' src='https://bigdata.moa.gov.tw/javascripts/api/viz_v1.js'></script>
                    <div id='tableauPlaceholder' class='tableauPlaceholder' style='width: 1366px; height: 571px;'>
                        <object class='tableauViz' width='1366' height='571' style='display:none;'>
                            <param name='host_url' value='https%3A%2F%2Fbigdata.moa.gov.tw%2F' />
                            <param name='embed_code_version' value='3' />
                            <param name='site_root' value='&#47;t&#47;stattab' />
                            <param name='name' value='{embed_id}' />
                            <param name='tabs' value='no' />
                            <param name='toolbar' value='yes'/>
                            <param name='showAppBanner' value='false' />
                            <param name='showShareOptions' value='no'/>
                            <param name='customViews' value='no'/>
                            <param name='alerts' value='no'/>
                            <param name='ticket' value='ticket_replace_me'/>
                        </object>
                    </div>
                    <script type='text/javascript'>
                        var divElement = document.getElementById('tableauPlaceholder');
                        var vizElement = divElement.getElementsByTagName('object')[0];
                        if (divElement.offsetWidth > 800) {{
                            vizElement.style.width = '100%';
                            vizElement.style.height = (divElement.offsetWidth * 0.75) + 'px';
                        }} else if (divElement.offsetWidth > 500) {{
                            vizElement.style.width = '100%';
                            vizElement.style.height = (divElement.offsetWidth * 0.75) + 'px';
                        }} else {{
                            vizElement.style.width = '100%';
                            vizElement.style.height = '2177px';
                        }}
                    </script>
                '''
                embed_id = re.sub('\n *', '', embed_id)
                meta_dict['embed'] = embed_id

    @logger.log
    def save_json(self):
        '''wbdata存json'''
        self.wbdata['log'] = {
            '更新日期': datetime.now().strftime('%Y-%m-%d'),
            '爬蟲秒數': f"{logger.total:.02f}",
            '工作簿數量': len(self.wbdata),
        }
        pp(self.wbdata['log'], width=4)
        #
        with open(self.json, 'w', encoding='utf-8') as f:
            json.dump(self.wbdata, f, ensure_ascii=False, indent=4)


# chrome設定
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
# A.init變數
init = {
    'url': {
        'login': 'https://bigdata.moa.gov.tw/#/signin',
        'view_prefix': 'https://bigdata.moa.gov.tw/#/site/stattab/views/',
        'hrefs': [
            "/#/site/stattab/projects/19",  # 國家
            "/#/site/stattab/projects/18",  # 總體
            "/#/site/stattab/projects/20",  # 農產品別
        ]
    },
    'driverpath': "chromedriver_87.exe",
    'chrome_options': chrome_options,
    'username': 'CoaStat',
    'password': 'CS135791qaz!',
    'wbdata': {},
    'json': 'Tableau_url_server.json',
    'quit': True,
}

# B.抓頁面資料
with ChromeDriver(**init) as myDriver:
    myDriver.login()
    myDriver.get_wbhref()
    myDriver.get_metahref()
    myDriver.get_embed()
    #
    myDriver.save_json()
