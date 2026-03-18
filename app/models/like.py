from app.extensions import db


class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    user = db.relationship("User", back_populates="likes")
    article = db.relationship("Article", back_populates="likes")

    __table_args__ = (
        db.UniqueConstraint("user_id", "article_id", name="uq_like_user_article"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "article_id": self.article_id,
            "username": self.user.username if self.user else None,
            "fullname": self.user.fullname if self.user else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
