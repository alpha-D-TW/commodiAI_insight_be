import os
from typing import Annotated, Optional
from urllib.request import Request

from fastapi import FastAPI, UploadFile, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from gen_ai.aws import get_file_url
from gen_ai.chat.chat import chat
from gen_ai.chat.chat_analysis import chat_analysis, chat_all_analysis
from gen_ai.db import list_knowledge, SessionLocal, get_knowledge, delete_knowledge, list_history, insert_question, \
    insert_json_answer, insert_string_answer, get_question, update_question, get_history_by_id, Base, engine, \
    get_answer, update_json_answer, delete_history
from gen_ai.file_handler import delete_docs, load_files
from gen_ai.load_doc import load_csv_files
from gen_ai.model import ChatItem, ChatAnalysisItem
from gen_ai.models.answer import ChatAnswerType
from gen_ai.models.knowledge import KnowledgeType
from gen_ai.util import load_json_file

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.middleware("http")
# async def catch_exceptions_middleware(request: Request, call_next):
#     try:
#         return await call_next(request)
#     except Exception as err:
#         err_msg = f"Error occurred: {err}"
#         print(err_msg)
#         return JSONResponse(status_code=500, content=err_msg)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chat")
async def chat_api(q: ChatItem, db: Session = Depends(get_db)) -> dict:
    """
    return Dict {type: 'str', question, answer}
    """
    question_model = insert_question(db, q.question, q.chatSessionId) if not q.existingQuestionId \
        else get_question(db, q.existingQuestionId)
    result = chat(q.model, q.question, [])
    update_question(db, question_model.id, result["question"])
    if result["type"] == ChatAnswerType.JSON:
        insert_json_answer(db, question_model.id, question_model.history_id, result["answer"])
    else:
        insert_string_answer(db, question_model.id, question_model.history_id, result["answer"])
    history = get_history_by_id(db, question_model.history_id)
    return {
        "id": question_model.history_id,
        "question": question_model.question,
        "history": history
    }


@app.post("/chat-analysis")
async def chat_analysis_api(q: ChatAnalysisItem):
    """
    return Dict {type: 'str', question, answer}
    """
    return chat_analysis(q.model, q.question, q.data, q.is_english)


@app.get("/all-knowledge")
async def get_all_knowledge_api(type: KnowledgeType, db: Session = Depends(get_db)):
    return list_knowledge(db, type)


@app.post("/knowledge")
async def load_knowledge_api(files: Annotated[list[UploadFile], Form()], type: Annotated[KnowledgeType, Form()],
                             db: Session = Depends(get_db)):
    return load_files(db, files, type)


@app.get("/knowledge/{knowledge_id}/file-url")
async def get_knowledge_file_api(knowledge_id, db: Session = Depends(get_db)):
    knowledge = get_knowledge(db, knowledge_id)
    return {
        "fileUrl": get_file_url(knowledge.s3_key) if knowledge.s3_key else ""
    }


@app.delete("/knowledge/{knowledge_id}")
async def remove_knowledge_api(knowledge_id, db: Session = Depends(get_db)):
    knowledge = get_knowledge(db, knowledge_id)
    delete_knowledge(db, knowledge_id)
    if knowledge.embedding_ids:
        file_extension = knowledge.filename.split(".")[-1]
        delete_docs(file_extension, knowledge.embedding_ids)


@app.get("/histories")
async def get_histories_api(db: Session = Depends(get_db)):
    return list_history(db)


@app.get("/sample-questions")
async def get_sample_questions_api(is_english: Optional[bool] = None):
    file_name = "data_config/sample_questions_en.json" if is_english else "data_config/sample_questions_cn.json"
    return load_json_file(os.path.join(os.path.dirname(__file__), file_name))


@app.get("/knowledge/batch-data/{answer_id}")
async def get_batch_data_api(answer_id, model, is_english: Optional[bool] = None, db: Session = Depends(get_db)):
    answer = get_answer(db, answer_id)
    question = get_question(db, answer.question_id)
    if answer.type == ChatAnswerType.JSON and answer.json_answer:
        csv_result = load_csv_files(answer.json_answer)
        if answer.has_analysis:
            return [{**ans, **csv_result[i]} for i, ans in enumerate(answer.json_answer)]
        else:
            all_analysis = chat_all_analysis(model=model, question=question.question, data=csv_result,
                                             is_english=is_english)
            updated_answer = [{**ans, "analysis": all_analysis[i]} for i, ans in enumerate(answer.json_answer)]
            update_json_answer(db, answer_id, updated_answer)
            return [{**ans, **csv_result[i]} for i, ans in enumerate(updated_answer)]
    else:
        return []


@app.get("/histories/{history_id}")
async def get_history_api(history_id, db: Session = Depends(get_db)):
    return get_history_by_id(db, history_id)


@app.delete("/histories/{history_id}")
async def remove_history_api(history_id, db: Session = Depends(get_db)):
    return delete_history(db, history_id)
