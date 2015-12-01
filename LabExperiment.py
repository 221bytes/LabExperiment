from flask import Flask, jsonify, make_response
from flask.ext.pymongo import PyMongo
from flask.ext.restful import Api
from bson.json_util import dumps
from controllers.Pictogram import PictogramAPI, PictogramListAPI
from controllers.Task import TaskAPI, TaskListAPI
from controllers.Sound import SoundAPI, SoundListAPI

app = Flask(__name__, static_folder='images')

# Define errors http://werkzeug.pocoo.org/docs/0.10/exceptions/
errors = {
    'NotFound': {
        'message': "Page Not Found",
        'status': 404
    },
    'BadRequest': {
        'message': "The request could not be understood by the server due to malformed syntax.",
        'status': 400
    }
}

api = Api(app, errors=errors, catch_all_404s=True)

IMAGES_PATH = app.root_path + '/images/'
SOUNDS_PATH = app.root_path + '/sounds/'


@app.errorhandler(400)
def page_not_found(e):
    return jsonify({'message': "The request could not be understood by the server due to malformed syntax.",
                    'status': 400})


@api.representation('application/json')
def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp


mongo = PyMongo(app, config_prefix='MONGO')

api.add_resource(TaskListAPI, '/todo/api/v1/tasks', endpoint='tasks',
                 resource_class_kwargs={'smart_engine': mongo})

api.add_resource(TaskAPI, '/todo/api/v1/task/<ObjectId:id>', endpoint='task',
                 resource_class_kwargs={'smart_engine': mongo})

api.add_resource(SoundListAPI, '/todo/api/v1/sounds', endpoint='sounds',
                 resource_class_kwargs={'smart_engine': mongo})

api.add_resource(SoundAPI, '/todo/api/v1/sound/<ObjectId:id>', endpoint='sound',
                 resource_class_kwargs={'smart_engine': mongo, 'path': SOUNDS_PATH})

api.add_resource(PictogramListAPI, '/todo/api/v1/pictograms', endpoint='pictograms',
                 resource_class_kwargs={'smart_engine': mongo})

api.add_resource(PictogramAPI, '/todo/api/v1/pictogram/<ObjectId:id>', endpoint='pictogram',
                 resource_class_kwargs={'smart_engine': mongo, 'path': IMAGES_PATH})

if __name__ == '__main__':
    app.run(debug=True)
