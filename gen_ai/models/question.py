import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Question(Base):
    __tablename__ = "question"

    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()"))
    history_id = sa.Column(sa.UUID(), nullable=False, server_default=sa.text("gen_random_uuid()"))
    question = sa.Column(sa.String(), nullable=False)
    prompted_question = sa.Column(sa.String())
    created_at = sa.Column(sa.TIMESTAMP(), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(sa.TIMESTAMP(), nullable=False, server_default=sa.func.now())

    class Config:
        orm_mode = True

    def __repr__(self):
        return f"<{self.__class__.__qualname__}(question={self.question}, prompted_question={self.prompted_question})>"
