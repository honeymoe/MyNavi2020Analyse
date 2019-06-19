from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
from navi20.items import MyNavi2020_Item  # 如果报错是pyCharm对目录理解错误的原因，不影响
import pymongo
import pandas as pd
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from lxml import etree

class navi20Spider(Spider): #既然上面是from scrapy import了，这边就不是Scrapy.Spider而是直接Spider了。
    name = 'navi20'
    allowed_domains = ['mynavi.jp']

    # 用来保持登录状态，可把chrome上拷贝下来的字符串形式cookie转化成字典形式，粘贴到此处
    cookies = {}

    # 发送给服务器的http头信息，有的网站需要伪装出浏览器头进行爬取，有的则不需要
    headers = {
        # 'Connection': 'keep - alive',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }

    # 对请求的返回进行处理的配置
    meta = {
        'dont_redirect': True,  # 禁止网页重定向
        'handle_httpstatus_list': [301, 302]  # 对哪些异常返回进行处理
    }

    base_URL = r'https://job.mynavi.jp/20/pc/search/corp'
    add_oURL = r'/outline.html'
    add_eURL = r'/employment.html'
    trans = {
        'Location': '//td[@id="corpDescDtoListDescText50"]//text()',
        'Email': '//td[@id="corpDescDtoListDescText130"]//text()',
        #'Business_Area':'//div[@class="category"]/ul/li/span//text()',
        'Number_of_Employeees':'//td[@id="corpDescDtoListDescText270"]//text()',
        'Overtime_avg':'//td[@id="outlineAfterInfoListDescText640"]//text()',
        'Capital':'//td[@id="corpDescDtoListDescText260"]//text()',
        'Sales':'//td[@id="corpDescDtoListDescText300"]//text()',
        'Paid_avg':'//td[@id="outlineAfterInfoListDescText650"]//text()',
        'Name':'//div[@id="companyHead"]/div/h1//text()'
    }
    
    trans2 = {
        'Salary':'//td[@id="employTreatmentListDescText3190"]//text()',
        'Vacation':'//td[@id="employTreatmentListDescText3240"]//text()',
        'Worktime':'//td[@id="employTreatmentListDescText3270"]//text()',
        'Pickup':'//tr[@id="school"]/td//text()'
    }
    def get_all_text(self,key,selector,xpath,error='error'):
        try:
            list = selector.xpath(xpath).extract()
            list = map(str.strip, list)
            Text = ''.join(list)
        except:
            Text = 'error'
        return Text

    def open_driver():
        options = Options()
        options.add_argument('-headless')
        driver = Firefox(options=options)
        return driver

    def database(connecto,dataB):
        conn = pymongo.MongoClient(host='localhost', port=27017)
        MyNaviDB = conn[connecto]
        general = MyNaviDB[dataB]
        return general

    def start_requests(self):
        """
        这是一个重载函数，它的作用是发出第一个Request请求
        :return:
        """
        # 带着headers、cookies去请求start_urls[0],返回的response会被送到
        # 回调函数parse中
        start_URL = r"https://job.mynavi.jp/20/pc/search/query.html?HR:1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,99"
        driver=navi20Spider.open_driver()
        driver.get(start_URL)
        stop = False
        while True:
            content = driver.page_source.encode('utf-8')
            html = etree.HTML(content)
            pages = html.xpath("//li[@class='center paging quantity']/span/text()")[0]
            # print(pages)
            flags = pages.strip('()').split("/")
            print('当前位于第' + flags[0] + '页，共' + flags[1] + '页。')
            blocks = html.xpath("//div[@class='boxSearchresultEach corp label']")
            # if flags[0]==flags[1]:
            try:
                next_page = driver.find_element_by_xpath("//a[@id='lowerNextPage']")
                click = next_page.click()
            except:
                print('无法找到下一页按钮！')
                stop=True
                #break
            for block in blocks:
                ID = block.xpath("div[contains(@class,'right')]/h3/a/@href")[0].replace("/20/pc/search/corp", "").replace("/outline.html", "")
                item = MyNavi2020_Item()  # ITEM的位置需要注意！
                item['ID'] = ID  # 传入的ID
                self.Ourl = self.base_URL + ID + self.add_oURL
                yield Request(self.Ourl,
                              callback=self.outline_parse, headers=self.headers,
                              cookies=self.cookies, meta={'item': item})
            if flags[0] == flags[1] or stop==True :
                print("执行完毕！恭喜！")
                break
        driver.close()

    def outline_parse(self, response):
        selector = Selector(response)  # 创建选择器
        item = response.meta['item']  # 传入的Item
        try:
            item['Update'] = selector.xpath('//p[@id="updateDate"]/text()').extract()[0].replace("最終更新日：","")
        except:
            item['update'] = 'Unknown'
        try:
            item['Honsha'] = selector.xpath('//div[@class="place"]/dl/dd/text()').extract()[0].strip()
        except:
            item['Honsha'] = 'Unknown'
        try:
            Ryouiki = list(selector.xpath('//div[@class="category"]/ul/li/span/text()').extract())
        except:
            Ryouiki = 'error'
        item['Business_Area']=Ryouiki

        for key,value in self.trans.items():
            item[key]= self.get_all_text(key, selector, value)

        self.Eurl = self.base_URL + item['ID'] + self.add_eURL  # 我觉得是这个EUrl的位置错了！4月26日02:22:31
        yield Request(self.Eurl,
                      callback=self.employment_parse, headers=self.headers,
                      cookies=self.cookies, meta={'item': item})

    def employment_parse(self, response):
        selector = Selector(response)  # 创建选择器
        item = response.meta['item']  # 传入的Item
        for key,value in self.trans2.items():
            item[key]= self.get_all_text(key, selector, value)
        try:
            Pickup_Tags = list(selector.xpath('//tr[@id="feature"]/td/ul/li/span/text()').extract())
        except:
            Pickup_Tags = 'error'
        item['Pickup_Tags']=Pickup_Tags
        yield item
        #return item