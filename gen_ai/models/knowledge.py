import enum

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class KnowledgeStatus(enum.Enum):
    CREATED = 'created'
    OS_LOAD_QUEUED = 'os_load_queued'
    OS_LOAD_SUCCEED = 'os_load_succeed'
    OS_LOAD_FAILED = 'os_load_failed'
    CSV_LOAD_QUEUED = 'csv_load_queued'
    CSV_LOAD_SUCCEED = 'csv_load_succeed'
    CSV_LOAD_FAILED = 'csv_load_failed'

    def __str__(self):
        return str(self.value)


class KnowledgeType(enum.Enum):
    MARKET_DATA = 'market_data'
    DOMAIN_KNOWLEDGE = 'domain_knowledge'

    def __str__(self):
        return str(self.value)


class Knowledge(Base):
    __tablename__ = "knowledge"

    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()"))
    s3_key = sa.Column(sa.String(200), nullable=False)
    file_name = sa.Column(sa.String(200), nullable=False)
    embedding_ids = sa.Column(sa.String())
    status = sa.Column(sa.Enum(KnowledgeStatus), nullable=False)
    type = sa.Column(sa.Enum(KnowledgeType), nullable=False)
    created_at = sa.Column(sa.TIMESTAMP(), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(sa.TIMESTAMP(), nullable=False, server_default=sa.func.now())

    def __repr__(self):
        return (f"<{self.__class__.__qualname__}"
                f"(file_name={self.file_name}, status={self.status}, s3_key={self.s3_key})>")
