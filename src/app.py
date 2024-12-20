"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, FavoritesPlanets, FavoritesPeople
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize_User() for user in users]), 200

@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    return jsonify([person.serialize_People() for person in people]), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize_Planet() for planet in planets]), 200

@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({"message": "User id not found"}), 404
    user = user.serialize_User()
    return jsonify(user), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"message": "Person id not found"}), 404
    return jsonify(person.serialize_People()), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"message": "Planet id not found"}), 404
    return jsonify(planet.serialize_Planet()), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    data = request.get_json()
    user_id = data.get('user_id')

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    favorites = {
        "favorite_planets": [{"id": fav.planet_id, "name": fav.planet.name} for fav in user.favorites_planets],
        "favorite_people": [{"id": fav.people_id, "name": fav.people.name} for fav in user.favorites_people]
    }

    return jsonify(favorites), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    favorite = FavoritesPlanets(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite planet added"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    data = request.get_json()
    user_id = data.get('user_id')

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    favorite = FavoritesPeople(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite person added"}), 201

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()

    name = data.get('name')
    climate = data.get('climate')
    population = data.get('population')

    if not name or not climate or not population:
        return jsonify({"error": "Missing fields"}), 400

    new_planet = Planet(name=name, climate=climate, population=population)

    db.session.add(new_planet)
    db.session.commit()

    return jsonify({"message": "Planet created", "id": new_planet.id}), 200

@app.route('/people', methods=['POST'])
def create_person():

    data = request.get_json()

    name = data.get('name')
    description = data.get('description')
    hometown = data.get('hometown')

    if not name or not description or not hometown:
        return jsonify({"error": "Missing required fields"}), 400

    new_person = People(name=name, description=description, hometown=hometown)

    db.session.add(new_person)
    db.session.commit()

    return jsonify({"message": "Person created", "id": new_person.id}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    data = request.get_json()
    user_id = data.get('user_id')

    favorite = FavoritesPeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({"error": "Favorite person not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite person deleted"}), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = People.query.get(people_id)

    if person is None:
        return jsonify({"error": "Person id not found"}), 404

    db.session.delete(person)
    db.session.commit()

    return jsonify({"message": "Person deleted"}), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')

    favorite = FavoritesPlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Favorite planet not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite planet deleted"}), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"error": "Planet id not found"}), 404

    db.session.delete(planet)
    db.session.commit()

    return jsonify({"message": "Planet deleted"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
