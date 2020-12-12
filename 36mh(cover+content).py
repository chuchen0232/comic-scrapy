#從封面到全部的章節
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import os
from time import sleep
from opencc import OpenCC
import myheader
cc = OpenCC('s2twp')

#cover_url=input("請輸入漫畫封面url:")
cover_url="https://www.36mh.net/manhua/xinglaideshihoubianchengleshouershaonv/"

user_agent=myheader.headerRnd()
opt = webdriver.ChromeOptions()
opt.add_argument('--user-agent=%s' % user_agent)
driver = webdriver.Chrome('chromedriver.exe',options=opt)#
driver.get(cover_url)
soup = BeautifulSoup(driver.page_source,'lxml')

#漫畫名
comic_name=soup.select("h1 span")
comicName=[cc.convert(i.get_text()) for i in comic_name][0]
print(comicName)
#建立漫畫資料夾
folder_path ='./{}/'.format(comicName)
if (os.path.exists(folder_path) == False): #判斷資料夾是否存在
    os.makedirs(folder_path) #Create folder

with open(folder_path+comicName+"-簡介.txt", 'w+',encoding="utf-8") as f:
    #漫畫資訊
    book_detail=soup.select(".detail-list.cf li")
    #print(book_detail)
    bookDetail=[cc.convert(i.get_text()).replace("                                ","") for i in book_detail]
    #print(bookDetail)
    for i in bookDetail:
        f.write(i)
    #簡介
    #driver.find_elements_by_id("#intro-act").click()
    js = """
        elements = document.getElementsByClassName('none');
        for (var i=0; i < elements.length; i++)
        {
            elements[i].style.display='block'
        }
        """
    driver.execute_script(js)
    #driver.find_element_by_link_text("展开详情").click()##########error often
    book_intro=soup.select("#intro-all p")
    bookIntro=[cc.convert(i.get_text()) for i in book_intro][0].lstrip()
    f.write(bookIntro)

#漫畫cover
cover_img=soup.select(".cover .pic")
coverURL=[i.get("src") for i in cover_img][0]
#download使用request，修改header
header = {'user-agent':"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"}
r = requests.get(coverURL,headers=myheader.headerRQ())
with open("{}cover.jpg".format(folder_path), "wb")as f:  # wb二進位
    f.write(r.content)
print("封面與簡介工作完成!!!")

cha=soup.select("#chapter-list-4 li a")
links=[i.get('href') for i in cha]

def catchimg():
    #建立章節資料夾
    chapter_name="{}.".format(str(number))
    for i in soup.select("h2"):
        chapter_name+=cc.convert(i.get_text())
    print(chapter_name)
    chapter_path=folder_path+"{}/".format(chapter_name)
    if (os.path.exists(chapter_path) == False): #判斷資料夾是否存在
        os.makedirs(chapter_path) #Create folder
    ##睡一下
    #sleep(random.randint(5,10))
    try:
        ##分析圖片網址
        spImg=soup.select("#images img")
        imgURL=[i.get("src") for i in spImg][0]#str(spImg[0]).split("src=\"")[1].split("\"")[0]
        print(imgURL)

        ##分析圖片名稱
        imgInfo=""
        for i in soup.find_all("p",{"class":"img_info"}):
            imgInfo+=cc.convert(i.get_text()).replace("/","-")
        print(imgInfo)
        #download
        r = requests.get(imgURL)
        imgName=chapter_name+imgInfo
        with open("{}{}.jpg".format(chapter_path,imgName), "wb")as f:  #wb代表二進位
            f.write(r.content)
        #檢查進度
        if imgInfo.split("-")[0][1:]==imgInfo.split("-")[1][:-1]:
            msg="這一章抓完了"
            return msg
    except:
        print("圖片分析出現情況－正在重新讀取")
        pass


for i in links[0:10]:#這裡可以控制抓取章節的起訖點
    number=links.index(i)+1
    targetURL="https://www.36mh.net"+i
    driver.get(targetURL)
    soup = BeautifulSoup(driver.page_source,'lxml')
        
    catchimg()
    while True:
        try:
            driver.find_element_by_link_text("下一页(right)").click()
            #取得點擊過後的網址連結
            currenturl=driver.current_url
            driver.get(currenturl)
            soup = BeautifulSoup(driver.page_source,'lxml')

            msg=catchimg()
            if msg=="這一章抓完了":
                print(msg)
                break
        except:
            print("下一頁出現情況－正在左轉")
            pass


driver.close()    
print("任務結束")
