import json
import os
import time
from typing import Dict, List

from WeChatEnterprise.API.SendMsg import WeChatEnterprise
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Yz:
    __str_tj_qecx = "余额查询"
    __str_login = "登录"


    def __init__(self):
        options = Options()
        options.binary_location = r"C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe"
        options.add_argument("headless")
        options.add_argument("disable-gpu")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('window-size=1920,1080')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

        self.__wechat = WeChatEnterprise(os.getenv('CORP_ID'), os.getenv('CORP_SECRET'),
                                         os.getenv('AGENT_ID'), os.getenv('REDIS_HOST'))


    def __search(self, keyword: str):
        self.driver.find_element_by_css_selector("input#dwxx").send_keys(keyword)
        self.driver.find_element_by_css_selector("a.tj-seach-btn").click()
        time.sleep(1)
        tables = self.driver.find_elements_by_css_selector("table.tj-table tbody tr")
        if "没有查询到" in tables[0].text:
            content: List[str] = [tables[0].text]
        else:
            content: List[str] = [' '.join([td.text for td in table.find_elements_by_css_selector('td')[0:7]]) for table
                                  in tables]
        return content


    def crawl(self):
        self.driver.get("https://yz.chsi.com.cn/sytj/tj/qecx.html")

        if self.__str_login in self.driver.title:
            self.driver.find_element_by_css_selector("input#username").send_keys(os.getenv("YZ_USERNAME"))
            self.driver.find_element_by_css_selector("input#password").send_keys(os.getenv("YZ_PASSWORD"))
            self.driver.find_element_by_css_selector(".yz-pc-loginbtn input.yz_btn_login").click()

        if self.__str_tj_qecx in self.driver.title:

            search_button = self.driver.find_elements_by_css_selector("li[onclick]")[0]
            if "精确查询" not in search_button.text:
                raise Exception("Unknown button: %s" % search_button.text)
            search_button.click()
            with open('config/keywords.json', encoding='utf-8') as f:
                keywords: Dict = json.load(f)
                precise_keywords: Dict = keywords.get('precise')
                for precise_keyword in precise_keywords:
                    for result in self.__search(precise_keyword):
                        self.__wechat.send_text_message(content=result,
                                                        to_user='|'.join(precise_keywords.get(precise_keyword)))

            search_button = self.driver.find_elements_by_css_selector("li[onclick]")[1]
            if "模糊查询" not in search_button.text:
                raise Exception("Unknown button: %s" % search_button.text)
            search_button.click()
            with open('config/keywords.json', encoding='utf-8') as f:
                keywords: Dict = json.load(f)
                fuzzy_keywords: Dict = keywords.get('fuzzy')
                for fuzzy_keyword in fuzzy_keywords:
                    for result in self.__search(fuzzy_keyword):
                        self.__wechat.send_text_message(content=result,
                                                        to_user='|'.join(fuzzy_keywords.get(fuzzy_keyword)))

        else:
            raise Exception()

        self.driver.quit()


load_dotenv(encoding="utf-8")

yz = Yz()
yz.crawl()
