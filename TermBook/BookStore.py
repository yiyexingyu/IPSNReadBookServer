# -*- encoding: utf-8 -*-
# @File    : BookStore.py
# @Time    : 2020/5/15 19:33
# @Author  : 一叶星羽
# @Email   : h0670131005@gmail.com
# @Software: PyCharm

import sys
import os
import time

import requests
import re
from threading import Thread
from lxml import etree

import json
from json.decoder import JSONDecodeError

from eprogress import LineProgress, MultiProgressManager
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, ID3NoHeaderError


def SetMap3Info(id3Data: ID3, infoDict: dict):
    for key in infoDict.keys():
        if key == "APIC":
            id3Data[key] = APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc=u'封面',
                data=infoDict[key]
            )
        elif key == 'TIT2':
            id3Data[key] = TIT2(
                encoding=3,
                text=infoDict[key]
            )
        elif key == "TPE1":
            id3Data[key] = TPE1(
                encoding=3,
                text=infoDict[key]
            )
        elif key == "TALB":
            id3Data[key] = TALB(
                encoding=3,
                text=infoDict[key]
            )
    return id3Data


def searchMp3Novel(novelInfo):
    novelInfo = str(novelInfo.encode("gb2312")).replace("\\", "|").split("'")[1].replace("|x", "%")
    url = "https://m.tingshubao.com/search.asp?searchword=" + novelInfo

    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36", }

    response = requests.get(url, headers=header)
    response.encoding = "gb2312"

    html = etree.HTML(response.text)
    novelNum = int(html.xpath("/html/body/div[2]/div/span/em")[0].text)
    result = {"novelNum": novelNum, "novelList": []}

    if novelNum == 0:
        return result

    novelList = html.xpath("/html/body/div[2]/ul/li[@class='book-li']")
    novelInfoList = []
    for index, novelHtmlInfo in enumerate(novelList):  # type: etree._Element
        novelInfoList.append({
            "novelID": int(novelHtmlInfo.xpath("./a/@href")[0].split("/")[-1].split(".")[0]),
            "novelCover": "https://m.tingshubao.com" + novelHtmlInfo.xpath("./a/img/@data-original")[0],
            "novelTitle": novelHtmlInfo.xpath("./a/div/h4/text()")[0],
            "novelDesc": novelHtmlInfo.xpath("./a/div/p/text()")[0],
            "novelAuthor": novelHtmlInfo.xpath("./a/div/div[@class='book-meta']/text()")[0],
        })
    result["novelList"] = novelInfoList
    return result


def searchTxtNovel(novelInfo):
    txtUrl = "http://www.xbiquge.la/modules/article/waps.php?searchkey=" + novelInfo
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36", }

    response = requests.get(txtUrl, headers=header)
    response.encoding = "utf-8"

    html = etree.HTML(response.text)
    novelListHtml = html.xpath("//*[@id='checkform']/table/tr")[1:]

    result = {"novelNum": len(novelListHtml), "novelList": []}
    if len(novelListHtml) <= 0:
        return result

    novelInfoList = []
    for novel in novelListHtml:
        novelInfoList.append({
            "novelUrl": novel.xpath("./td[1]/a/@href")[0],
            "novelTitle": novel.xpath("./td[1]/a/text()")[0],
            "novelAuthor": novel.xpath("./td[3]/text()")[0]
        })
    result["novelList"] = novelInfoList
    return result


def getNovelChapterList(novelUrl):
    response = requests.get(novelUrl)
    response.encoding = "gb2312"

    html = etree.HTML(response.text)
    novelInfo = html.xpath("/html/body/div[1]/div")[0]

    result = {"novelType": novelInfo.xpath("./div/a/text()")[0]}
    statue = novelInfo.xpath("./div[3]/text()")
    result["updateStatue"] = statue[0]
    result["updateDate"] = statue[1]

    print("正在获取章节列表....")
    chapterList = []
    urlDomain = "m.tingshubao.com/"
    chapterHtmlList = html.xpath("//*[@id='playlist']/ul/li")

    for chapter in chapterHtmlList:
        tUrl = urlDomain + chapter.xpath("./a/@href")[0]
        url = "https:/"
        for v in tUrl.split("/"):
            if v: url += ("/" + v)
        chapterList.append({
            "url": url,
            "title": chapter.xpath("./a/text()")[0]
        })
    result["chapterList"] = chapterList
    return result


def downloadMp3Novel(url):
    response = requests.get(url)
    response.encoding = "gb2312"
    html = response.text
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
    }

    oriCode = re.findall("datas=\(FonHen_JieMa\((.*?)\).split", html)[0].strip("'").split("*")[1:]
    data = "".join(chr(int(code)) for code in oriCode).split("&")

    if data[2] == "tc":
        urlData = data[0].split("/")
        url = (urlData[0] + '/' + urlData[1] + '/play_' + urlData[1] + '_' + urlData[2] + '.htm').strip()
        novelUrl = "https://m.tingshubao.com/player/tingchina.php?url=" + url

        musicType = "mp3"
        response = requests.get(novelUrl, headers=header)
        response.encoding = "gb2312"

        while True:
            try:
                mp3Url = response.json()['url']
                break
            except JSONDecodeError:
                print("获取音频出现错误: ", novelUrl)
                print(response.text)
                time.sleep(2)
    else:
        mp3Url = data[0]
        musicType = "mp4"

    response = requests.get(mp3Url, headers=header)
    return musicType, response.content


def downloadTxtNovel(url, curChaptersNum=0):
    response = requests.get(url)
    response.encoding = "utf-8"

    html = etree.HTML(response.text)
    coverUrl = html.xpath("//*[@id='fmimg']/img/@src")[0]

    title = html.xpath("//*[@id='info']/h1/text()")[0]
    chaptersHtml = html.xpath("//*[@id='list']/dl/dd")
    data = """\n"""

    progress = LineProgress(total=100, title=title)
    total = len(chaptersHtml) - curChaptersNum
    for index in range(curChaptersNum, len(chaptersHtml)):
        chapter = chaptersHtml[index]
        title = chapter.xpath("./a/text()")[0].split("【")[0].split("(")[0]
        data += ("\n\n" + title + "\n\n")
        response = requests.get("http://www.xbiquge.la/" + chapter.xpath("./a/@href")[0])
        response.encoding = "utf-8"

        chapterHtml = etree.HTML(response.text)
        data += "".join(chapterHtml.xpath("//*[@id='content']/text()")).replace("\xa0", " ").replace("\r", "\n")
        progress.update(int((index - curChaptersNum + 1) / total * 100))
    return coverUrl, len(chaptersHtml), data


class INovel():

    def __init__(self):
        self.root = "../../INovel"
        self.bookshelfData = {}
        self.bookshelfPath = os.path.join(self.root, "bookshelf.txt")
        self.__loadBookshelData()

    def __loadBookshelData(self):

        with open(self.bookshelfPath, mode='a', encoding="gbk") as f:
            print(f)

        try:
            with open(self.bookshelfPath, mode='r') as file:
                self.bookshelfData = json.load(file)
        except JSONDecodeError:
            print("打开小说信息文件失败....")

    def __saveBookshelData(self):
        with open(self.bookshelfPath, "w") as file:
            json.dump(self.bookshelfData, file)

    def bookSearchRes(self, mp3NovelList: list, txtNovelList: list):
        menu = """搜索结果:"""

        i = 1
        for novel in mp3NovelList:
            menu += ("\n" + str(i) + "、" + novel["novelTitle"] + ("--%s" % novel["novelAuthor"]) + "(mp3)")
            i += 1
        for novel in txtNovelList:
            menu += ("\n" + str(i) + "、" + novel["novelTitle"] + ("--%s" % novel["novelAuthor"]) + "(txt)")
            i += 1

        menu += ("\n" + str(i) + "、" + "返回书城")
        menu += ("\n" + str(i + 1) + "、" + "返回主页")
        menu += ("\n" + str(i + 2) + "、" + "退出")

        select = INovel.showMenu(menu, range(1, i + 4))
        if 1 <= select <= len(mp3NovelList):
            return self.mp3BookDetail(mp3NovelList[select - 1])
        elif len(mp3NovelList) < select <= len(mp3NovelList) + len(txtNovelList):
            return self.txtBookDetail(txtNovelList[select - len(mp3NovelList) - 1])
        else:
            return select - i

    def txtBookDetail(self, bookInfoDict: dict):
        path = os.path.join(self.root, "txt", bookInfoDict["novelTitle"] + ".txt")

        menu = """%s--%s""" % (bookInfoDict["novelTitle"], bookInfoDict["novelAuthor"])
        menu += """
         1、下载书籍
         2、返回书城
         3、返回主页
         4、退出"""

        flag = bookInfoDict["novelTitle"] in self.bookshelfData
        while True:
            select = INovel.showMenu(menu, range(1, 5))
            if select == 1:
                if flag:
                    curChaptersNum = self.bookshelfData[bookInfoDict["novelTitle"]]["curChaptersNum"]
                else:
                    curChaptersNum = 0
                self.saveTxtNovel(path, bookInfoDict["novelUrl"], curChaptersNum, bookInfoDict["novelTitle"], flag)
            elif select == 2:
                    return 0
            elif select == 3:
                return 1
            else:
                return 2

    def mp3BookDetail(self, bookInfoDict: dict):
        def saveMp3(data, path, cover, title, author, novel):
            try:
                id3Data = ID3(data)
                id3Data.filename = path
                SetMap3Info(id3Data, {
                    "APIC": cover,
                    "TIT2": title,
                    "TPE1": author,
                    "TALB": novel
                })
                return True
            except ID3NoHeaderError as e:
                print(e)
                print("下载失败！！")
                return False

        path = os.path.join(self.root, "mp3", bookInfoDict["novelTitle"])
        menu = """%s--%s""" % (bookInfoDict["novelTitle"], bookInfoDict["novelAuthor"])
        url = "https://m.tingshubao.com/book/%s.html" % str(bookInfoDict["novelID"])

        coverData = requests.get(bookInfoDict["novelCover"]).content
        novelDetail = getNovelChapterList(url)

        chapterNum = len(novelDetail["chapterList"])
        menu += ("\n" + "共有%d集(1-%d)" % (chapterNum, chapterNum))
        flag = bookInfoDict["novelTitle"] in self.bookshelfData.keys()

        def downLoad(chapterId):
            if flag and chapterId in self.bookshelfData[bookInfoDict["novelTitle"]]["downloaded"]:
                print("第%d集已经下载了" % chapterId)
                return

            print("开始下载第%d集..." % chapterId)
            musicType, data = downloadMp3Novel(novelDetail["chapterList"][chapterId - 1]["url"])
            musicTitle = novelDetail["chapterList"][chapterId - 1]["title"]
            if musicType == "mp3" and saveMp3(data, path + "/" + musicTitle + ".mp3",
                                              coverData, musicTitle, bookInfoDict["novelAuthor"],
                                              bookInfoDict["novelTitle"]):
                print("下载第%d集完成..." % chapterId)
            elif musicType == "mp4":
                with open(path + "/" + musicTitle + ".mp3", "wb") as f:
                    f.write(data)
                print("下载第%d集完成..." % chapterId)
            self.bookshelfData[bookInfoDict["novelTitle"]]["downloaded"].append(chapterId)
            self.__saveBookshelData()

        menu += """
        1、下载谋集
        2、连续下载
        3、下载全部
        4、收藏书籍
        5、返回书城
        6、返回主页
        7、退出"""

        while True:
            select = INovel.showMenu(menu, range(1, 8))
            if not flag and 1 <= select <= 3:
                info = {"novelName": bookInfoDict["novelTitle"], "novelType": "mp3", "downloaded": []}
                self.bookshelfData[bookInfoDict["novelTitle"]] = info
            if select == 1:
                chapters = input("请选择集数(多集请用逗号分隔[如1,2,3])：")
                try:
                    chapters = chapters.split(",")
                    chaptersID = []

                    for chapter in chapters:
                        chaptersID.append(int(chapter))

                    if not os.path.exists(path):
                        print("创建文件夹：", path)
                        os.makedirs(path)

                    for chapterID in chaptersID:
                        if 1 <= chapterID <= chapterNum:
                            downLoad(chapterID)
                        else:
                            print("集数 %d 错误" % chapterID)
                    print("下载完成")
                    input("输入任意继续...")
                except ValueError as e:
                    print(e)
                    print("输入错误!!!集数应该是数字，多集间用英文逗号隔开。")
                    input("输入任意继续...")
            elif select == 2:
                chapters = input("请选择集数(多集请用-分隔[如1-100])：")
                try:
                    start, end = chapters.strip().split("-")
                    start, end = int(start), int(end)

                    if not os.path.exists(path):
                        print("创建文件夹：", path)
                        os.makedirs(path)

                    for chapterID in range(start, end + 1):
                        if 1 <= chapterID <= chapterNum:
                            downLoad(chapterID)
                        else:
                            print("集数 %d 错误" % chapterID)
                    print("下载完成")
                    input("输入任意继续...")
                except Exception as e:
                    print(e)
                    print("输入错误!!!集数应该是数字，多集间用-隔开。")
                    input("输入任意继续...")
            elif select == 3:
                if not os.path.exists(path):
                    os.makedirs(path)
                for i, chapter in enumerate(novelDetail["chapterList"]):
                    downLoad(i + 1)
            elif select == 4:
                print("收藏成功...")
                input("输入任意继续...")
            elif select == 5:
                return 0
            elif select == 6:
                return 1
            else:
                return 2

    def bookCity(self):
        bookCityText = """欢迎来到书城
        1、搜索书籍
        2、返回主页"""

        while True:
            select = INovel.showMenu(bookCityText, range(1, 3))
            if select == 1:
                bookInfo = input("搜索书籍(输入书籍名称/作者，如牧神记):")
                bookInfo = bookInfo.replace(" ", "")
                if bookInfo:
                    mp3BookSearchResDict = searchMp3Novel(bookInfo)
                    txtBookSearchResDict = searchTxtNovel(bookInfo)
                    if mp3BookSearchResDict["novelNum"] > 0 or txtBookSearchResDict["novelNum"] > 0:
                        res = self.bookSearchRes(mp3BookSearchResDict["novelList"], txtBookSearchResDict["novelList"])
                        if res == 1:
                            break
                        elif res == 2:
                            sys.exit(0)
                    else:
                        print(5 * "*", "对不起，没有任何记录", 5 * "*")
                        input("回车继续...")
            else:
                break

    def bookshelf(self):
        bookshelfText = """欢迎来到书架
        1、返回主页"""
        select = INovel.showMenu(self.bookshelf(), range(1, 2))

    def saveTxtNovel(self, path, url, curChaptersNum, title, flag=True):
        _, curChaptersNum, data = downloadTxtNovel(url, curChaptersNum)
        with open(path, "a", encoding="utf-8") as f:
            try:
                f.write(data)
                if flag:
                    self.bookshelfData[title]["curChaptersNum"] = curChaptersNum
                else:
                    self.bookshelfData[title] = {
                        'type': "txt",
                        'url': url,
                        'curChaptersNum': curChaptersNum,
                        'path': path
                    }
                self.__saveBookshelData()
            except UnicodeEncodeError as e:
                print(e.__str__())


    def updateTxtNovel(self):
        for title in self.bookshelfData.keys():
            if self.bookshelfData[title]["type"] == 'txt':
                url = self.bookshelfData[title]['url']
                curChaptersNum = self.bookshelfData[title]['curChaptersNum']
                path = self.bookshelfData[title]['path']
                self.saveTxtNovel(path, url, curChaptersNum, title, True)
                print(title, "-更新", self.bookshelfData[title]['curChaptersNum'] - curChaptersNum,"章")


    def setting(self):
        print("此功能还未开发，敬请期待！")
        input("回车继续...")

    def run(self):
        mainMenu = """欢迎来到i阅读
        1、书城
        2、书架
        3、设置
        4、更新数据
        5、退出"""
        while True:
            select = INovel.showMenu(mainMenu, range(1, 6))
            if select == 1:
                self.bookCity()
            elif select == 2:
                self.bookshelf()
            elif select == 3:
                self.setting()
            elif select == 4:
                self.updateTxtNovel()
            else:
                print("感谢使用i阅读！！")
                break

    @staticmethod
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


def fileTest():
    path = "../../fileTest"

    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':

    novel = INovel()
    novel.run()
