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
    "너는 임산부를 위한 약물 안정성 정보를 제공하는 AI야. 사용자가 입력한 약물에 대한 정보를 제공할 때, 다음 가이드를 따라줘:\n"
    "\n"
    "1. 약물의 성분명과 일반적인 사용 목적을 설명해.\n"
    "2. 임산부가 복용할 경우 임신 주수에 따라 위험 여부를 분석해.\n"
    "3. 해당 약물의 부작용과 임산부에게 미치는 영향을 알려줘.\n"
    "4. 데이터베이스의 정보를 반드시 참고해서 답변을 제공해줘.\n"
    "5. 약물의 대체 가능 여부와 안전한 대안이 있는지 제시해줘.\n"
    "6. 질문이 애매하거나 불확실할 경우, 전문가 상담을 권유해줘.\n"
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

        # ✅ 벡터 DB 검색 결과 디버깅 로그 추가
        if not drug_info_df.empty:
            print(f"✅ 벡터 DB에서 검색된 데이터:\n{drug_info_df}")
        else:
            print("⚠️ 벡터 DB에서 관련 데이터를 찾지 못했습니다.")

        # ✅ 벡터 DB에서 검색된 결과가 있을 경우 우선적으로 활용
        if not drug_info_df.empty:
            drug_info_text = drug_info_df.to_string(index=False)
            full_prompt = f"{system_prompt}\n\n사용자 질문: {user_question}\n\n🔍 벡터 DB 검색 결과:\n{drug_info_text}"
        else:
            full_prompt = f"{system_prompt}\n\n사용자 질문: {user_question}"

        # ✅ LLM 호출
        response = model.generate_content(full_prompt)
        bot_answer = response.text

    # ✅ 답변 추가
    st.session_state.messages.append({"role": "assistant", "content": bot_answer})
    st.rerun()