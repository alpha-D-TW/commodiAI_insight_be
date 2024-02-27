from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from .config import dbs
from .models.answer import Answer, ChatAnswerType
from .models.knowledge import Knowledge, KnowledgeStatus, KnowledgeType
from .models.question import Question

DEFAULT_DB_PORT = 5432
DB_CONNECT_TIMEOUT = 20

engine = create_engine(
    f"postgresql+psycopg2://{dbs.get('user')}:{dbs.get('password')}@{dbs.get('host')}:{dbs.get('port')}/{dbs.get('database')}",
    echo=True)
print(f"Connect to DB: {dbs.get('host')}:{dbs.get('port')}/{dbs.get('database')}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def mapping_query(db: Session, final_query):
    result = db.query(final_query)
    columns = [r["name"] for r in result.column_descriptions]
    records = result.all()
    final = []
    for record in records:
        final.append({k: record[j] for j, k in enumerate(columns)})
    return final


def list_knowledge(db: Session, knowledge_type: KnowledgeType):
    knowledge_rank = db.query(Knowledge,
                              func.rank().over(order_by=Knowledge.created_at.desc(),
                                               partition_by=Knowledge.file_name).label(
                                  'rank')).filter(Knowledge.type == knowledge_type).subquery()
    latest_knowledge = db.query(knowledge_rank).filter(knowledge_rank.c.rank == 1).subquery()
    final_query = db.query(latest_knowledge.c.id, latest_knowledge.c.file_name.label("name"), latest_knowledge.c.status,
                           latest_knowledge.c.s3_key.label("s3Key"),
                           latest_knowledge.c.created_at.label("created")).order_by(
        latest_knowledge.c.created_at.desc()).subquery()
    return mapping_query(db, final_query)


def insert_knowledge(db: Session, file_name, s3_key, knowledge_type, status=KnowledgeStatus.CREATED):
    knowledge = Knowledge(file_name=file_name, s3_key=s3_key, type=knowledge_type, status=status)
    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)
    return knowledge.id


def get_knowledge(db: Session, knowledge_id: str):
    return db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()


def update_knowledge(db: Session, knowledge_id, status, embedding_ids=None):
    knowledge = get_knowledge(db, knowledge_id)
    knowledge.status = status
    knowledge.embedding_ids = embedding_ids
    db.commit()


def delete_knowledge(db: Session, knowledge_id: str):
    knowledge = get_knowledge(db, knowledge_id)
    db.delete(knowledge)
    db.commit()


def list_history(db: Session):
    question_rank = db.query(
        Question,
        func.rank().over(
            order_by=Question.updated_at.desc(),
            partition_by=Question.history_id
        ).label('rank')
    ).subquery()
    latest_question = db.query(question_rank).filter(question_rank.c.rank == 1).order_by(
        question_rank.c.updated_at.desc()).limit(20).subquery()
    agg_history = db.query(
        Question.history_id,
        func.count(Question.id.distinct()).label('chatCount'),
    ).group_by(Question.history_id).subquery()
    final_query = db.query(
        latest_question.c.history_id.label("historyId"),
        latest_question.c.updated_at.label("updated"),
        latest_question.c.question.label("question"),
        agg_history.c.chatCount,
    ).join(agg_history, latest_question.c.history_id == agg_history.c.history_id).order_by(
        latest_question.c.updated_at.desc()).subquery()
    return mapping_query(db, final_query)


def get_history_by_id(db: Session, history_id: str):
    questions = db.query(Question).filter(Question.history_id == history_id).subquery()
    answers = db.query(Answer,
                       func.rank().over(order_by=Answer.created_at.desc(), partition_by=Answer.question_id).label(
                           'rank')).filter(Answer.history_id == history_id).subquery()
    latest_answers = db.query(answers).filter(answers.c.rank == 1).subquery()
    agg = (db.query(questions.c.id.label("questionId"),
                    questions.c.question,
                    questions.c.prompted_question.label("promptedQuestion"),
                    questions.c.created_at.label("created"),
                    latest_answers.c.id.label("answerId"),
                    latest_answers.c.type,
                    latest_answers.c.str_answer.label("strAnswer"),
                    latest_answers.c.json_answer.label("jsonAnswer"), )
           .join(latest_answers, questions.c.id == latest_answers.c.question_id).subquery())
    final_query = db.query(agg).order_by(agg.c.created.asc()).subquery()
    return mapping_query(db, final_query)


def get_question(db: Session, question_id: str):
    return db.query(Question).filter(Question.id == question_id).first()


def insert_question(db: Session, question, history_id):
    question = Question(history_id=history_id, question=question) if history_id else Question(question=question)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def update_question(db: Session, question_id, prompted_question):
    question = get_question(db, question_id)
    question.prompted_question = prompted_question
    db.commit()


def get_answer(db: Session, answer_id: str):
    return db.query(Answer).filter(Answer.id == answer_id).first()


def insert_string_answer(db: Session, question_id, history_id, str_answer):
    answer = Answer(history_id=history_id, question_id=question_id, str_answer=str_answer, type=ChatAnswerType.STRING)
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer.id


def insert_json_answer(db: Session, question_id, history_id, json_answer):
    answer = Answer(history_id=history_id, question_id=question_id, json_answer=json_answer, type=ChatAnswerType.JSON)
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer.id


def update_json_answer(db: Session, answer_id, json_answer):
    answer = get_answer(db, answer_id)
    answer.json_answer = json_answer
    answer.has_analysis = True
    db.commit()
    db.refresh(answer)
    return answer.id


def delete_history(db: Session, history_id: str):
    db.query(Question).filter(Question.history_id == history_id).delete()
    db.query(Answer).filter(Answer.history_id == history_id).delete()
    db.commit()
