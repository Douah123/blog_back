from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.helpers import parse_pagination
from app.services.article_service import (
    create_article,
    get_my_articles,
    update_article,
    delete_article,
    get_articles_feed,
)

article_bp = Blueprint("article_routes", __name__)


@article_bp.route("/create/article", methods=["POST"])
@jwt_required()
def article_create():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    is_public = data.get("is_public")
    allow_comments = data.get("allow_comments")
    author_id = get_jwt_identity()

    response, status = create_article(title, content, is_public, allow_comments, author_id)

    return jsonify(response), status


@article_bp.route("/articles/me", methods=["GET"])
@jwt_required()
def my_articles():
    author_id = get_jwt_identity()
    page, per_page, error, status = parse_pagination(request.args.get("page"), request.args.get("per_page"))
    if error:
        return jsonify(error), status

    response, status = get_my_articles(author_id, page, per_page)

    return jsonify(response), status


@article_bp.route("/articles/<int:article_id>", methods=["PUT"])
@jwt_required()
def article_update(article_id):
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    content = data.get("content")
    is_public = data.get("is_public")
    allow_comments = data.get("allow_comments")
    author_id = get_jwt_identity()

    response, status = update_article(
        article_id,
        author_id,
        title=title,
        content=content,
        is_public=is_public,
        allow_comments=allow_comments,
    )

    return jsonify(response), status


@article_bp.route("/articles/<int:article_id>", methods=["DELETE"])
@jwt_required()
def article_delete(article_id):
    author_id = get_jwt_identity()
    response, status = delete_article(article_id, author_id)

    return jsonify(response), status


@article_bp.route("/articles/feed", methods=["GET"])
@jwt_required()
def article_feed():
    current_user_id = get_jwt_identity()
    page, per_page, error, status = parse_pagination(request.args.get("page"), request.args.get("per_page"))
    if error:
        return jsonify(error), status

    response, status = get_articles_feed(current_user_id, page, per_page)

    return jsonify(response), status
