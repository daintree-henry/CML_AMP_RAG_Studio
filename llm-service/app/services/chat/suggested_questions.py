#
#  CLOUDERA APPLIED MACHINE LEARNING PROTOTYPE (AMP)
#  (C) Cloudera, Inc. 2025
#  All rights reserved.
#
#  Applicable Open Source License: Apache 2.0
#
#  NOTE: Cloudera open source products are modular software products
#  made up of hundreds of individual components, each of which was
#  individually copyrighted.  Each Cloudera open source product is a
#  collective work under U.S. Copyright Law. Your license to use the
#  collective work is as provided in your written agreement with
#  Cloudera.  Used apart from the collective work, this file is
#  licensed for your use pursuant to the open source license
#  identified above.
#
#  This code is provided to you pursuant a written agreement with
#  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
#  this code. If you do not have a written agreement with Cloudera nor
#  with an authorized and properly licensed third party, you do not
#  have any rights to access nor to use this code.
#
#  Absent a written agreement with Cloudera, Inc. ("Cloudera") to the
#  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
#  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
#  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
#  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
#  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
#  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
#  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
#  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
#  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
#  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
#  DATA.
#

from random import shuffle
from typing import List, Optional

import os
from app.ai.vector_stores.vector_store_factory import VectorStoreFactory
from app.services import llm_completion
from app.services.chat.utils import retrieve_chat_history, process_response
from app.services.metadata_apis import session_metadata_api
from app.services.metadata_apis.session_metadata_api import Session
from app.services.query import querier
from app.services.query.query_configuration import QueryConfiguration

LLM_RESPONSE_LANGUAGE = os.getenv("LLM_RESPONSE_LANGUAGE", "English")

SAMPLE_QUESTIONS = [
    "What is Cloudera, and how does it support organizations in managing big data?",
    "What are the key components of the Cloudera Data Platform (CDP), and how do they work together?",
    "How does Cloudera enable hybrid and multi-cloud data management for enterprises?",
    "What are the primary use cases for Cloudera's platform in industries such as finance, healthcare, and retail?",
    "How does Cloudera ensure data security and compliance with regulations like GDPR, HIPAA, and CCPA?",
    "What is the role of Apache Hadoop and Apache Spark in Cloudera's ecosystem, and how do they contribute to data processing?",
    "How does Cloudera's platform support machine learning and artificial intelligence workflows?",
    "What are the differences between Cloudera Data Platform (CDP) Public Cloud and CDP Private Cloud?",
    "How does Cloudera's platform handle data ingestion, storage, and real-time analytics at scale?",
    "What tools and features does Cloudera provide for data governance, lineage, and cataloging?,",
]

SAMPLE_KR_QUESTIONS = [
    "Cloudera란 무엇이며, 빅데이터 관리를 위해 조직을 어떻게 지원하나요?",
    "Cloudera Data Platform(CDP)의 주요 구성 요소는 무엇이며, 이들이 어떻게 함께 작동하나요?",
    "Cloudera는 어떻게 엔터프라이즈의 하이브리드 및 멀티 클라우드 데이터 관리를 가능하게 하나요?",
    "금융, 의료, 소매와 같은 산업에서 Cloudera 플랫폼의 주요 활용 사례는 무엇인가요?",
    "Cloudera는 GDPR, HIPAA, CCPA와 같은 규제 준수 및 데이터 보안을 어떻게 보장하나요?",
    "Cloudera의 생태계에서 Apache Hadoop과 Apache Spark의 역할은 무엇이며, 데이터 처리에 어떻게 기여하나요?",
    "Cloudera 플랫폼은 머신러닝 및 인공지능 워크플로우를 어떻게 지원하나요?",
    "Cloudera Data Platform(CDP) 퍼블릭 클라우드와 CDP 프라이빗 클라우드의 차이점은 무엇인가요?",
    "Cloudera 플랫폼은 대규모 데이터 수집, 저장 및 실시간 분석을 어떻게 처리하나요?",
    "Cloudera가 제공하는 데이터 거버넌스, 계보 추적(lineage), 카탈로그 기능 및 도구는 무엇인가요?",
]

LANGUAGE_QUESTION_MAP = {
    "english": SAMPLE_QUESTIONS,
    "korean": SAMPLE_KR_QUESTIONS,
}

def generate_dummy_suggested_questions() -> List[str]:
    questions = LANGUAGE_QUESTION_MAP.get(
        LLM_RESPONSE_LANGUAGE.lower(), SAMPLE_QUESTIONS
    ).copy()
    shuffle(questions)
    return questions[:4]


def _generate_suggested_questions_direct_llm(session: Session) -> List[str]:
    chat_history = retrieve_chat_history(session.id)
    if not chat_history:
        return generate_dummy_suggested_questions()
    query_str = (
        " Give me a list of possible follow-up questions."
        " Each question should be on a new line."
        " There should be no more than four (4) questions."
        " Each question should be no longer than fifteen (15) words."
        " The response should be a bulleted list, using an asterisk (*) to denote the bullet item."
        " Do not start like this - `Here are four questions that I can answer based on the context information`"
        " Only return the list."
        " Only return plain text."
        " Do not return any HTML tags or markdown formatting."
    )
    chat_response = llm_completion.completion(
        session.id, query_str, session.inference_model
    )
    suggested_questions = process_response(chat_response.message.content)
    return suggested_questions


def generate_suggested_questions(
    session_id: Optional[int],
    user_name: Optional[str] = None,
) -> List[str]:
    if session_id is None:
        return generate_dummy_suggested_questions()
    session = session_metadata_api.get_session(session_id, user_name)
    if len(session.get_all_data_source_ids()) == 0:
        return _generate_suggested_questions_direct_llm(session)

    total_data_sources_size: int = sum(
        map(
            lambda ds_id: VectorStoreFactory.for_chunks(ds_id).size() or 0,
            session.get_all_data_source_ids(),
        )
    )
    if total_data_sources_size == 0:
        return _generate_suggested_questions_direct_llm(session)
        # raise HTTPException(status_code=404, detail="Knowledge base not found.")

    chat_history = retrieve_chat_history(session_id)
    if total_data_sources_size == 0:
        suggested_questions = []
    else:
        query_str = (
            "Give me a list of questions that you can answer."
            " Each question should be on a new line."
            " There should be no more than four (4) questions."
            " Each question should be no longer than fifteen (15) words."
            " The response should be a bulleted list, using an asterisk (*) to denote the bullet item."
            " Only return plain text."
            " Do not return any HTML tags or markdown formatting."
            " Do not return questions based on the metadata of the document. Only the content."
            " Do not start like this - `Here are four questions that I can answer based on the context information`"
            " Only return the list."
        )
        if chat_history:
            query_str = (
                query_str
                + (
                    "I will provide a response from my last question to help with generating new questions."
                    " Consider returning questions that are relevant to the response"
                    " They might be follow up questions or questions that are related to the response."
                    " Here is the last response received:\n"
                )
                + chat_history[-1].content
            )
        response, _ = querier.query(
            session,
            query_str,
            QueryConfiguration(
                top_k=session.response_chunks,
                model_name=session.inference_model,
                rerank_model_name=None,
                exclude_knowledge_base=False,
                use_question_condensing=False,
                use_hyde=False,
                use_postprocessor=False,
                use_tool_calling=False,
            ),
            [],
            should_condense_question=False,
        )
        suggested_questions = process_response(response.response)
    return suggested_questions
