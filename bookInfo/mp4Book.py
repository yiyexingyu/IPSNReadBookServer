# -*- encoding: utf-8 -*-
# @File    : mp4Book.py
# @Time    : 2020/5/12 22:05
# @Author  : 一叶星羽
# @Email   : h0670131005@gmail.com
# @Software: PyCharm

import re

from lxml import etree
import requests
from urllib import request

import urllib.request

import urllib.parse

import re

import os.path

import selenium.webdriver


# <a title="第000章" href="/down/?26-0-0.html" target="_blank">第000章</a>


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
    # print("url:", url)

    novelUrl = "https://m.tingshubao.com/player/tingchina.php?url=" + url
    header = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
    }

    response = requests.get(novelUrl, headers=header)
    response.encoding = "gb2312"

    mp3Url = response.json()['url']
    response = requests.get(mp3Url, headers=header)
    return {"title": title, "data":response.content}


if __name__ == '__main__':
    getMp3Novel()

