import enum

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ChatAnswerType(enum.Enum):
    JSON = 'json'
    STRING = 'string'


class Answer(Base):
    __tablename__ = "answer"

    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()"))
    history_id = sa.Column(sa.UUID(), nullable=False)
    question_id = sa.Column(sa.UUID(), nullable=False)
    str_answer = sa.Column(sa.String())
    json_answer = sa.Column(sa.JSON())
    has_analysis = sa.Column(sa.BOOLEAN())
    type = sa.Column(sa.Enum(ChatAnswerType))
    created_at = sa.Column(sa.TIMESTAMP(), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(sa.TIMESTAMP(), nullable=False, server_default=sa.func.now())

    def __repr__(self):
        return f"<{self.__class__.__qualname__}(question_id={self.question_id}, type={self.type})>"
