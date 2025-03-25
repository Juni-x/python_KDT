import os
import time
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# ✅ 환경 변수 로드 (Gemini API Key 가져오기)
load_dotenv("env.env")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ✅ Gemini 모델 설정
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-pro")

# ✅ CSV 파일 불러오기 (네 파일명으로 변경)
file_path = "시나리오_난이도_상.csv"  # 🔹 네 파일명에 맞게 수정 필요
df_scenario = pd.read_csv(file_path, header=None)  # 🔹 CSV 첫 번째 행이 컬럼명이 아니므로 header=None 추가

# ✅ 질문 리스트 가져오기
questions = df_scenario[0].tolist()  # 🔹 CSV에서 첫 번째 컬럼만 가져오기

# ✅ 챗봇 응답 저장 리스트
responses = []

# ✅ 챗봇에 질문 입력 및 응답 수집 (네가 사용하는 "드럭인포맘" 챗봇 테스트)
for idx, question in enumerate(questions):
    print(f"🔎 {idx+1}/{len(questions)}: {question}")  # 현재 진행 상황 출력
    conversation = f"사용자: {question}\n드럭인포맘:"  # 🔹 "드럭인포맘" 챗봇 테스트 문맥 포함
    response = model.generate_content(conversation)  # 챗봇 응답 생성
    bot_answer = response.text
    
    # 결과 저장
    responses.append({"질문": question, "응답": bot_answer})
    
    # API 속도 제한 방지
    time.sleep(1)

# ✅ 결과를 DataFrame으로 변환
df_results = pd.DataFrame(responses)

# ✅ 결과를 CSV 파일로 저장
output_file = "드럭인포맘_챗봇_테스트_결과.csv"
df_results.to_csv(output_file, index=False)

# ✅ 실행 완료 메시지 출력
print(f"✅ 테스트 완료! 챗봇 응답이 '{output_file}' 파일로 저장되었습니다.")