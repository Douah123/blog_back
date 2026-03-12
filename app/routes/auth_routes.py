from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash
import re

from app.extensions import db
from app.models.user import User


auth_bp = Blueprint("auth_routes", __name__, url_prefix="/auth")
PASSWORD_PATTERN = re.compile(r"^[A-Z](?=.*\d)[A-Za-z\d]{7,}$")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    fullname = (data.get("fullname") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not fullname or not email or not password:
        return jsonify({"error": "username, fullname, email et password sont obligatoires"}), 400

    if not PASSWORD_PATTERN.match(password):
        return jsonify(
            {
                "error": (
                    "Mot de passe invalide: minimum 8 caracteres, commencer par une "
                    "majuscule et contenir des lettres et des chiffres"
                )
            }
        ), 400

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email) | (User.fullname == fullname)
    ).first()
    if existing_user:
        return jsonify({"error": "Utilisateur deja existant"}), 409

    user = User(
        username=username,
        fullname=fullname,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Utilisateur cree", "user": user.to_dict(), "access_token": access_token}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("email") or data.get("username") or "").strip()
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"error": "email ou username, et password sont obligatoires"}), 400

    user = User.query.filter(
        (User.email == identifier.lower()) | (User.username == identifier)
    ).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Identifiants invalides"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Connexion reussie", "access_token": access_token, "user": user.to_dict()}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Deconnexion reussie. Supprime le token cote client."}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({"user": user.to_dict()}), 200
