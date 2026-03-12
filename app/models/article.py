from app.extensions import db


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    allow_comments = db.Column(db.Boolean, nullable=False, default=True)
    is_public = db.Column(db.Boolean, nullable=False, default=True)
    author = db.relationship("User", back_populates="articles")
    comments = db.relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    likes = db.relationship("Like", back_populates="article", cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "allow_comments": self.allow_comments,
            "is_public": self.is_public,
            "likes_count": len(self.likes),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
