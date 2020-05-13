# -*- encoding: utf-8 -*-
# @File    : mp4Book.py
# @Time    : 2020/5/12 22:05
# @Author  : 一叶星羽
# @Email   : h0670131005@gmail.com
# @Software: PyCharm

import requests
import re
from bs4 import BeautifulSoup


def searchNovel(novelInfo):
    url = "https://m.tingshubao.com/search.asp?searchword=" + novelInfo
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    }

    response = requests.get(url, headers=header)
    response.encoding = "gb2312"

    soup = BeautifulSoup(response.text)
    print(soup.prettify())


def downloadNovel(url):
    response = requests.get(url)
    response.encoding = "gb2312"
    html = response.text

    soup = BeautifulSoup(html)
    print(soup.prettify())


def getMp3Novel():
    response = requests.get("https://m.tingshubao.com/video/?2940-0-2.html")
    response.encoding = "gb2312"
    html = response.text

    novelInfos = re.findall("<script>var datas=(.*?)}</script>", html)[0].split(";")
    title = novelInfos[2].split("'")[-2].strip()
    oriCode = re.findall("datas=\(FonHen_JieMa\((.*?)\).split", html)[0].strip("'").split("*")[1:]
    data = "".join(chr(int(code)) for code in oriCode).split("&")

    urlData = data[0].split("/")
    url = (urlData[0] + '/' + urlData[1] + '/play_' + urlData[1] + '_' + urlData[2] + '.htm').strip()

    novelUrl = "https://m.tingshubao.com/player/tingchina.php?url=" + url
    print("url:", novelUrl)
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
    }

    response = requests.get(novelUrl, headers=header)
    response.encoding = "gb2312"

    mp3Url = response.json()['url']
    response = requests.get(mp3Url, headers=header)

    with open(title + ".mp3", "wb") as f:
        f.write(response.content)
    return {"title": title, "data": response.content}


if __name__ == '__main__':
    # getMp3Novel()
    searchNovel("%BE%B2%D2%B9%BC%C4%CB%BC")
    # downloadNovel("https://m.tingshubao.com/book/2940.html")
