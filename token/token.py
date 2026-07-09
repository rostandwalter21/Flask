# ============================================================
# CONFIGURATION CSRF MANUEL - SANS FLASK-WTF
# ============================================================
# Fichier: tokenn.py
# À placer à la racine de ton projet Flask
# ============================================================

import secrets
from functools import wraps
from flask import (
    Flask, render_template, request, session, 
    abort, redirect, url_for, flash, g
)

# ============================================================
# 1. CONFIGURATION DE L'APPLICATION
# ============================================================

def configure_app(app):
    """
    Configure l'application Flask avec la protection CSRF.
    À appeler après la création de l'app.

    Exemple:
        app = Flask(__name__)
        app.secret_key = 'ta-cle-super-secrete'
        configure_app(app)
    """
    # Configuration des cookies de session (sécurité)
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,      # Empêche l'accès JS au cookie
        SESSION_COOKIE_SAMESITE='Lax',     # Protection CSRF supplémentaire
        PERMANENT_SESSION_LIFETIME=3600,   # Session expire après 1h
    )

    # Injection automatique du token dans tous les templates
    @app.context_processor
    def inject_csrf():
        return dict(csrf_token=get_csrf_token())

    print("✅ CSRF configuré avec succès")


# ============================================================
# 2. GÉNÉRATION DU TOKEN CSRF
# ============================================================

def get_csrf_token():
    """
    Génère ou récupère le token CSRF de la session.

    Returns:
        str: Le token CSRF (32 caractères aléatoires)
    """
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']


def regenerate_csrf_token():
    """
    Régénère un nouveau token CSRF (utile après login/logout).
    """
    session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']


# ============================================================
# 3. VALIDATION DU TOKEN CSRF
# ============================================================

def validate_csrf_token():
    """
    Vérifie que le token CSRF envoyé correspond à celui de la session.

    Raises:
        403: Si le token est manquant ou invalide

    Usage dans une route POST:
        @app.route('/create', methods=['POST'])
        def create():
            validate_csrf_token()
            # ... traitement
    """
    # Récupère le token du formulaire
    token_from_form = request.form.get('csrf_token')

    # Récupère le token de la session
    token_from_session = session.get('csrf_token')

    # Vérifications
    if not token_from_form:
        abort(403, description="CSRF token manquant dans le formulaire")

    if not token_from_session:
        abort(403, description="Session invalide ou expirée")

    if token_from_form != token_from_session:
        abort(403, description="CSRF token invalide")

    # Token valide ✅
    return True


# ============================================================
# 4. DÉCORATEUR PRATIQUE POUR LES ROUTES
# ============================================================

def csrf_required(f):
    """
    Décorateur qui valide automatiquement le CSRF sur les requêtes POST.

    Usage:
        @app.route('/create', methods=['GET', 'POST'])
        @csrf_required
        def create():
            if request.method == 'POST':
                # Le token est déjà validé!
                pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            validate_csrf_token()
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# 5. PROTECTION SUPPLÉMENTAIRE: REFERER CHECK
# ============================================================

def check_referer():
    """
    Vérifie que la requête vient bien de ton propre site.
    Protection additionnelle contre le CSRF.
    """
    referer = request.headers.get('Referer', '')
    host = request.host_url.rstrip('/')

    if referer and not referer.startswith(host):
        abort(403, description="Origine de la requête non valide")


# ============================================================
# 6. RATE LIMITING (ANTI-SPAM)
# ============================================================

from datetime import datetime, timedelta

# Stockage en mémoire (pour production, utiliser Redis)
_rate_limits = {}

def check_rate_limit(key, max_requests=10, window_seconds=60):
    """
    Limite le nombre de requêtes par IP/utilisateur.

    Args:
        key: Identifiant (ex: IP + route)
        max_requests: Nombre max de requêtes
        window_seconds: Fenêtre de temps en secondes

    Returns:
        bool: True si autorisé, False si limité
    """
    now = datetime.now()

    if key not in _rate_limits:
        _rate_limits[key] = []

    # Nettoie les anciennes entrées
    _rate_limits[key] = [
        t for t in _rate_limits[key] 
        if now - t < timedelta(seconds=window_seconds)
    ]

    # Vérifie la limite
    if len(_rate_limits[key]) >= max_requests:
        return False

    # Enregistre la requête
    _rate_limits[key].append(now)
    return True


def rate_limit(max_requests=10, window_seconds=60):
    """
    Décorateur pour limiter le nombre de requêtes.

    Usage:
        @app.route('/create', methods=['POST'])
        @rate_limit(max_requests=5, window_seconds=60)
        def create():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = f"{request.remote_addr}:{request.endpoint}"
            if not check_rate_limit(key, max_requests, window_seconds):
                abort(429, description="Trop de requêtes. Réessayez plus tard.")
            return f(*args, **kwargs)
        return decorated_function
    return decorator


