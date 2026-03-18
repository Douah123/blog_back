from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.helpers import parse_pagination

from app.services.user_service import (
    search_users,
    send_friend_request,
    accept_friends_request,
    reject_friends_request,
    getfriends_request,
    get_friends,
    remove_friend,
    block_user,
    unblock_user,
    upload_my_avatar,
)



user_bp = Blueprint("user_routes", __name__)


@user_bp.route("/search/users", methods=["GET"])
@jwt_required()
def Search():
    username = request.args.get("username")

    if not username:
        return jsonify({"error": "username est vide"}), 400

    current_user_id = get_jwt_identity()
    page, per_page, error, status = parse_pagination(request.args.get("page"), request.args.get("per_page"))
    if error:
        return jsonify(error), status

    users = search_users(username, current_user_id, page, per_page)

    return jsonify(users), 200


@user_bp.route("/users/me/avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    current_user_id = get_jwt_identity()
    avatar_file = request.files.get("avatar")

    response, status = upload_my_avatar(current_user_id, avatar_file)

    return jsonify(response), status


@user_bp.route("/uploads/avatars/<path:filename>", methods=["GET"])
def get_avatar(filename):
    return send_from_directory(current_app.config["AVATAR_UPLOAD_FOLDER"], filename)


@user_bp.route("/friends/request", methods=["POST"])
@jwt_required()
def request_friend():
    data = request.get_json(silent=True) or {}
    addressee_id = data.get("addressee_id")

    if not addressee_id:
        return jsonify({"error": "addressee_id requis"}), 400

    requester_id = get_jwt_identity()
    response, status = send_friend_request(requester_id, addressee_id)

    return jsonify(response), status


@user_bp.route("/friends/accept", methods=["POST"])
@jwt_required()
def accept_friend():
    data = request.get_json(silent=True) or {}
    requester_id = data.get("requester_id")

    if not requester_id:
        return jsonify({"error": "requester_id requis"}), 400

    addressee_id = get_jwt_identity()
    response, status = accept_friends_request(requester_id, addressee_id)

    return jsonify(response), status

@user_bp.route("/friends/reject", methods=["POST"])
@jwt_required()
def reject_friend():
    data = request.get_json(silent=True) or {}
    requester_id = data.get("requester_id")

    if not requester_id:
        return jsonify({"error": "requester_id requis"}), 400

    addressee_id = get_jwt_identity()
    response, status = reject_friends_request(requester_id, addressee_id)

    return jsonify(response), status


@user_bp.route("/get/friends/requests", methods=["GET"])
@jwt_required()
def get_friend_request():
   
    current_user_id = get_jwt_identity()
    page, per_page, error, status = parse_pagination(request.args.get("page"), request.args.get("per_page"))
    if error:
        return jsonify(error), status

    result, status = getfriends_request(current_user_id, page, per_page)

    return jsonify(result), status

@user_bp.route("/get/friends", methods=["GET"])
@jwt_required()
def friends():
   
    current_user_id = get_jwt_identity()
    page, per_page, error, status = parse_pagination(request.args.get("page"), request.args.get("per_page"))
    if error:
        return jsonify(error), status

    result, status = get_friends(current_user_id, page, per_page)

    return jsonify(result), status


@user_bp.route("/friends/remove", methods=["POST"])
@jwt_required()
def remove():
    data = request.get_json(silent=True) or {}
    friend_id = data.get("friend_id")

    if not friend_id:
        return jsonify({"error": "friend_id requis"}), 400

    current_user_id = get_jwt_identity()
    response, status = remove_friend(current_user_id, friend_id)

    return jsonify(response), status


@user_bp.route("/friends/block", methods=["POST"])
@jwt_required()
def block():
    data = request.get_json(silent=True) or {}
    target_user_id = data.get("target_user_id")

    if not target_user_id:
        return jsonify({"error": "target_user_id requis"}), 400

    current_user_id = get_jwt_identity()
    response, status = block_user(current_user_id, target_user_id)

    return jsonify(response), status


@user_bp.route("/friends/unblock", methods=["POST"])
@jwt_required()
def unblock():
    data = request.get_json(silent=True) or {}
    target_user_id = data.get("target_user_id")

    if not target_user_id:
        return jsonify({"error": "target_user_id requis"}), 400

    current_user_id = get_jwt_identity()
    response, status = unblock_user(current_user_id, target_user_id)

    return jsonify(response), status
