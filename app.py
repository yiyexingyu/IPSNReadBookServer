# -*- encoding: utf-8 -*-
# @File    : app.py
# @Time    : 2020/3/13 23:18
# @Author  : 一叶星羽
# @Email   : h0670131005@gmail.com
# @Software: PyCharm


from flask import Flask,jsonify
from flask_restful import reqparse, Resource, Api
from bookInfo.allBookInfo import getNovelListFromBiquge

app = Flask(__name__)
app.config["JSON_AS_ASCII"]=False
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("count", type=int, required=False)

class GetNovelFromBiquge(Resource):

    def get(self):
        arg = parser.parse_args()
        if "count" in arg:
            count = arg.get("count")
        else:
            count = 0

        resData = {"count": count, "start": 0}
        resData["books"] = getNovelListFromBiquge(count)
        return jsonify(resData)

api.add_resource(GetNovelFromBiquge, "/novel/biquge/")


@app.route('/')
def hello_world():
    return '欢迎来到我的世界！！！！'


if __name__ == '__main__':
    app.run()
