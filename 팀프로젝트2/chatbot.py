import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from modules.sql_db import query_sql_db  # ✅ SQLite 데이터 검색
from modules.vector_db import load_drug_data  # ✅ 벡터 DB에서 검색

# ✅ 환경 변수 로드
load_dotenv("env.env")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ✅ Google Gemini API 설정
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-pro")

st.set_page_config(page_title='드럭인포맘', page_icon='💊', layout='wide')
st.title("💊 드럭인포맘 DrugInfoMom")

# ✅ 시스템 프롬프트 설정 (LLM의 응답 규칙 지정)
system_prompt = (
    "너는 임산부를 위한 약물 안정성 정보를 제공하는 AI야. 벡터DB를 참고해서 대답해주고, 사용자가 입력한 약물에 대한 정보를 제공할 때, 다음 가이드를 따라줘:\n"
    "\n"
    "1. 약물의 성분명과 일반적인 사용 목적을 간단하게 설명해줘.\n"
    "2. 해당 약물의 일반적인 부작용을 알려줘.\n"
    "3. 임산부가 복용가능한지, 복용할 경우 임신 주수에 따라 위험 여부를 분석해.\n"
    "4. 질문이 애매하거나 불확실할 경우, 전문가 상담을 권유해줘.\n"
    "\n"
    "⚠️ **경고문구**: 나는 의료 전문가가 아니므로, 제공된 정보는 참고용이며 반드시 의사나 약사와 상담해야 합니다.⚠️"
)

# ✅ 세션 초기화 (대화 기록 저장)
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "안녕하세요🤗 임산부 약물 상담 도우미 **드럭인포맘**입니다! 무엇을 도와드릴까요?"
    })

# ✅ 채팅 UI
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="💊" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

# ✅ 사용자 입력 받기
if user_question := st.chat_input("드럭인포맘에게 질문하세요."):
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_question)

    with st.spinner("드럭인포맘이 답변을 작성 중입니다..."):
        # ✅ 벡터 DB에서 유사한 약물 검색
        drug_info_df = query_sql_db(f"SELECT * FROM drug_info WHERE 성분명 LIKE '%{user_question}%' LIMIT 1")

        # ✅ 벡터 DB에서 검색된 결과가 없으면 LLM만 사용
        if drug_info_df.empty:
            full_prompt = f"{system_prompt}\n\n사용자 질문: {user_question}"
        else:
            drug_info_text = drug_info_df.to_string(index=False)
            full_prompt = f"{system_prompt}\n\n사용자 질문: {user_question}\n\n관련 약물 정보:\n{drug_info_text}"

        # ✅ 시스템 프롬프트를 적용한 전체 프롬프트로 LLM 호출
        response = model.generate_content(full_prompt)
        bot_answer = response.text

    # ✅ 답변 추가
    st.session_state.messages.append({"role": "assistant", "content": bot_answer})
    st.rerun()