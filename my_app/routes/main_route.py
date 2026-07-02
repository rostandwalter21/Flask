from flask import Blueprint, render_template, redirect, url_for, flash
from models.pokemon_model import Pokemon
from flask import request
from config.database import db
from validators.pokemon_validators import validate_pokemon

main_route = Blueprint('main', __name__)

@main_route.route('/')
def pokemon_views():
    pokemons = Pokemon.query.all()
    return render_template('pages/index.html', nom = 'Arsene', data = pokemons)

@main_route.route('/pokemon/<int:id>')
def pokemon_details_views(id):
    pokemon_trouve = Pokemon.query.get(id)
    # ou : Pokemon.query.filter_by(id=id).first()

    if pokemon_trouve is None:
        return "Pokemon introuvable", 404

    return render_template(
        'pages/pokemon_show.html',
        pokemon=pokemon_trouve
    )

@main_route.route('/pokemon/create', methods=['GET', 'POST'])
def pokemon_create_views():
    errors = []

    if request.method == 'POST':
        errors = validate_pokemon(request.form)

        if errors:
            return render_template(
                'pages/pokemon_create.html',
                errors=errors,
                form_data=request.form
            )

        pokemon = Pokemon(
            name=request.form['name'].strip(),
            hp=int(request.form['hp']),
            cp=int(request.form['cp']),
            picture=request.form['picture'],
            types=request.form['types']
        )

        db.session.add(pokemon)
        db.session.commit()

        flash("Pokémon créé avec succès !", "success")
        return redirect(url_for('main.pokemon_views'))

    return render_template(
        'pages/pokemon_create.html',
        form_data={},
        errors=errors
    )
    
@main_route.route('/pokemon/edit/<int:id>', methods=['GET', 'POST'])
def pokemon_edit_views(id):
    pokemon = Pokemon.query.get(id)
    # ou : Pokemon.query.filter_by(id=id).first()

    if pokemon is None:
        return "Pokemon introuvable", 404

    errors = []

    if request.method == "POST":

        errors = validate_pokemon(request.form, pokemon.id)

        if errors:
            return render_template(
                "pages/pokemon_edit.html",
                pokemon=pokemon,
                form_data=request.form,
                errors=errors
            )

        pokemon.name = request.form["name"].strip()
        pokemon.hp = int(request.form["hp"])
        pokemon.cp = int(request.form["cp"])
        pokemon.picture = request.form["picture"]
        pokemon.types = request.form["types"]

        db.session.commit()

        return redirect(url_for("main.pokemon_views"))

    return render_template(
        "pages/pokemon_edit.html",
        pokemon=pokemon,
        form_data={
            "name": pokemon.name,
            "hp": pokemon.hp,
            "cp": pokemon.cp,
            "picture": pokemon.picture,
            "types": pokemon.types
        },
        errors=[]
    )
    
@main_route.route('/pokemon/delete/<int:id>', methods=['POST'])
def pokemon_delete_views(id):

    pokemon = Pokemon.query.get(id)
    # ou : Pokemon.query.filter_by(id=id).first()

    if pokemon is None:
        return "Pokemon introuvable", 404

    db.session.delete(pokemon)
    db.session.commit()

    return redirect(url_for('main.pokemon_views'))