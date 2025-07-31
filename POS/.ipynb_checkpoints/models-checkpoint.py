from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Restaurant(db.Model):
    id_restaurant_id = db.Column(db.Integer, primary_key=True)
    gn_restaurant_name = db.Column(db.String, nullable=False)
    ds_restaurant_address_descr = db.Column(db.String, nullable=False)

class FoodCategory(db.Model):
    id_food_category_id = db.Column(db.Integer, primary_key=True)
    gn_food_category_name = db.Column(db.String, nullable=False)
    ds_food_category_descr = db.Column(db.String)

class Food(db.Model):
    id_food_id = db.Column(db.Integer, primary_key=True)
    gn_food_name = db.Column(db.String, nullable=False)
    id_food_category_id = db.Column(db.Integer, db.ForeignKey('food_category.id_food_category_id'), nullable=False)
    nm_price_number = db.Column(db.Integer, nullable=False)
    ds_food_descr = db.Column(db.String, nullable=False)
    id_restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id_restaurant_id'), nullable=False)

    category = db.relationship('FoodCategory', backref='foods')
    restaurant = db.relationship('Restaurant', backref='foods')