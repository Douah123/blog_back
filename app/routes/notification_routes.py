from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.notification_service import (
    get_notifications,
    get_unread_notifications_count,
    mark_all_notifications_read,
    mark_notification_read,
)
from app.utils.helpers import parse_pagination


notification_bp = Blueprint("notification_routes", __name__)


@notification_bp.route("/notifications", methods=["GET"])
@jwt_required()
def notifications():
    current_user_id = get_jwt_identity()
    page, per_page, error, status = parse_pagination(request.args.get("page"), request.args.get("per_page"))
    if error:
        return jsonify(error), status

    unread_only = str(request.args.get("unread_only", "")).strip().lower() in ["1", "true", "yes"]
    response, status = get_notifications(current_user_id, page, per_page, unread_only=unread_only)
    return jsonify(response), status


@notification_bp.route("/notifications/<int:notification_id>/read", methods=["PUT"])
@jwt_required()
def read_notification(notification_id):
    current_user_id = get_jwt_identity()
    response, status = mark_notification_read(notification_id, current_user_id)
    return jsonify(response), status


@notification_bp.route("/notifications/read-all", methods=["PUT"])
@jwt_required()
def read_all_notifications():
    current_user_id = get_jwt_identity()
    response, status = mark_all_notifications_read(current_user_id)
    return jsonify(response), status


@notification_bp.route("/notifications/unread-count", methods=["GET"])
@jwt_required()
def unread_count():
    current_user_id = get_jwt_identity()
    response, status = get_unread_notifications_count(current_user_id)
    return jsonify(response), status
