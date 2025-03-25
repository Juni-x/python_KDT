import google.generativeai as genai
import os
from dotenv import load_dotenv

# ✅ 환경 변수 로드
load_dotenv("env.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_response(prompt):
    """ Gemini API를 사용하여 응답 생성 """
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    query = "이부프로펜을 임산부가 먹어도 될까?"
    print(generate_response(query))