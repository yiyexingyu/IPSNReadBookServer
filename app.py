from flask import Flask,jsonify
from flask_restful import reqparse, Resource, Api
from bookInfo.allBookInfo import getNovelListFromBiquge
from bookInfo.mp4Book import getMp3Novel

app = Flask(__name__)
app.config["JSON_AS_ASCII"]=False
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("type", type=int, required=False)
parser.add_argument("start", type=int, required=False)
parser.add_argument("count", type=int, required=False)


class GetNovelMp3(Resource):
    """docstring for GetNovelMp3"""

    def get(self):
        return jsonify(getMp3Novel())


class GetNovelFromBiquge(Resource):

    def get(self):
        arg = parser.parse_args()

        count = arg.get("count")
        novelType = arg.get("type")
        start = arg.get("start")

        if count is None:
            count = 0
        if novelType is None:
            novelType = -1
        if start is None:
            start = 0

        resData = {"count": count, "start": start, "type": novelType}
        resData["books"] = getNovelListFromBiquge(novelType, start, count)
        return jsonify(resData)

api.add_resource(GetNovelFromBiquge, "/novel/biquge/")
api.add_resource(GetNovelMp3, "/novel/mp3/")


@app.route('/')
def hello_world():
    return '欢迎来到我的世界！！！！'


if __name__ == '__main__':
    app.run()
