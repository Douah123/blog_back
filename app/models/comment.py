from app.extensions import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    article = db.relationship("Article", back_populates="comments")
    author = db.relationship("User", back_populates="comments")
    parent_comment = db.relationship("Comment", remote_side=[id], back_populates="replies")
    replies = db.relationship(
        "Comment",
        back_populates="parent_comment",
        cascade="all, delete-orphan",
        single_parent=True,
        order_by="Comment.created_at.asc()",
    )

    def to_dict(self, include_replies=True):
        return {
            "id": self.id,
            "content": self.content,
            "article_id": self.article_id,
            "user_id": self.user_id,
            "parent_comment_id": self.parent_comment_id,
            "author_username": self.author.username if self.author else None,
            "author_fullname": self.author.fullname if self.author else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "replies_count": len(self.replies),
            "replies": [reply.to_dict() for reply in self.replies] if include_replies else [],
        }
