# -*- encoding: utf-8 -*-
# @File    : BookStore.py
# @Time    : 2020/5/15 19:33
# @Author  : 一叶星羽
# @Email   : h0670131005@gmail.com
# @Software: PyCharm

import sys
import os

import requests
import re
from lxml import etree


def searchNovel(novelInfo):
    novelInfo = str(novelInfo.encode("gb2312")).replace("\\", "|").split("'")[1].replace("|x", "%")
    url = "https://m.tingshubao.com/search.asp?searchword=" + novelInfo
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36", }

    response = requests.get(url, headers=header)
    response.encoding = "gb2312"

    html = etree.HTML(response.text)
    novelNum = int(html.xpath("/html/body/div[2]/div/span/em")[0].text)
    result = {"novelNum": novelNum}

    if novelNum == 0:
        return result

    novelList = html.xpath("/html/body/div[2]/ul/li[@class='book-li']")
    novelInfoList = []
    for index, novelHtmlInfo in enumerate(novelList):  # type: etree._Element
        novelInfoList.append({
            "novelID": int(novelHtmlInfo.xpath("./a/@href")[0].split("/")[-1].split(".")[0]),
            "novelCover": "https:" + novelHtmlInfo.xpath("./a/img/@data-original")[0],
            "novelTitle": novelHtmlInfo.xpath("./a/div/h4/text()")[0],
            "novelDesc": novelHtmlInfo.xpath("./a/div/p/text()")[0],
            "novelAuthor": novelHtmlInfo.xpath("./a/div/div[@class='book-meta']/text()")[0],
        })
    result["novelList"] = novelInfoList
    return result


def getNovelChapterList(novelUrl):
    response = requests.get(novelUrl)
    response.encoding = "gb2312"

    html = etree.HTML(response.text)
    novelInfo = html.xpath("/html/body/div[1]/div")[0]

    result = {"novelType": novelInfo.xpath("./div/a/text()")[0]}
    # result["startRand"] = novelInfo.xpath("")/html/body/div[1]/div
    statue = novelInfo.xpath("./div[3]/text()")
    result["updateStatue"] = statue[0]
    result["updateDate"] = statue[1]

    print("正在获取章节列表....")
    chapterList = []
    urlDomain = "https://m.tingshubao.com/"
    chapterHtmlList = html.xpath("//*[@id='playlist']/ul/li")
    for chapter in chapterHtmlList:
        chapterList.append({
            "url": urlDomain + chapter.xpath("./a/@href")[0],
            "title": chapter.xpath("./a/text()")[0]
        })
    result["chapterList"] = chapterList
    return result


def downloadMp3Novel(url):
    response = requests.get(url)
    response.encoding = "gb2312"
    html = response.text

    novelInfos = re.findall("<script>var datas=(.*?)}</script>", html)[0].split(";")
    title = novelInfos[2].split("'")[-2].strip()
    oriCode = re.findall("datas=\(FonHen_JieMa\((.*?)\).split", html)[0].strip("'").split("*")[1:]
    data = "".join(chr(int(code)) for code in oriCode).split("&")

    urlData = data[0].split("/")
    url = (urlData[0] + '/' + urlData[1] + '/play_' + urlData[1] + '_' + urlData[2] + '.htm').strip()

    novelUrl = "https://m.tingshubao.com/player/tingchina.php?url=" + url
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
    }

    response = requests.get(novelUrl, headers=header)
    response.encoding = "gb2312"

    mp3Url = response.json()['url']
    response = requests.get(mp3Url, headers=header)


    return response.content



root = "../INovel"

def showMenu(menu, selectRange):
    tip = str(selectRange.start) + "-" + str(selectRange.stop - 1)

    def inputSelect():
        try:
            select = int(input("选择操作(输入%s): " % tip))
            if select in selectRange:
                return select
            else:
                print("输入错误，请输入" + tip)
                return inputSelect()
        except ValueError:
            print("输入错误，请输入" + tip)
            return inputSelect()

    print("")
    print("*" * 40)
    print(menu)
    print("*" * 40)
    return inputSelect()


def mp3BookDetail(bookInfoDict: dict):
    path = os.path.join(root, "mp3", bookInfoDict["novelTitle"])
    menu = """%s--%s""" % (bookInfoDict["novelTitle"], bookInfoDict["novelAuthor"])

    url = "https://m.tingshubao.com/book/%s.html" % str(bookInfoDict["novelID"])
    novelDetail = getNovelChapterList(url)

    chapterNum = len(novelDetail["chapterList"])
    menu += ("\n" + "共有%d集(1-%d)" % (chapterNum, chapterNum))
    menu += """
    1、下载谋集
    2、下载全部
    3、收藏书籍
    4、返回书城
    5、返回主页
    6、退出"""

    while True:
        select = showMenu(menu, range(1, 7))
        if select == 1:
            chapters = input("请选择集数(多集请用逗号分隔)：")
            try:
                chapters = chapters.split(",")
                chaptersID = []

                for chapter in chapters:
                    chaptersID.append(int(chapter))

                if not os.path.exists(path):
                    print("创建文件夹：", path)
                    os.makedirs(path)
                for chapterID in chaptersID:
                    if 1<= chapterID <= chapterNum:
                        print("开始下载第%d集..." % chapterID)
                        data = downloadMp3Novel(novelDetail["chapterList"][chapterID-1]["url"])
                        with open(path + "/" + novelDetail["chapterList"][chapterID-1]["title"] + ".mp3", "wb") as f:
                            f.write(data)
                        print("下载第%d集完成..." % chapterID)
                    else:
                        print("集数 %d 错误" % chapterID)
                print("下载完成")
                input("输入任意继续...")
            except Exception as e:
                print(e)
                print("输入错误!!!集数应该是数字，多集间用英文逗号隔开。")
                input("输入任意继续...")
        elif select == 2:
            if not os.path.exists(path):
                os.makedirs(path)
            for i, chapter in enumerate(novelDetail["chapterList"]):
                print("正在下载第%d集..." % (i + 1))
                data = downloadMp3Novel(chapter["url"])
                with open(path + "/" + chapter["title"] + ".mp3", "wb") as f:
                    f.write(data)
                print("下载第%d集完成..." % (i + 1))
        elif select == 3:
            print("收藏成功...")
            input("输入任意继续...")
        elif select == 4:
            return 0
        elif select == 5:
            return 1
        else:
            return 2



def bookSearchRes(novelList: list):
    menu = """搜索结果:"""
    i = 1
    for novel in novelList:
        menu += ("\n" + str(i) + "、" + novel["novelTitle"] + ("--%s" % novel["novelAuthor"]))
        i += 1
    menu += ("\n" + str(i) + "、" + "返回书城")
    menu += ("\n" + str(i + 1) + "、" + "返回主页")
    menu += ("\n" + str(i + 2) + "、" + "退出")

    select = showMenu(menu, range(1, i + 4))
    if 1 <= select < i:
        return mp3BookDetail(novelList[select - 1])
    else:
        return select - i


def bookCity():
    bookCityText = """欢迎来到书城
    1、搜索书籍
    2、返回主页"""

    while True:
        select = showMenu(bookCityText, range(1, 3))
        if select == 1:
            bookInfo = input("搜索书籍(输入书籍名称/作者，如牧神记):")
            bookInfo = bookInfo.replace(" ", "")
            if bookInfo:
                bookSearchResDict = searchNovel(bookInfo)
                if bookSearchResDict["novelNum"] > 0:
                    res = bookSearchRes(bookSearchResDict["novelList"])
                    if res == 1:
                        break
                    elif res == 2:
                        sys.exit(0)
                else:
                    print(5 * "*", "对不起，没有任何记录", 5 * "*")
                    input("回车继续...")
        else:
            break


def bookshelf():
    bookshelfText = """欢迎来到书架
    1、返回主页"""
    select = showMenu(bookshelf(), range(1, 2))


def setting():
    print("此功能还未开发，敬请期待！")
    input("回车继续...")


def run():
    mainMenu = """欢迎来到i阅读
    1、书城
    2、书架
    3、设置
    4、退出"""
    while True:
        select = showMenu(mainMenu, range(1, 5))
        if select == 1:
            bookCity()
        elif select == 2:
            bookshelf()
        elif select == 3:
            setting()
        else:
            print("感谢使用i阅读！！")
            break


def fileTest():
    path = "../../fileTest"

    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    # run()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(BASE_DIR)