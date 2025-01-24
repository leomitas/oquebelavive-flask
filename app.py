from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flasgger import Swagger, LazyString, LazyJSONEncoder
import os

app = Flask(__name__)

app.json_encoder = LazyJSONEncoder

app.config['SWAGGER'] = {
    'title': LazyString(lambda: 'API de Produtos'),
    'uiversion': 3,
    'version': LazyString(lambda: '1.0'),
    'description': LazyString(lambda: 'Uma API para gerenciar produtos')
}
swagger = Swagger(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://u3afl46d1u0mld:p4c48e12931e7c75c92a3d051622774ac7890091ea4cdd175a47682b788f6c167@ceqbglof0h8enj.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d6gq13gvfmgbli'
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
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
    """
    Página inicial
    ---
    responses:
      200:
        description: Mensagem de boas-vindas
    """
    return "Hello, World!"

@app.route('/product', methods=['POST'])
def create_product():
    """
    Cria um novo produto
    ---
    parameters:
      - in: body
        name: body
        schema:
          id: Product
          required:
            - name
            - image
            - price
            - sold
          properties:
            name:
              type: string
            description:
              type: string
            image:
              type: string
            price:
              type: number
            sold:
              type: number
            linkForSale:
              type: string
    responses:
      200:
        description: Produto criado com sucesso
      400:
        description: Campos necessários faltando
    """
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
    """
    Retorna todos os produtos
    ---
    responses:
      200:
        description: Lista de produtos
        schema:
          properties:
            products:
              type: array
              items:
                $ref: '#/definitions/Product'
    """
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
    """
    Retorna um produto específico
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Detalhes do produto
        schema:
          $ref: '#/definitions/Product'
      404:
        description: Produto não encontrado
    """
    product = Product.query.get(id)
    if product is None:
        return jsonify({'message': 'Produto não encontrado!'}), 404
    return jsonify({'name': product.name, 'description': product.description, 'image': product.image, 'price': product.price, 'sold': product.sold, 'linkForSale': product.linkForSale})

@app.route('/product/<int:id>', methods=['PATCH'])
def update_product(id):
    """
    Atualiza um produto existente
    ---
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          id: ProductUpdate
          properties:
            name:
              type: string
            description:
              type: string
            image:
              type: string
            price:
              type: number
            sold:
              type: number
            linkForSale:
              type: string
    responses:
      200:
        description: Produto atualizado com sucesso
      404:
        description: Produto não encontrado
    """
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