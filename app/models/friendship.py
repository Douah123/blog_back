from app.extensions import db


class Friendship(db.Model):
    __tablename__ = "friendships"

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    addressee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    requester = db.relationship(
        "User",
        foreign_keys=[requester_id],
        back_populates="sent_friendships",
    )
    addressee = db.relationship(
        "User",
        foreign_keys=[addressee_id],
        back_populates="received_friendships",
    )

    __table_args__ = (
        db.UniqueConstraint("requester_id", "addressee_id", name="uq_friendship_pair"),
        db.CheckConstraint("requester_id <> addressee_id", name="ck_friendship_not_self"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "requester_id": self.requester_id,
            "addressee_id": self.addressee_id,
            "status": self.status,
        }
