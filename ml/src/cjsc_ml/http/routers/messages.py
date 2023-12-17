#!/usr/bin/env python3
"""
This module handles queries to the ML model.
"""
import json
from datetime import datetime

import requests
import torch
from joblib import load
from loguru import logger
from catboost import CatBoostClassifier
from cjsc_ml.db.databases import \
    assets_db
from cjsc_ml.db.repos.regulatory_doc import \
    RegulatoryDocRepo
from cjsc_ml.http.schemas.message import \
    MessageSchema, MessageRequestType
from fastapi import APIRouter
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModel
from transformers import GenerationConfig

from cjsc_ml.ml_models.models import seed_everything, Summarizer, Retriever, Chat

# See https://fastapi.tiangolo.com/tutorial/bigger-applications/

router = APIRouter(
    prefix="/msg",
    tags=['Messages', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)

regdoc_repo = RegulatoryDocRepo(database=assets_db)

"""
CONFIG
"""

DEVICE = "cuda"
SUMMARIZATION_MODEL_NAME = "/home/leffff/PycharmProjects/misis-cjsc-lct-yakutia-2023/ml/src/cjsc_ml/csebuetnlp--mT5_multilingual_XLSum/snapshots/2437a524effdbadc327ced84595508f1e32025b3"
EMBEDDING_MODEL_NAME = "/home/leffff/PycharmProjects/misis-cjsc-lct-yakutia-2023/ml/src/cjsc_ml/ai-forever--sbert_large_nlu_ru/snapshots/95c66a03e1cea189286bf8ba895999f1fd355d8c"
GENERATION_MODEL_NAME = "/home/leffff/PycharmProjects/misis-cjsc-lct-yakutia-2023/ml/src/cjsc_ml/Den4ikAI--FRED-T5-LARGE_text_qa/snapshots/80fc4948c0b1600b4149c23879f5f203664e4e6f"
INDEX_PATH = "/home/leffff/PycharmProjects/misis-cjsc-lct-yakutia-2023/ml/src/cjsc_ml/index.bin"
OOD_PATH = "/home/leffff/PycharmProjects/misis-cjsc-lct-yakutia-2023/ml/src/cjsc_ml/catboost_ood"
RANDOM_STATE = 42

seed_everything(RANDOM_STATE)

"""
SUMMARIZER
"""

summarization_tokenizer = AutoTokenizer.from_pretrained(SUMMARIZATION_MODEL_NAME, local_files_only=True)
summarization_model = AutoModelForSeq2SeqLM.from_pretrained(SUMMARIZATION_MODEL_NAME, local_files_only=True)

summarizer = Summarizer(
    summarization_model,
    summarization_tokenizer,
    device=DEVICE
)

"""
RETRIEVER
"""

embedding_model = AutoModel.from_pretrained(EMBEDDING_MODEL_NAME, local_files_only=True)
embedding_tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME, local_files_only=True)

ood_model = CatBoostClassifier()
ood_model.load_model(OOD_PATH)

# ood_model = load(OOD_PATH)

retriever = Retriever(
    embedding_model,
    embedding_tokenizer,
    summarizer,
    ood_model,
    db=regdoc_repo,
    d=1024,
    k=1,
    batch_size=2,
    device="cpu"
)

# retriever.add(
#     regdoc_repo.find_by({"seq_id": {"$in": [i for i in range(530)]}})
# )
# retriever.save_index(INDEX_PATH)

retriever.load_index(INDEX_PATH)
retriever.get_indexer_size()

"""
GENERATOR
"""

generation_config = GenerationConfig.from_pretrained(GENERATION_MODEL_NAME)
generation_config.num_beams = 3
generation_config.seed = 42
generation_config.max_length = 128

generation_tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL_NAME)
generation_model = AutoModelForSeq2SeqLM.from_pretrained(GENERATION_MODEL_NAME, local_files_only=True)

chat = Chat(
    generation_model,
    generation_tokenizer,
    generation_config,
    retriever,
    device=DEVICE
)


@router.post(
    "/answer",
    response_model=MessageSchema,
)
def generate_response(msg: MessageSchema) -> MessageSchema:
    msg_json: str = json.dumps(
        msg.model_dump(),
        indent=4,
        default=str,
        ensure_ascii=True,
    )

    requests.post(
        "https://backend.cjsc.seizure.icu/msg/save",
        data=msg_json,
    )

    history = MessageSchema.model_validate_json(requests.get(
        f"https://backend.cjsc.seizure.icu/msg/history",
        params={"platform": msg.platform.value, "user_id": msg.user_id}
    ).content).chat_history

    logger.debug(history)

    history = " ".join([el.request_text for el in history if el.request_text is not None][-1:])

    request_type, answer = chat.answer(history)

    answer = MessageSchema(
        platform=msg.platform,
        user_id=msg.user_id,
        timestamp=datetime.utcnow(),
        request_text=None,
        response_text=answer,
        request_type=MessageRequestType(request_type)
    )

    msg_json: str = json.dumps(
        answer.model_dump(),
        indent=4,
        default=str,
        ensure_ascii=True,
    )

    requests.post(
        "https://backend.cjsc.seizure.icu/msg/save",
        data=msg_json,
    )

    return answer