# -*- encoding: utf-8 -*-
# @File    : mp4Book.py
# @Time    : 2020/5/12 22:05
# @Author  : 一叶星羽
# @Email   : h0670131005@gmail.com
# @Software: PyCharm

import time
import requests
import re
from lxml import etree
from json.decoder import JSONDecodeError


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

    response = requests.get(mp3Url, headers=header)
    return response.content


if __name__ == '__main__':
    print(searchNovel("牧神记"))
    response = requests.get("https://www.tingshubao.com/pic/uploadimg/2019-9/201991717492928723.jpg")
    data = downloadMp3Novel("https://m.tingshubao.com/video/?2940-0-493.html")

