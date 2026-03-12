from app.models.article import Article
from app.models.friendship import Friendship
from app.extensions import db
from app.utils.helpers import paginate_list


def _parse_bool_value(value, field_name):
    if value is None:
        return None, None
    if isinstance(value, bool):
        return value, None
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ["true", "1", "yes", "on"]:
            return True, None
        if normalized in ["false", "0", "no", "off"]:
            return False, None
    return None, {"error": f"{field_name} doit etre un booleen"}


def create_article(title, content, is_public, allow_comments, author_id):
    title = (title or "").strip()
    content = (content or "").strip()

    if not title or not content:
        return {"error": "title et content sont requis"}, 400
    if len(title) > 200:
        return {"error": "title ne doit pas depasser 200 caracteres"}, 400

    try:
        author_id = int(author_id)
    except (TypeError, ValueError):
        return {"error": "author_id invalide"}, 400

    parsed_is_public, bool_error = _parse_bool_value(is_public, "is_public")
    if bool_error:
        return bool_error, 400
    parsed_allow_comments, bool_error = _parse_bool_value(allow_comments, "allow_comments")
    if bool_error:
        return bool_error, 400

    if parsed_is_public is None:
        parsed_is_public = True
    if parsed_allow_comments is None:
        parsed_allow_comments = True

    article = Article(
        title=title,
        content=content,
        is_public=parsed_is_public,
        allow_comments=parsed_allow_comments,
        user_id=author_id,
    )
    db.session.add(article)
    db.session.commit()

    return {
        "message": "article cree avec succes", "article": article.to_dict(),
    }, 201


def get_my_articles(author_id, page=1, per_page=10):
    try:
        author_id = int(author_id)
    except (TypeError, ValueError):
        return {"error": "author_id invalide"}, 400

    articles = Article.query.filter(Article.user_id == author_id).order_by(Article.id.desc()).all()
    results = [article.to_dict() for article in articles]
    return paginate_list(results, page, per_page), 200


def update_article(article_id, author_id, title=None, content=None, is_public=None, allow_comments=None):
    try:
        article_id = int(article_id)
        author_id = int(author_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    article = Article.query.get(article_id)
    if not article:
        return {"error": "Article introuvable"}, 404
    if article.user_id != author_id:
        return {"error": "Acces refuse"}, 403

    if title is not None:
        title = str(title).strip()
        if not title:
            return {"error": "title ne peut pas etre vide"}, 400
        if len(title) > 200:
            return {"error": "title ne doit pas depasser 200 caracteres"}, 400
        article.title = title

    if content is not None:
        content = str(content).strip()
        if not content:
            return {"error": "content ne peut pas etre vide"}, 400
        article.content = content

    if is_public is not None:
        parsed_is_public, bool_error = _parse_bool_value(is_public, "is_public")
        if bool_error:
            return bool_error, 400
        article.is_public = parsed_is_public

    if allow_comments is not None:
        parsed_allow_comments, bool_error = _parse_bool_value(allow_comments, "allow_comments")
        if bool_error:
            return bool_error, 400
        article.allow_comments = parsed_allow_comments

    db.session.commit()
    return {"message": "article modifie avec succes", "article": article.to_dict()}, 200


def delete_article(article_id, author_id):
    try:
        article_id = int(article_id)
        author_id = int(author_id)
    except (TypeError, ValueError):
        return {"error": "IDs invalides"}, 400

    article = Article.query.get(article_id)
    if not article:
        return {"error": "Article introuvable"}, 404
    if article.user_id != author_id:
        return {"error": "Acces refuse"}, 403

    db.session.delete(article)
    db.session.commit()
    return {"message": "article supprime avec succes"}, 200


def get_articles_feed(current_user_id, page=1, per_page=10):
    try:
        current_user_id = int(current_user_id)
    except (TypeError, ValueError):
        return {"error": "ID utilisateur invalide"}, 400

    friendships = Friendship.query.filter(
        (
            (Friendship.requester_id == current_user_id)
            | (Friendship.addressee_id == current_user_id)
        )
        & (Friendship.status == "accepted")
    ).all()

    blocked_friendships = Friendship.query.filter(
        (
            (Friendship.requester_id == current_user_id)
            | (Friendship.addressee_id == current_user_id)
        )
        & (Friendship.status == "blocked")
    ).all()

    friend_ids = []
    for friendship in friendships:
        if friendship.requester_id == current_user_id:
            friend_ids.append(friendship.addressee_id)
        else:
            friend_ids.append(friendship.requester_id)

    blocked_ids = []
    for friendship in blocked_friendships:
        if friendship.requester_id == current_user_id:
            blocked_ids.append(friendship.addressee_id)
        else:
            blocked_ids.append(friendship.requester_id)

    friend_ids = [friend_id for friend_id in friend_ids if friend_id not in blocked_ids]

    friend_articles = []
    if friend_ids:
        friend_articles = Article.query.filter(
            (Article.user_id.in_(friend_ids)) & (Article.is_public == True)  # noqa: E712
        ).all()

    feed = sorted(friend_articles, key=lambda article: article.id, reverse=True)

    results = [article.to_dict() for article in feed]
    return paginate_list(results, page, per_page), 200
