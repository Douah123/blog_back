from app.extensions import db
from app.models.friendship import Friendship
from app.models.message import Message
from app.models.user import User
from app.utils.helpers import paginate_list
from app.services.notification_service import create_notification


def send_message(sender_id, receiver_id, content):
    try:
        sender_id = int(sender_id)
        receiver_id = int(receiver_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    content = (content or "").strip()
    if not content:
        return {"error": "content est requis"}, 400

    if sender_id == receiver_id:
        return {"error": "Vous ne pouvez pas vous envoyer un message"}, 400

    sender = User.query.get(sender_id)
    receiver = User.query.get(receiver_id)
    if not sender or not receiver:
        return {"error": "Utilisateur introuvable"}, 404

    blocked = Friendship.query.filter(
        (
            (
                (Friendship.requester_id == sender_id) & (Friendship.addressee_id == receiver_id)
            ) |
            (
                (Friendship.requester_id == receiver_id) & (Friendship.addressee_id == sender_id)
            )
        ) &
        (Friendship.status == "blocked")
    ).first()
    if blocked:
        return {"error": "Impossible d'envoyer un message: relation bloquee"}, 403

    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
    )
    db.session.add(message)
    create_notification(
        user_id=receiver_id,
        actor_id=sender_id,
        event_type="new_message",
        title="Nouveau message",
        message=f"{sender.username} vous a envoye un message",
        resource_type="message",
    )
    db.session.commit()

    return {"message": "message envoye avec succes", "data": message.to_dict()}, 201


def get_conversation(current_user_id, other_user_id, page=1, per_page=20):
    try:
        current_user_id = int(current_user_id)
        other_user_id = int(other_user_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    current_user = User.query.get(current_user_id)
    other_user = User.query.get(other_user_id)
    if not current_user or not other_user:
        return {"error": "Utilisateur introuvable"}, 404

    messages = Message.query.filter(
        (
            (Message.sender_id == current_user_id) & (Message.receiver_id == other_user_id)
        ) |
        (
            (Message.sender_id == other_user_id) & (Message.receiver_id == current_user_id)
        )
    ).order_by(Message.id.desc()).all()

    paginated = paginate_list([message.to_dict() for message in messages], page, per_page)
    paginated["items"].reverse()
    return paginated, 200


def get_my_chats(current_user_id, page=1, per_page=10):
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return {"error": "ID utilisateur invalide"}, 400

    current_user = User.query.get(current_user_id)
    if not current_user:
        return {"error": "Utilisateur introuvable"}, 404

    messages = Message.query.filter(
        (Message.sender_id == current_user_id) | (Message.receiver_id == current_user_id)
    ).order_by(Message.id.desc()).all()

    chats = {}
    for message in messages:
        other_user_id = message.receiver_id if message.sender_id == current_user_id else message.sender_id
        if other_user_id in chats:
            continue
        other_user = User.query.get(other_user_id)
        chats[other_user_id] = {
            "user_id": other_user_id,
            "username": other_user.username if other_user else None,
            "last_message": message.content,
            "last_message_at": message.created_at,
        }

    return paginate_list(list(chats.values()), page, per_page), 200
