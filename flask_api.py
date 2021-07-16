from flask import Flask, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app=app)


class Hello_World(Resource):
    def get(self):
        return "get_data"

    def post(self):
        return "post_data"


api.add_resource(Hello_World, "/test")

if __name__ == "__main__":
    app.run()


