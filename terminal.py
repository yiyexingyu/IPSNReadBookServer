# -*- encoding: utf-8 -*-
# @File    : terminal.py
# @Time    : 2020/5/15 23:24
# @Author  : 一叶星羽
# @Email   : h0670131005@gmail.com
# @Software: PyCharm

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "BookInfo"))

from TermBook.BookStore import INovel


if __name__ == '__main__':
    novel = INovel()
    novel.run()