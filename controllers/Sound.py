import os
from datetime import datetime
from flask import request
from flask.ext.restful import Resource, reqparse, abort


class SoundListAPI(Resource):
    def __init__(self, **kwargs):
        self.mongo = kwargs['smart_engine']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True,
                                   help='No task title provided', location='json')
        super(SoundListAPI, self).__init__()

    def get(self):
        sounds = self.mongo.db.sounds.find()
        ret = []
        for sound in sounds:
            ret.append(sound)
        return ret

    def post(self):
        rule = request.url_rule.rule
        rule = rule[1:len(rule) - 1]
        root = request.url_root
        args = self.reqparse.parse_args()
        sound = {
            'name': args['name'],
            'last_update': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            'path': ''
        }
        sound_id = self.mongo.db.sounds.insert(sound)
        sound = self.mongo.db.sounds.find_one({"_id": sound_id})
        sound['content_url'] = '%s%s/%s' % (root, rule, sound_id)
        return sound


class SoundAPI(Resource):
    def __init__(self, **kwargs):
        self.mongo = kwargs['smart_engine']
        self.FILE_PATH = kwargs['path']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        # self.reqparse.add_argument('description', type=str, location='json')
        # self.reqparse.add_argument('done', type=bool, location='json')
        super(SoundAPI, self).__init__()

    def get(self, id):
        ret = self.mongo.db.sounds.find_one({"_id": id})
        if ret:
            return ret
        return abort(404)

    def put(self, id):
        file = request.files['file']
        file.filename = str(id) + '.mp3'
        image_path = os.path.join(self.FILE_PATH, file.filename)
        file.save(image_path)
        sound = self.mongo.db.sounds.find_one({"_id": id})
        sound['last_update'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        sound['path'] = '/sounds/' + file.filename
        result = self.mongo.db.sounds.update({'_id': id}, {"$set": sound}, upsert=False)
        return sound

    def delete(self, id):
        result = self.mongo.db.tests.delete_many({"_id": id})
        if result.deleted_count == 0:
            abort(404)
        return {'status': '200'}
