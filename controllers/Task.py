from flask.ext.restful import Resource, reqparse, abort


class TaskListAPI(Resource):
    def __init__(self, **kwargs):
        self.mongo = kwargs['smart_engine']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided', location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        tests = self.mongo.db.tests.find()
        ret = []
        for test in tests:
            ret.append(test)
        return ret

    def post(self):
        args = self.reqparse.parse_args()
        test = {
            'title': args['title']
        }
        test_id = self.mongo.db.tests.insert(test)
        return self.mongo.db.tests.find_one({"_id": test_id})


class TaskAPI(Resource):
    def __init__(self, **kwargs):
        self.mongo = kwargs['smart_engine']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        # self.reqparse.add_argument('description', type=str, location='json')
        # self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        ret = self.mongo.db.tests.find_one({"_id": id})
        if ret:
            return ret
        return abort(404)

    def put(self, id):
        args = self.reqparse.parse_args()
        result = self.mongo.db.tests.update({'_id': id}, {"$set": args}, upsert=False)
        if result['nModified'] == 0:
            abort(400)
        return {'status': '200'}

    def delete(self, id):
        result = self.mongo.db.tests.delete_many({"_id": id})
        if result.deleted_count == 0:
            abort(404)
        return {'status': '200'}
