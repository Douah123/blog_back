from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils.helpers import parse_pagination

from app.services.chat_service import get_conversation, get_my_chats, send_message


chat_bp = Blueprint("chat_routes", __name__)


@chat_bp.route("/chat/messages", methods=["POST"])
@jwt_required()
def create_message():
    data = request.get_json(silent=True) or {}
    receiver_id = data.get("receiver_id")
    content = data.get("content")
    sender_id = get_jwt_identity()

    response, status = send_message(sender_id, receiver_id, content)
    return jsonify(response), status


@chat_bp.route("/chat/conversation/<int:other_user_id>", methods=["GET"])
@jwt_required()
def conversation(other_user_id):
    current_user_id = get_jwt_identity()
    page, per_page, error, status = parse_pagination(request.args.get("page"), request.args.get("per_page"), default_per_page=20)
    if error:
        return jsonify(error), status

    response, status = get_conversation(current_user_id, other_user_id, page, per_page)
    return jsonify(response), status


@chat_bp.route("/chat/my", methods=["GET"])
@jwt_required()
def my_chats():
    current_user_id = get_jwt_identity()
    page, per_page, error, status = parse_pagination(request.args.get("page"), request.args.get("per_page"))
    if error:
        return jsonify(error), status

    response, status = get_my_chats(current_user_id, page, per_page)
    return jsonify(response), status
