from app.schemas.article_schema import ArticleSchema, article_schema, articles_schema
from app.schemas.comment_schema import CommentSchema, comment_schema, comments_schema
from app.schemas.friendship_schema import FriendshipSchema, friendship_schema, friendships_schema
from app.schemas.like_schema import LikeSchema, like_schema, likes_schema
from app.schemas.message_schema import MessageSchema, message_schema, messages_schema
from app.schemas.notification_schema import NotificationSchema, notification_schema, notifications_schema
from app.schemas.user_schema import UserSchema, user_schema, users_schema

__all__ = [
    "UserSchema",
    "user_schema",
    "users_schema",
    "ArticleSchema",
    "article_schema",
    "articles_schema",
    "FriendshipSchema",
    "friendship_schema",
    "friendships_schema",
    "LikeSchema",
    "like_schema",
    "likes_schema",
    "MessageSchema",
    "message_schema",
    "messages_schema",
    "NotificationSchema",
    "notification_schema",
    "notifications_schema",
    "CommentSchema",
    "comment_schema",
    "comments_schema",
]
