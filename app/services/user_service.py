from app.models.user import User
from app.models.friendship import Friendship
from app.extensions import db
from app.utils.helpers import paginate_list
from app.services.notification_service import create_notification

def search_users(username_query, current_user_id=None, page=1, per_page=10):
    username_query = (username_query or "").strip()
    if not username_query:
        return []

    query = User.query.filter(
        (User.username.ilike(f"%{username_query}%"))
        | (User.fullname.ilike(f"%{username_query}%"))
    )

    if current_user_id is not None:
        query = query.filter(User.id != int(current_user_id))

    users = query.order_by(User.username.asc()).all()

    results = [
        {
            "id": user.id,
            "username": user.username,
            "fullname": user.fullname,
        }
        for user in users
    ]
    return paginate_list(results, page, per_page)


def send_friend_request(requester_id, addressee_id):
    try:
        requester_id = int(requester_id)
        addressee_id = int(addressee_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    if requester_id == addressee_id:
        return {"error": "Vous ne pouvez pas vous envoyer une invitation"}, 400

    requester = User.query.get(requester_id)
    addressee = User.query.get(addressee_id)
    if not requester or not addressee:
        return {"error": "Utilisateur introuvable"}, 404

    existing = Friendship.query.filter(
        ((Friendship.requester_id == requester_id) & (Friendship.addressee_id == addressee_id))
        | ((Friendship.requester_id == addressee_id) & (Friendship.addressee_id == requester_id))
    ).first()
    if existing:
        if existing.status == "blocked":
            return {"error": "Relation bloquee"}, 403
        if existing.status == "accepted":
            return {"error": "Vous etes deja amis"}, 409
        return {"error": "Demande d'ami deja en cours"}, 409

    friendship = Friendship(
        requester_id=requester_id,
        addressee_id=addressee_id,
        status="pending",
    )
    db.session.add(friendship)
    create_notification(
        user_id=addressee_id,
        actor_id=requester_id,
        event_type="friend_request",
        title="Nouvelle demande d'ami",
        message=f"{requester.username} vous a envoye une demande d'ami",
        resource_type="friendship",
    )
    db.session.commit()

    return {"message": "Invitation envoyee", "friendship": friendship.to_dict()}, 201

def accept_friends_request(requester_id, addressee_id):

    try:
        requester_id = int(requester_id)
        addressee_id = int(addressee_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    requester = User.query.get(requester_id)
    addressee = User.query.get(addressee_id)
    if not requester or not addressee:
        return {"error": "Utilisateur introuvable"}, 404
    
    existing = Friendship.query.filter(
        (Friendship.requester_id == requester_id)
        & (Friendship.addressee_id == addressee_id)
    ).first()

    if not existing:
        return {"error": "aucune demande n'existe"}, 404

    if existing.status == "blocked":
        return {"error": "Relation bloquee"}, 403
    if existing.status == "accepted":
        return {"error": "Demande deja acceptee"}, 409

    existing.status = "accepted"
    create_notification(
        user_id=requester_id,
        actor_id=addressee_id,
        event_type="friend_request_accepted",
        title="Demande d'ami acceptee",
        message=f"{addressee.username} a accepte votre demande d'ami",
        resource_type="friendship",
        resource_id=existing.id,
    )
    db.session.commit()
    return {"message": "demande acceptee avec succes", "friendship": existing.to_dict()}, 200

def reject_friends_request(requester_id, addressee_id):

    try:
        requester_id = int(requester_id)
        addressee_id = int(addressee_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    requester = User.query.get(requester_id)
    addressee = User.query.get(addressee_id)
    if not requester or not addressee:
        return {"error": "Utilisateur introuvable"}, 404
    
    existing = Friendship.query.filter(
        (Friendship.requester_id == requester_id)
        & (Friendship.addressee_id == addressee_id)
    ).first()

    if not existing:
        return {"error": "aucune demande n'existe"}, 404

    if existing.status == "blocked":
        return {"error": "Relation bloquee"}, 403
    if existing.status == "accepted":
        return {"error": "Demande deja acceptee"}, 409
    if existing.status == "rejected":
        return {"error": "Demande deja refusee"}, 409

    existing.status = "rejected"
    db.session.commit()
    return {"message": "demande refusee avec succes", "friendship": existing.to_dict()}, 200

def getfriends_request(current_user_id, page=1, per_page=10):
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return {"error": "ID utilisateur invalide"}, 400

    user = User.query.get(current_user_id)
    if not user:
        return {"error": "Utilisateur introuvable"}, 404

    users = Friendship.query.filter(
        (Friendship.addressee_id == current_user_id) &
        (Friendship.status == "pending")
    ).all()

    results = [
        {
            "id": friendship.id,
            "username": friendship.requester.username,
            "fullname": friendship.requester.fullname
        }
        for friendship in users
    ]
    return paginate_list(results, page, per_page), 200

def get_friends(current_user_id, page=1, per_page=10):
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return {"error": "ID utilisateur invalide"}, 400

    user = User.query.get(current_user_id)
    if not user:
        return {"error": "Utilisateur introuvable"}, 404

    users = Friendship.query.filter(
        (
            (Friendship.requester_id == current_user_id) |
            (Friendship.addressee_id == current_user_id)
        ) &
        (Friendship.status == "accepted")
    ).all()

    blocked_friendships = Friendship.query.filter(
        (
            (Friendship.requester_id == current_user_id) |
            (Friendship.addressee_id == current_user_id)
        ) &
        (Friendship.status == "blocked")
    ).all()

    blocked_ids = []
    for friendship in blocked_friendships:
        if friendship.requester_id == current_user_id:
            blocked_ids.append(friendship.addressee_id)
        else:
            blocked_ids.append(friendship.requester_id)

    friends = []
    for friendship in users:
        if friendship.requester_id == current_user_id:
            friend = friendship.addressee
        else:
            friend = friendship.requester
        if friend.id in blocked_ids:
            continue
        friends.append({
                "id": friend.id,
                "username": friend.username,
                "fullname": friend.fullname
            })

    return paginate_list(friends, page, per_page), 200

def remove_friend(current_user_id, friend_id):

    try:
        current_user_id = int(current_user_id)
        friend_id = int(friend_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    if current_user_id == friend_id:
        return {"error": "Action invalide"}, 400

    current_user = User.query.get(current_user_id)
    friend = User.query.get(friend_id)
    if not current_user or not friend:
        return {"error": "Utilisateur introuvable"}, 404

    friendship = Friendship.query.filter(
        (
            (Friendship.requester_id == current_user_id) &
            (Friendship.addressee_id == friend_id)
        ) |
        (
            (Friendship.requester_id == friend_id) &
            (Friendship.addressee_id == current_user_id)
        )
    ).first()

    if not friendship:
        return {"error": "Aucune relation d'amitie trouvee"}, 404

    if friendship.status != "accepted":
        return {"error": "Vous n'etes pas amis"}, 409

    db.session.delete(friendship)
    db.session.commit()
    return {"message": "Ami supprime avec succes"}, 200


def block_user(current_user_id, target_user_id):

    try:
        current_user_id = int(current_user_id)
        target_user_id = int(target_user_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    if current_user_id == target_user_id:
        return {"error": "Vous ne pouvez pas vous bloquer vous-meme"}, 400

    current_user = User.query.get(current_user_id)
    target_user = User.query.get(target_user_id)
    if not current_user or not target_user:
        return {"error": "Utilisateur introuvable"}, 404

    friendship = Friendship.query.filter(
        (
            (Friendship.requester_id == current_user_id) &
            (Friendship.addressee_id == target_user_id)
        ) |
        (
            (Friendship.requester_id == target_user_id) &
            (Friendship.addressee_id == current_user_id)
        )
    ).first()

    if friendship:
        if friendship.status == "blocked":
            return {"error": "Utilisateur deja bloque"}, 409
        friendship.status = "blocked"
    else:
        friendship = Friendship(
            requester_id=current_user_id,
            addressee_id=target_user_id,
            status="blocked",
        )
        db.session.add(friendship)

    create_notification(
        user_id=target_user_id,
        actor_id=current_user_id,
        event_type="user_blocked",
        title="Vous avez ete bloque",
        message=f"{current_user.username} vous a bloque",
        resource_type="friendship",
        resource_id=friendship.id if friendship.id else None,
    )

    db.session.commit()
    return {"message": "Utilisateur bloque avec succes", "friendship": friendship.to_dict()}, 200
