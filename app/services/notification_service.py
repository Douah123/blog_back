from app.extensions import db
from app.models.notification import Notification
from app.models.user import User
from app.utils.helpers import paginate_list


def create_notification(user_id, event_type, title, message, actor_id=None, resource_type=None, resource_id=None):
    try:
        user_id = int(user_id)
        actor_id = int(actor_id) if actor_id is not None else None
    except (TypeError, ValueError):
        return

    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        event_type=event_type,
        title=title,
        message=message,
        resource_type=resource_type,
        resource_id=resource_id,
        is_read=False,
    )
    db.session.add(notification)


def get_notifications(current_user_id, page=1, per_page=10, unread_only=False):
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return {"error": "ID utilisateur invalide"}, 400

    user = User.query.get(current_user_id)
    if not user:
        return {"error": "Utilisateur introuvable"}, 404

    query = Notification.query.filter(Notification.user_id == current_user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)  # noqa: E712

    notifications = query.order_by(Notification.id.desc()).all()
    results = [notification.to_dict() for notification in notifications]
    return paginate_list(results, page, per_page), 200


def mark_notification_read(notification_id, current_user_id):
    try:
        notification_id = int(notification_id)
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    notification = Notification.query.filter(
        (Notification.id == notification_id) & (Notification.user_id == current_user_id)
    ).first()
    if not notification:
        return {"error": "Notification introuvable"}, 404

    if notification.is_read:
        return {"message": "Notification deja lue", "notification": notification.to_dict()}, 200

    notification.is_read = True
    notification.read_at = db.func.now()
    db.session.commit()
    return {"message": "Notification marquee comme lue", "notification": notification.to_dict()}, 200


def mark_all_notifications_read(current_user_id):
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return {"error": "ID utilisateur invalide"}, 400

    notifications = Notification.query.filter(
        (Notification.user_id == current_user_id) & (Notification.is_read == False)  # noqa: E712
    ).all()

    for notification in notifications:
        notification.is_read = True
        notification.read_at = db.func.now()

    db.session.commit()
    return {"message": "Toutes les notifications ont ete marquees comme lues"}, 200


def get_unread_notifications_count(current_user_id):
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return {"error": "ID utilisateur invalide"}, 400

    count = Notification.query.filter(
        (Notification.user_id == current_user_id) & (Notification.is_read == False)  # noqa: E712
    ).count()
    return {"unread_count": count}, 200
