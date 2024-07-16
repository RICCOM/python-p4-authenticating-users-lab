#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy.orm import Session
from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            if article:
                return make_response(jsonify(article.to_dict()), 200)
            return {'message': 'Article not found'}, 404

        return {'message': 'Maximum pageview limit reached'}, 401

class Login(Resource):

    def post(self):
        username = request.json.get('username')
        if not username:
            return {'message': 'Username is required'}, 400

        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return make_response(jsonify(user.to_dict()), 200)
        return {'message': 'User not found'}, 404

class Logout(Resource):

    def delete(self):
        session.pop('user_id', None)
        return {}, 204

class CheckSession(Resource):

    def get(self):
        user_id = session.get('user_id')
        if user_id:
            with Session(db.engine) as sess:
                user = sess.get(User, user_id)
                if user:
                    return make_response(jsonify(user.to_dict()), 200)
        return {}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
