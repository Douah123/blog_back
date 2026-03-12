from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils.helpers import parse_pagination

from app.services.comment_service import add_comment, delete_comment, get_article_comments, update_comment


comment_bp = Blueprint("comment_routes", __name__)


@comment_bp.route("/comments", methods=["POST"])
@jwt_required()
def create_comment():
    data = request.get_json(silent=True) or {}
    article_id = data.get("article_id")
    content = data.get("content")
    user_id = get_jwt_identity()

    response, status = add_comment(article_id, user_id, content)
    return jsonify(response), status


@comment_bp.route("/articles/<int:article_id>/comments", methods=["GET"])
@jwt_required()
def article_comments(article_id):
    page, per_page, error, status = parse_pagination(request.args.get("page"), request.args.get("per_page"))
    if error:
        return jsonify(error), status

    response, status = get_article_comments(article_id, page, per_page)
    return jsonify(response), status


@comment_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def remove_comment(comment_id):
    user_id = get_jwt_identity()
    response, status = delete_comment(comment_id, user_id)
    return jsonify(response), status


@comment_bp.route("/comments/<int:comment_id>", methods=["PUT"])
@jwt_required()
def edit_comment(comment_id):
    data = request.get_json(silent=True) or {}
    content = data.get("content")
    user_id = get_jwt_identity()

    response, status = update_comment(comment_id, user_id, content)
    return jsonify(response), status
