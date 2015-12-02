import os
from datetime import datetime
from flask import request
from flask.ext.restful import Resource, reqparse, abort


class PictogramListAPI(Resource):
    def __init__(self, **kwargs):
        self.mongo = kwargs['smart_engine']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True,
                                   help='No task title provided', location='json')
        super(PictogramListAPI, self).__init__()

    def get(self):
        pictograms = self.mongo.db.pictograms.find()
        ret = []
        for pictogram in pictograms:
            ret.append(pictogram)
        return ret

    def post(self):
        rule = request.url_rule.rule
        rule = rule[1:len(rule) - 1]
        root = request.url_root
        args = self.reqparse.parse_args()
        pictogram = {
            "name": args['name'],
            "last_update": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }
        pictogram_id = self.mongo.db.pictograms.insert(pictogram)
        pictogram = self.mongo.db.pictograms.find_one({"_id": pictogram_id})
        pictogram["content_url"] = '%s%s/%s' % (root, rule, pictogram_id)
        return pictogram


class PictogramAPI(Resource):
    def __init__(self, **kwargs):
        self.mongo = kwargs['smart_engine']
        self.FILE_PATH = kwargs['path']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        # self.reqparse.add_argument('description', type=str, location='json')
        # self.reqparse.add_argument('done', type=bool, location='json')
        super(PictogramAPI, self).__init__()

    def get(self, id):
        ret = self.mongo.db.pictograms.find_one({"_id": id})
        if ret:
            return ret
        return abort(404)

    def put(self, id):
        file = request.files['file']
        file.filename = str(id) + '.jpg'
        image_path = os.path.join(self.FILE_PATH, file.filename)
        file.save(image_path)
        pictogram = self.mongo.db.pictograms.find_one({"_id": id})
        pictogram["last_update"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        pictogram["path"] = '/images/' + file.filename
        result = self.mongo.db.pictograms.update({"_id": id}, {"$set": pictogram}, upsert=False)
        return pictogram

    def delete(self, id):
        result = self.mongo.db.tests.delete_many({"_id": id})
        if result.deleted_count == 0:
            abort(404)
        return {"status": '200'}
