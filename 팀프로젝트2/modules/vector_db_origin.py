import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # ✅ Google Gemini 임베딩 사용

# ✅ 환경 변수 로드 (Google Gemini API 사용)
load_dotenv("env.env")  
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ✅ 벡터 DB 저장 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "data/vector_store/")

def load_drug_data():
    """ SQLite에서 약물 데이터 불러오기 """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT 성분명, 성분명_한글, 대표_상품명, 임부금기등급, 허가사항 FROM drug_info", conn)
    conn.close()

    if df.empty:
        raise ValueError("⚠️ SQLite에서 불러온 데이터가 없습니다. DB를 확인하세요.")
    
    return df

def create_vector_db():
    """ 벡터 DB 생성 및 저장 (Google Gemini API 사용) """
    df = load_drug_data()
    
    # ✅ Google Gemini API 기반 임베딩 사용 (모델 지정)
    embeddings = GoogleGenerativeAIEmbeddings(
        google_api_key=gemini_api_key, 
        model="models/embedding-001"  # 🔥 필수 모델 추가
    )

    # ✅ 약물 데이터 임베딩 및 벡터 DB 저장
    faiss_db = FAISS.from_texts(df["성분명"].tolist(), embeddings)
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    faiss_db.save_local(VECTOR_STORE_PATH)

    print("✅ 벡터 DB 저장 완료!")

if __name__ == "__main__":
    create_vector_db()