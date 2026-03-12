from app.extensions import db
from app.models.article import Article
from app.models.like import Like
from app.models.user import User
from app.utils.helpers import paginate_list
from app.services.notification_service import create_notification


def like_article(article_id, user_id):
    try:
        article_id = int(article_id)
        user_id = int(user_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    article = Article.query.get(article_id)
    user = User.query.get(user_id)
    if not article or not user:
        return {"error": "Article ou utilisateur introuvable"}, 404

    if (not article.is_public) and (article.user_id != user_id):
        return {"error": "Acces refuse"}, 403

    existing_like = Like.query.filter(
        (Like.article_id == article_id) & (Like.user_id == user_id)
    ).first()
    if existing_like:
        return {"error": "Article deja like"}, 409

    like = Like(article_id=article_id, user_id=user_id)
    db.session.add(like)
    if article.user_id != user_id:
        create_notification(
            user_id=article.user_id,
            actor_id=user_id,
            event_type="article_liked",
            title="Nouvel article aime",
            message=f"{user.username} a aime votre article",
            resource_type="article",
            resource_id=article_id,
        )
    db.session.commit()

    return {"message": "article like avec succes", "like": like.to_dict()}, 201


def unlike_article(article_id, user_id):
    try:
        article_id = int(article_id)
        user_id = int(user_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    like = Like.query.filter(
        (Like.article_id == article_id) & (Like.user_id == user_id)
    ).first()
    if not like:
        return {"error": "Like introuvable"}, 404

    db.session.delete(like)
    db.session.commit()

    return {"message": "like retire avec succes"}, 200


def get_article_likes(article_id, page=1, per_page=10):
    try:
        article_id = int(article_id)
    except (TypeError, ValueError):
        return {"error": "article_id invalide"}, 400

    article = Article.query.get(article_id)
    if not article:
        return {"error": "Article introuvable"}, 404

    likes = Like.query.filter(Like.article_id == article_id).order_by(Like.id.desc()).all()
    paginated = paginate_list([like.to_dict() for like in likes], page, per_page)
    return {
        "article_id": article_id,
        "likes_count": len(likes),
        "likes": paginated["items"],
        "pagination": paginated["pagination"],
    }, 200
