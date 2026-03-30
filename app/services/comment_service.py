from app.extensions import db
from app.models.article import Article
from app.models.comment import Comment
from app.models.user import User
from app.utils.helpers import paginate_list
from app.services.notification_service import create_notification


def _build_comment_tree(comments):
    comment_map = {}
    root_comments = []

    for comment in comments:
        payload = comment.to_dict(include_replies=False)
        payload["replies"] = []
        comment_map[comment.id] = payload

    for comment in comments:
        payload = comment_map[comment.id]
        if comment.parent_comment_id and comment.parent_comment_id in comment_map:
            comment_map[comment.parent_comment_id]["replies"].append(payload)
        else:
            root_comments.append(payload)

    return root_comments


def add_comment(article_id, user_id, content, parent_comment_id=None):
    try:
        article_id = int(article_id)
        user_id = int(user_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    try:
        parent_comment_id = int(parent_comment_id) if parent_comment_id is not None else None
    except (TypeError, ValueError):
        return {"error": "parent_comment_id invalide"}, 400

    content = (content or "").strip()
    if not content:
        return {"error": "content est requis"}, 400

    article = Article.query.get(article_id)
    user = User.query.get(user_id)
    if not article or not user:
        return {"error": "Article ou utilisateur introuvable"}, 404

    if not article.allow_comments:
        return {"error": "Les commentaires sont desactives pour cet article"}, 403

    parent_comment = None
    if parent_comment_id is not None:
        parent_comment = Comment.query.get(parent_comment_id)
        if not parent_comment:
            return {"error": "Commentaire parent introuvable"}, 404
        if parent_comment.article_id != article_id:
            return {"error": "Le commentaire parent n'appartient pas a cet article"}, 400

    comment = Comment(
        content=content,
        article_id=article_id,
        user_id=user_id,
        parent_comment_id=parent_comment_id,
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
    if parent_comment and parent_comment.user_id not in {user_id, article.user_id}:
        create_notification(
            user_id=parent_comment.user_id,
            actor_id=user_id,
            event_type="comment_replied",
            title="Nouvelle reponse",
            message=f"{user.username} a repondu a votre commentaire",
            resource_type="comment",
            resource_id=parent_comment.id,
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

    comments = Comment.query.filter(Comment.article_id == article_id).order_by(Comment.created_at.asc(), Comment.id.asc()).all()
    results = list(reversed(_build_comment_tree(comments)))
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
