from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils.helpers import parse_pagination

from app.services.like_service import get_article_likes, like_article, unlike_article


like_bp = Blueprint("like_routes", __name__)


@like_bp.route("/articles/<int:article_id>/like", methods=["POST"])
@jwt_required()
def like(article_id):
    user_id = get_jwt_identity()
    response, status = like_article(article_id, user_id)
    return jsonify(response), status


@like_bp.route("/articles/<int:article_id>/like", methods=["DELETE"])
@jwt_required()
def unlike(article_id):
    user_id = get_jwt_identity()
    response, status = unlike_article(article_id, user_id)
    return jsonify(response), status


@like_bp.route("/articles/<int:article_id>/likes", methods=["GET"])
@jwt_required()
def likes(article_id):
    page, per_page, error, status = parse_pagination(request.args.get("page"), request.args.get("per_page"))
    if error:
        return jsonify(error), status

    response, status = get_article_likes(article_id, page, per_page)
    return jsonify(response), status
