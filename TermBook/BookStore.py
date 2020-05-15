# -*- encoding: utf-8 -*-
# @File    : BookStore.py
# @Time    : 2020/5/15 19:33
# @Author  : 一叶星羽
# @Email   : h0670131005@gmail.com
# @Software: PyCharm

import sys
import os
from BookInfo.mp4Book import searchNovel, getNovelChapterList, downloadMp3Novel


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
    print("下载路径：", path)
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
        select = showMenu(menu, range(1, 6))
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
                        data = downloadMp3Novel(novelDetail["chapterList"][chapterID-1]["url"])
                        with open(path + "/" + novelDetail["chapterList"][chapterID-1]["title"], "wb") as f:
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
    fileTest()