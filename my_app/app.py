from flask import Flask, render_template, redirect, url_for
from routes.main_route import main_route
from models.pokemon_model import Pokemon
from config.database import db
from sqlalchemy import text
from flask_migrate import Migrate

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://Arsène:test123@localhost/pokemon_db"
)

# Elle désactive le suivi automatique des modifications, car on n’en a généralement pas besoin.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Clé pour utiliser la clé session
app.config["SECRET_KEY"] = "pokemon123456789"

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    try:
        db.session.execute(text("SELECT 1"))
        print("✅ Base de données connectée")
    except Exception as e:
        print("❌ Erreur de connexion :", e)
        
# with app.app_context():
#     pokemon1 = Pokemon.query.all()
#     print(pokemon1)

# Pour voir les status pour chaque route
@app.after_request
def afficher_status(response):
    print(response.status_code)
    return response

app.register_blueprint(main_route)

@app.errorhandler(404)
def page_not_found_views(error):
    print(error)
    return render_template("global/404.html"), 404
    # return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
    
app.run(debug=True)