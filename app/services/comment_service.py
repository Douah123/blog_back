from app.extensions import db
from app.models.article import Article
from app.models.comment import Comment
from app.models.user import User
from app.utils.helpers import paginate_list
from app.services.notification_service import create_notification


def add_comment(article_id, user_id, content):
    try:
        article_id = int(article_id)
        user_id = int(user_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    content = (content or "").strip()
    if not content:
        return {"error": "content est requis"}, 400

    article = Article.query.get(article_id)
    user = User.query.get(user_id)
    if not article or not user:
        return {"error": "Article ou utilisateur introuvable"}, 404

    if not article.allow_comments:
        return {"error": "Les commentaires sont desactives pour cet article"}, 403

    comment = Comment(
        content=content,
        article_id=article_id,
        user_id=user_id,
    )
    db.session.add(comment)
    if article.user_id != user_id:
        create_notification(
            user_id=article.user_id,
            actor_id=user_id,
            event_type="article_commented",
            title="Nouveau commentaire",
            message=f"{user.username} a commente votre article",
            resource_type="article",
            resource_id=article_id,
        )
    db.session.commit()

    return {"message": "commentaire ajoute avec succes", "comment": comment.to_dict()}, 201


def get_article_comments(article_id, page=1, per_page=10):
    try:
        article_id = int(article_id)
    except (TypeError, ValueError):
        return {"error": "article_id invalide"}, 400

    article = Article.query.get(article_id)
    if not article:
        return {"error": "Article introuvable"}, 404

    if not article.allow_comments:
        return {"error": "Les commentaires sont desactives pour cet article"}, 403

    comments = Comment.query.filter(Comment.article_id == article_id).order_by(Comment.id.desc()).all()
    results = [comment.to_dict() for comment in comments]
    return paginate_list(results, page, per_page), 200


def delete_comment(comment_id, user_id):
    try:
        comment_id = int(comment_id)
        user_id = int(user_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    comment = Comment.query.get(comment_id)
    if not comment:
        return {"error": "Commentaire introuvable"}, 404

    if comment.user_id != user_id:
        return {"error": "Acces refuse"}, 403

    db.session.delete(comment)
    db.session.commit()
    return {"message": "commentaire supprime avec succes"}, 200


def update_comment(comment_id, user_id, content):
    try:
        comment_id = int(comment_id)
        user_id = int(user_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    content = (content or "").strip()
    if not content:
        return {"error": "content est requis"}, 400

    comment = Comment.query.get(comment_id)
    if not comment:
        return {"error": "Commentaire introuvable"}, 404

    if comment.user_id != user_id:
        return {"error": "Acces refuse"}, 403

    article = Article.query.get(comment.article_id)
    if not article:
        return {"error": "Article introuvable"}, 404
    if not article.allow_comments:
        return {"error": "Les commentaires sont desactives pour cet article"}, 403

    comment.content = content
    db.session.commit()
    return {"message": "commentaire modifie avec succes", "comment": comment.to_dict()}, 200
