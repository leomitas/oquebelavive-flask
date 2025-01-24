from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import psycopg2
from urllib.parse import urlparse, uses_netloc

app = Flask(__name__)

from flask_migrate import Migrate

migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(150), nullable=True)
    image = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    sold = db.Column(db.Float, nullable=False)
    linkForSale = db.Column(db.String(200), nullable=True)

@app.route('/', methods=['GET'])
def home():
    return "Hello, World!"

@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    if 'name' not in data or 'image' not in data or 'price' not in data or 'sold' not in data:
        abort(400, description='Faltando campos necessários')
    
    if 'linkForSale' in data:
        linkForSale = data['linkForSale']
    else:
        linkForSale = None

    new_product = Product(name=data['name'], description=data['description'], image=data['image'], price=data['price'], sold=data['sold'], linkForSale=linkForSale)
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Produto criado com sucesso!'})

@app.route('/product', methods=['GET'])
def get_products():
    products = Product.query.all()
    output = []

    for product in products:
        product_data = {}
        product_data['id'] = product.id
        product_data['name'] = product.name
        product_data['description'] = product.description
        product_data['image'] = product.image
        product_data['price'] = product.price
        product_data['sold'] = product.sold
        product_data['linkForSale'] = product.linkForSale
        output.append(product_data)

    return jsonify({'products': output})


@app.route('/product/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if product is None:
        return jsonify({'message': 'Produto não encontrado!'}), 404
    return jsonify({'name': product.name, 'description': product.description, 'image': product.image, 'price': product.price, 'sold': product.sold, 'linkForSale': product.linkForSale})

@app.route('/product/<int:id>', methods=['PATCH'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get(id)
    if product is None:
        return jsonify({'message': 'Produto não encontrado!'}), 404

    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'image' in data:
        product.image = data['image']
    if 'price' in data:
        product.price = data['price']
    if 'sold' in data:
        product.sold = data['sold']
    if 'linkForSale' in data:
        product.linkForSale = data['linkForSale']

    db.session.commit()
    return jsonify({'message': 'Produto atualizado com sucesso!'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
