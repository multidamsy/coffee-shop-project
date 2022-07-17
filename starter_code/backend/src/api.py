import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks=Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in all_drinks]
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    all_drinks=Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in all_drinks]
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    body = request.get_json()

    title = body.get('title')
    recipe = json.dumps(body['recipe'])

    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except:
        abort(422)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(id, payload):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id ==id).one_or_none()

    if not drink:
        abort(404)

    try:
        title = body['title']
        recipe = body['recipe']

        drink = Drink(title=title, recipe=recipe)
        drink.update()
        
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except:
        abort(422)


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(id, payload):

    try:
        drink = Drink.query.filter(Drink.id ==id).one_or_none()

        if not drink:
            abort(404)

        drink.delete()
        
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except:
        abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422



@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404 

@app.errorhandler(401)
def auth_error(auth_error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "token expired"
    }), 401