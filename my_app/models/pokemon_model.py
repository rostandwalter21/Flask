from datetime import datetime
from config.database import db

class Pokemon(db.Model):
    __tablename__ = "pokemons"

    # Clé primaire sert à identifier un id unique
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    # Nullable false Cela signifie que la colonne est obligatoire.
    name = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )   

    hp = db.Column(
        db.Integer,
        nullable=False
    )

    cp = db.Column(
        db.Integer,
        nullable=False
    )

    picture = db.Column(
        db.String(255),
        nullable=False
    )

    types = db.Column(
        db.String(255),
        nullable=False
    )

    created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
    )

    def __repr__(self):
        return f"<Pokemon {self.name}>"