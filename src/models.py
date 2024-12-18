from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    favorites_planets = db.relationship('FavoritesPlanets', backref='user', lazy=True)
    favorites_people = db.relationship('FavoritesPeople', backref='user', lazy=True)

    def __repr__(self):
        return '<user %r>' % self.name

    def serialize_User(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }


class Planet(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    climate = db.Column(db.String(120), nullable=True)
    population = db.Column(db.Integer, nullable=True)

    favorite_planets = db.relationship('FavoritesPlanets', back_populates='planet', lazy=True)

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize_Planet(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population,
        }


class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(120), nullable=True)
    hometown = db.Column(db.String(20), nullable=True)

    favorite_people = db.relationship('FavoritesPeople', back_populates='people', lazy=True)

    def __repr__(self):
        return '<People %r>' % self.name

    def serialize_People(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "hometown": self.hometown,
        }


class FavoritesPlanets(db.Model):
    __tablename__ = 'favorites_planets'
    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    planet = db.relationship('Planet', back_populates='favorite_planets')
    
    def __repr__(self):
        return '<Favorites_planets %r>' % self.id

    def serialize_FavoritePlanets(self):
        return {
            "id": self.id,
            "planet_id": self.planet_id,
            "user_id": self.user_id,
        }


class FavoritesPeople(db.Model):
    __tablename__ = 'favorites_people'
    id = db.Column(db.Integer, primary_key=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    people = db.relationship('People', back_populates='favorite_people')

    def __repr__(self):
        return '<Favorites_people %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "people_id": self.people_id,
            "user_id": self.user_id,
        }
