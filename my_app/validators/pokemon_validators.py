from models.pokemon_model import Pokemon

def validate_pokemon(form, pokemon_id=None):
    errors = []

    name = form.get("name", "").strip()
    hp = form.get("hp", "")
    cp = form.get("cp", "")
    picture = form.get("picture", "")
    types = form.get("types", "")

    if not all([name, hp, cp, picture, types]):
        errors.append("Tous les champs sont requis.")

    if len(name) < 3:
        errors.append("Le nom doit être au minimum de 3 caractères.")

    if len(name) > 25:
        errors.append("Le nom doit être au maximum de 25 caractères.")

    if not hp.isdigit() or int(hp) < 0:
        errors.append("L'HP doit être un nombre positif.")

    if not cp.isdigit() or int(cp) < 0:
        errors.append("Le CP doit être un nombre positif.")
        
    pokemon = Pokemon.query.filter_by(name=name).first()

    if pokemon and pokemon.id != pokemon_id:
        errors.append("Un Pokémon avec ce nom existe déjà.")

    return errors