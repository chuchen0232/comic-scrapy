#從中斷章節頁開始下載
from logging import error
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import os
from time import sleep
import random
from opencc import OpenCC
from myheader import headerRQ
cc = OpenCC('s2twp')

#startURL=input("請輸入漫畫章節url:")
startURL="https://www.36mh.net/manhua/xinglaideshihoubianchengleshouershaonv/399571.html"

driver = webdriver.Chrome('chromedriver.exe')
driver.get(startURL)
soup = BeautifulSoup(driver.page_source,'lxml')

#漫畫名
comicName=""
for i in soup.select("h1 a"):
    comicName+=cc.convert(i.get_text())
print(comicName)

#建立漫畫資料夾
folder_path ='./{}/'.format(comicName)
if (os.path.exists(folder_path) == False): #判斷資料夾是否存在
    os.makedirs(folder_path) #Create folder

def catchimg():
    #建立章節資料夾
    chapter_name=""
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
        r = requests.get(imgURL,headers=headerRQ())
        imgName=chapter_name+imgInfo
        with open("{}{}.jpg".format(chapter_path,imgName), "wb")as f:  # wb
            f.write(r.content)

        #檢查進度
        if imgInfo.split("-")[0][1:]==imgInfo.split("-")[1][:-1]:
            msg="這一章抓完了"
            return msg
    except:
        print("出現情況－重新抓取")
        pass

catchimg()
while True:
    driver.find_element_by_link_text("下一页(right)").click()
    #取得點擊過後的網址連結
    currenturl=driver.current_url
    driver.get(currenturl)
    soup = BeautifulSoup(driver.page_source,'lxml')

    #imgInfo=""
    msg=catchimg()
    if msg=="這一章抓完了":
        print(msg)
        #break

#關閉 broswer.close()

