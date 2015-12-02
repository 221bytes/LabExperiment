import os
from datetime import datetime
from flask import request
from flask.ext.restful import Resource, reqparse, abort


class EventListAPI(Resource):
    def __init__(self, **kwargs):
        self.mongo = kwargs['smart_engine']
        self.reqparse = reqparse.RequestParser()
        # self.reqparse.add_argument("pictograms")
        # self.reqparse.add_argument("sounds")
        # self.reqparse.add_argument("geojson")

        super(EventListAPI, self).__init__()

    def get(self):
        events = self.mongo.db.events.find()
        ret = []
        for event in events:
            ret.append(event)
        return ret

    def post(self):
        test = request.get_json()
        #https://webargs.readthedocs.org/en/latest/quickstart.html
        test['sounds'] = None
        event = {
            "pictograms": test['pictograms'],
            "sounds": test['sounds'],
            "geojson": test['geojson'],
            "last_update": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }
        event_id = self.mongo.db.events.insert(event, check_keys=False)
        event = self.mongo.db.events.find_one({"_id": event_id})
        return event


class EventAPI(Resource):
    def __init__(self, **kwargs):
        self.mongo = kwargs['smart_engine']
        self.FILE_PATH = kwargs['path']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        # self.reqparse.add_argument('description', type=str, location='json')
        # self.reqparse.add_argument('done', type=bool, location='json')
        super(EventAPI, self).__init__()

    def get(self, id):
        ret = self.mongo.db.events.find_one({"_id": id})
        if ret:
            return ret
        return abort(404)

    def put(self, id):
        file = request.files['file']
        image_path = os.path.join(self.FILE_PATH, file.filename)
        file.save(image_path)
        event = self.mongo.db.events.find_one({"_id": id})
        event['last_update'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        event['path'] = './images/' + file.filename
        result = self.mongo.db.events.update({'_id': id}, {"$set": event}, upsert=False)
        return event

    def delete(self, id):
        result = self.mongo.db.tests.delete_many({"_id": id})
        if result.deleted_count == 0:
            abort(404)
        return {'status': '200'}
