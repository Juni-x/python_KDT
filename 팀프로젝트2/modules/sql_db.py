import sqlite3
import os
import pandas as pd

# ✅ SQLite DB 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")

def init_database():
    """ SQLite 데이터베이스 초기화 및 데이터 삽입 """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ✅ 테이블 존재 여부 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='drug_info'")
    table_exists = cursor.fetchone()

    if not table_exists:
        print("✅ 테이블이 존재하지 않습니다. 테이블을 생성하고 데이터를 삽입합니다.")
        cursor.execute("""
        CREATE TABLE drug_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            성분명 TEXT,
            성분명_한글 TEXT,
            대표_상품명 TEXT,
            임부금기등급 TEXT,
            허가사항 TEXT
        )
        """)
    else:
        print("✅ 테이블이 이미 존재합니다.")

    conn.commit()
    conn.close()
    print("✅ SQLite 데이터베이스 초기화 완료!")

def query_sql_db(query):
    """ 주어진 SQL 쿼리를 실행하고 결과를 Pandas DataFrame으로 반환 """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    init_database()