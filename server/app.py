#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
#from datetime import datetime;

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200);

@app.route('/baked_goods', methods=["GET", "POST"])
def bakedgoods():
    if (request.method == "GET"):
        bgds = [bg.to_dict() for bg in BakedGood.query.all()]
        return make_response(bgds, 200);
    elif (request.method == "POST"):
        #need to make a new item
        #need to add that item to the database
        #return the json of the item with a successful code
        bg = BakedGood();
        #print(request.form);
        for attr in request.form:
            #print(attr);
            #print(request.form.get(attr));
            setattr(bg, attr, request.form.get(attr))#there might be a bug with datetime casting here
        #print(bg);
        db.session.add(bg);
        db.session.commit();
        #print(bg.id);
        #return make_response("Error 404: NOT DONE WITH POST YET HERE!", 404);
        return make_response(bg.to_dict(), 201);
    else: return make_response("Error 500: Wrong method used here!", 500);


def getPatchDeleteMethod(item, rqst, cls, id):
    typestr = "";
    if (cls == Bakery): typestr = "Bakery";
    elif (cls == BakedGood): typestr = "BakedGood";
    else: raise Exception("invalid value found and used for the cls here!");

    if (item == None):
        return make_response(f"Error 404: {typestr} with id ({id}) not found!", 404);
    if (rqst.method == "GET"):
        return make_response(item.to_dict(), 200);
    elif (rqst.method == "PATCH"):
        #we want to take the updated information from the request and put it on the database
        #we want to update it in the database
        #we want to return the updated information to the user... with a successful code
        for attr in rqst.form:
            #print(attr);
            #print(rqst.form.get(attr));
            setattr(item, attr, rqst.form.get(attr))#there might be a bug with datetime casting here
        bdict = item.to_dict();
        db.session.add(item);
        db.session.commit();
        return make_response(bdict, 200);
    elif (rqst.method == "DELETE"):
        #remove it from the database
        #send some response to the server as some object
        #give it a successful status code like 200
        db.session.delete(item);
        db.session.commit();

        msgstr = f"{typestr} deleted.";
        response_body = {
            "delete_successful": True,
            "message": msgstr
        };

        return make_response(response_body, 200);
    else: return make_response("Error 500: Wrong method used here!", 500);

@app.route('/bakeries/<int:id>', methods=["GET", "PATCH", "DELETE"])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    return getPatchDeleteMethod(bakery, request, Bakery, id);
    
@app.route('/baked_goods/<int:id>', methods=["GET", "PATCH", "DELETE"])
def bakedgoods_by_id(id):
    bgd = BakedGood.query.filter_by(id=id).first();
    return getPatchDeleteMethod(bgd, request, BakedGood, id);

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [bg.to_dict() for bg in baked_goods_by_price];
    return make_response(baked_goods_by_price_serialized, 200);
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first();
    most_expensive_serialized = most_expensive.to_dict();
    return make_response(most_expensive_serialized, 200);

if __name__ == '__main__':
    app.run(port=5555, debug=True)