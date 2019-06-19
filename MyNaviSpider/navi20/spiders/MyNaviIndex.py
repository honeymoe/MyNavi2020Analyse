from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import datetime
from lxml import etree
import pymongo

url="https://job.mynavi.jp/20/pc/search/query.html?HR:1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,99"

def open_driver():
    options = Options()
    options.add_argument('-headless')
    driver = Firefox(options=options)
    return driver

def database():
    conn = pymongo.MongoClient(host='localhost', port=27017)
    MyNaviDB = conn['MyNavi2020NEW']
    general = MyNaviDB['GeneralNEW']
    return general

def get_url(driver,url):
    while True:
        content = driver.page_source.encode('utf-8')
        html = etree.HTML(content)
        pages = html.xpath("//li[@class='center paging quantity']/span/text()")[0]
        #print(pages)
        flags = pages.strip('()').split("/")
        print('当前位于第' + flags[0] + '页，共' + flags[1] + '页。')
        yield html
        #if flags[0]==flags[1]:
        if flags[0]==flags[1]:
            print("这是最后一页！执行完毕！恭喜！")
            break
        try:
            next_page=driver.find_element_by_xpath("//a[@id='lowerNextPage']")
            click=next_page.click()
        except:
            print('无法找到下一页按钮！')
            break
    driver.close()

def spider(block):
    #selector = etree.HTML(html)
    try:
        mainURL = block.xpath("div[contains(@class,'right')]/h3/a/@href")[0]
        ID = mainURL.replace("/20/pc/search/corp", "").replace("/outline.html", "")
    except:
        mainURL = None
        ID = None
    try:
        name = block.xpath("div[contains(@class,'right')]/h3/a/text()")[0] #晚上因为查数据库发现是矢量，就修改了程序，注意调试！！
    except:
        name = None
    try:
        tags = block.xpath("div[@class='icons']/span")
        tags_done=[]
        for tag in tags:
            tags_done.append(tag.text)
            #print(tags_done)
    except:
        tags_done=None
    try:
        text= block.find("div[@class='boxArticle01']/*/div[@class='txt']")
        text_title=text.find("h4").text
        text_contents=text.find("p").text
    except:
        text_title,text_contents=None,None
    try:
        freeword=block.find("h4").text
    except:
        freeword=None
    try:
        announce=block.find("div[@class='announceBox01']")
        announce_contents=announce.find("p").text
        announce_date=announce.find("span[@class='date']").text
    except:
        announce_date,announce_contents=None,None

    data = {
        'name': name,
        'ID': ID,
        'tags': tags_done,
        'title': text_title,
        'contents': text_contents,
        'freeword': freeword,
        'announce': announce_contents,
        'announce_date': announce_date
    }
    return data

if __name__ == '__main__':
    driver=open_driver()
    driver.get(url)
    DB = database()
    s=get_url(driver, url)

    for i in range(247):
        webpage=next(s)
        target=webpage
        print(target)
        blocks = target.xpath("//div[@class='boxSearchresultEach corp label']")
        for block in blocks:
            out=spider(block)
            #print(out)
            DB.insert_one(out)