import json
import os
import re
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.shortcuts import (
    redirect,
    render,
)
from .Tableau_url.Tableau_url_forDjango import runall
from bs4 import BeautifulSoup as bs
import requests


class BrowserNotSupport(TemplateView):
    redirect_field_name = "redirect_to"
    template_name = "browser-not-support.html"


class Index(TemplateView):
    redirect_field_name = "redirect_to"
    template_name = "index.html"


class About(TemplateView):
    redirect_field_name = "redirect_to"
    template_name = "ajax/about.html"


def getTicket():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
    }
    data = {
        "username": "Coasta",
        "server": "https://bigdata.moa.gov.tw",
        "client_ip": "125.227.27.199",
        "target_site": "stattab",
        "submittable": "Get Ticket",
    }
    session = requests.Session()
    response = session.post(
        "https://bigdata.moa.gov.tw/trusted", headers=headers, data=data
    )
    soup = bs(response.text, "html.parser")
    ticket = str(soup)
    return ticket


def replaceTicket(embed_code):
    pattern = re.compile("<param name='ticket' value='(.*)'/")
    old_ticket = re.findall(pattern, embed_code)[0]
    new_ticket = getTicket()

    if new_ticket == "-1":
        print("get Tableau Server Ticket error")
        return None
    new_embed_code = embed_code.replace(old_ticket, new_ticket)
    return new_embed_code


class Tableau_base(TemplateView):
    """子類別所需的重要/共同資料，組織在父類變數"""

    # --1.讀全部嵌入碼(coa\src\dashboard\Tableau_url.json)
    file_path = os.path.join(os.path.dirname(__file__), "Tableau_url.json")
    with open(file_path, "r", encoding="utf-8") as json_file:
        wb_dict = json.loads(json_file.read())
    # --2.其他
    redirect_field_name = "redirect_to"
    # 定義每個選單按鈕對應的預設模板
    template_names = [
        "tableau1_1_1.html",
        "tableau2_1_1.html",
        "tableau3_1_1.html",
        "tableau4_1_1.html",
        "tableau5_1_1.html",
        "tableau6_1_1.html",
        "tableau7_1_1.html",
        "tableau8_1_1.html",
    ]

    @classmethod
    def reload_json(cls, request, refresh):
        """
        根據 refresh 的值，更新父類變數 wb_dict
        0: http://DNS/tableau_reloadjson/0/，手動小編輯views.py旁邊的json檔，用此網址重讀json並更新class變數
        1: http://DNS/tableau_reloadjson/1/，執行selenium全部重爬，在Tableau_url目錄裡重造Tableau_url_inner.json
        2: http://DNS/tableau_reloadjson/2/，將Tableau_url目錄裡的json更新到外面，並重讀
        """
        if refresh == "0":
            with open(cls.file_path, "r", encoding="utf-8") as json_file:
                cls.wb_dict = json.loads(json_file.read())
            #
            return HttpResponse("Tableau_url.json 重讀完畢")
        elif refresh == "1":
            try:
                runall()
                #
                return HttpResponse(
                    "Tableau_url.json 重新爬蟲完畢，確認Tableau_url目錄裡的json無誤後，refresh下2更新views.py外面的json"
                )
            except Exception as err:
                return HttpResponse("重新爬蟲失敗，Error= " + str(err))
        elif refresh == "2":
            inner_json = os.path.join(
                os.path.dirname(__file__), r"Tableau_url\Tableau_url.json"
            )
            with open(inner_json, "r", encoding="utf-8") as inner_json_file:
                with open(
                    cls.file_path, "w", encoding="utf-8"
                ) as outer_json_file:
                    inner_data = inner_json_file.read()
                    outer_json_file.write(inner_data)  # inner寫到外面json
                    cls.wb_dict = json.loads(inner_data)  # inner更新class變數
            #
            return HttpResponse(
                "將Tableau_url目錄裡的Tableau_url_inner.json更新到外面Tableau_url.json，並重讀Tableau_url.json完畢"
            )
        else:
            return HttpResponse("請確認refresh參數")

    def get_which(self, request):
        """根據網址區分不同按鈕"""
        # 子類self調用此方法，得到按了哪個選單按鈕的對應數字，1 到 8
        url = request.build_absolute_uri()
        which = int(re.search("tableau([1-8])", url).group(1))
        return which

    # 點 menu
    def get(self, request, *args, **kwargs):
        """點左側menu後的處理"""
        # 根據網址，判斷按了menu哪一按鈕
        which = self.get_which(request)
        # 從父類讀最新的wb_dict，決定出嵌入碼
        get_embed_code = [
            None,
            None,  # Tableau2 已停用
            self.wb_dict["災害損失_產物及民間設施"]["meta"]["產物及民間設施"]["embed"],
            self.wb_dict["災害損失_公共設施"]["meta"]["公共設施"]["embed"],
            self.wb_dict["災害損失_年度"]["meta"]["年度"]["embed"],
            self.wb_dict["災害損失_分布情形"]["meta"]["分布情形"]["embed"],
            None,  # Tableau7 (SSG) 已停用
            None,  # Tableau8 (豬肉進出口) 已停用
        ]

        embed_code = get_embed_code[which - 1]
        # 根據 menu 按鈕，決定模板
        template_name = self.template_names[which - 1]

        return render(request, template_name, locals())

    # post() 方法已移除，因為不需要表單切換功能


class Index(TemplateView):
    redirect_field_name = "redirect_to"
    template_name = "index.html"

    def get(self, request):
        which = request.GET.get("which") or "nothing"
        print("which=", which)
        return render(request, self.template_name, {"which": which})

# 總體/總攬
# class Tableau1(Tableau_base):  
#     """每個按鈕點選後，表單切換四種嵌入碼"""

#     @property
#     def post_embed_code(self):
#         # 從父類讀最新的 wb_dict，決定出嵌入碼
#         post_embed_code = {
#             "USDyear": self.wb_dict["貿易總覽"]["meta"]["概況"]["embed"],
#             "USDmonth": self.wb_dict["貿易總覽_月"]["meta"]["概況"]["embed"],
#             "USDaccumulation": self.wb_dict["貿易總覽_累計"]["meta"]["概況"][
#                 "embed"
#             ],
#             "NTDyear": self.wb_dict["貿易總覽(台幣)"]["meta"]["概況"]["embed"],
#             "NTDmonth": self.wb_dict["貿易總覽_月(台幣)"]["meta"]["概況"][
#                 "embed"
#             ],
#             "NTDaccumulation": self.wb_dict["貿易總覽_累計(台幣)"]["meta"][
#                 "概況"
#             ]["embed"],
#         }
#         return post_embed_code[self.dollar + self.date_range]


# class Tableau2(Tableau_base):  # 總體/進出口貿易
#     """每個按鈕點選後，表單切換四種嵌入碼"""

#     @property
#     def post_embed_code(self):
#         # 從父類讀最新的 wb_dict，決定出嵌入碼
#         post_embed_code = {
#             "USDyear": self.wb_dict["貿易總覽"]["meta"]["進出口"]["embed"],
#             "USDmonth": self.wb_dict["貿易總覽_月"]["meta"]["進出口"]["embed"],
#             "USDaccumulation": self.wb_dict["貿易總覽_累計"]["meta"]["進出口"][
#                 "embed"
#             ],
#             "NTDyear": self.wb_dict["貿易總覽(台幣)"]["meta"]["進出口"][
#                 "embed"
#             ],
#             "NTDmonth": self.wb_dict["貿易總覽_月(台幣)"]["meta"]["進出口"][
#                 "embed"
#             ],
#             "NTDaccumulation": self.wb_dict["貿易總覽_累計(台幣)"]["meta"][
#                 "進出口"
#             ]["embed"],
#         }
#         return post_embed_code[self.dollar + self.date_range]


class Tableau3(Tableau_base):  # 國家地區別/產品別
    """固定顯示一個圖表，不需要表單切換"""
    pass

# 國家地區別/製品別
class Tableau4(Tableau_base):  
    """固定顯示一個圖表，不需要表單切換"""
    pass

# 農產品別/產品別
class Tableau5(Tableau_base):  
    """固定顯示一個圖表，不需要表單切換"""
    pass

# 農產品別/製品別
class Tableau6(Tableau_base):  
    """固定顯示一個圖表，不需要表單切換"""
    pass

# SSG
# class Tableau7(Tableau_base):  
#     """每個按鈕點選後，表單切換四種嵌入碼"""

#     @property
#     def post_embed_code(self):
#         # 從父類讀最新的wb_dict，決定出嵌入碼
#         post_embed_code = {
#             "SSG": self.wb_dict["SSG"]["meta"]["SSG"]["embed"],
#         }
#         return post_embed_code["SSG"]

# 豬肉進出口
# class Tableau8(Tableau_base):  
#     """每個按鈕點選後，表單切換四種嵌入碼"""

#     @property
#     def post_embed_code(self):
#         # 從父類讀最新的 wb_dict，決定出嵌入碼
#         post_embed_code = {
#             "豬肉進出口": self.wb_dict["豬肉進出口"]["meta"]["豬肉進出口"][
#                 "embed"
#             ],
#         }
#         return post_embed_code["豬肉進出口"]
