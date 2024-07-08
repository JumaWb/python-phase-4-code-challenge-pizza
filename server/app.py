#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_all_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if restaurant:
           res = restaurant.to_dict()
           pizzas = [
               {
                   "id": restaurant_pizza.id,
            "pizza": {
                "id": restaurant_pizza.pizza.id,
                "name": restaurant_pizza.pizza.name,
                "ingredients": restaurant_pizza.pizza.ingredients
            },
            "pizza_id": restaurant_pizza.pizza_id,
            "price": restaurant_pizza.price,
            "restaurant_id": restaurant_pizza.restaurant_id
               }
               for restaurant_pizza in restaurant.restaurant_pizza
           ]
           res["restaurant_pizzas"] = pizzas
           return jsonify(res)
    except:
        return jsonify({"Error": "Restaurant not found!"}), 404

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_list = [pizza.to_dict() for pizza in pizzas]
    return jsonify(pizzas_list), 200

@app.route('/pizzas/<int:id>', methods=['GET'])
def get_pizza(id):
    pizza = Pizza.query.get(id)
    if pizza:
        return jsonify(pizza.to_dict()), 200
    return jsonify({'error': 'Pizza not found'}), 404


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    try:
        # Delete associated RestaurantPizzas
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        
        db.session.delete(restaurant)
        db.session.commit()
        
        return jsonify({"Message": "Restaurant deleted successfully!"}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.session.close()

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')
    
    errors = []
    
    if not price or not isinstance(price, int):
        errors.append("validation errors")
    if not pizza_id or not isinstance(pizza_id, int):
        errors.append("Pizza ID is required and must be an integer")
    if not restaurant_id or not isinstance(restaurant_id, int):
        errors.append("Restaurant ID is required and must be an integer")
    
    if errors:
        return jsonify({"errors": errors}), 400
    
    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)
    
    if not pizza or not restaurant:
        return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404
    
    try:
        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()
        
        response = {
            "id": restaurant_pizza.id,
            "pizza": pizza.to_dict(),
            "pizza_id": pizza_id,
            "price": price,
            "restaurant": restaurant.to_dict(),
            "restaurant_id": restaurant_id
        }
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db.session.close()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
