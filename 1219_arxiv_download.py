import arxiv
import requests
import os

# 논문 검색 함수
def search_arxiv_and_download(query, max_results=5, download_folder="downloads"):
    """
    ArXiv에서 논문을 검색하고 PDF 파일을 다운로드하는 함수.
    
    Args:
        query (str): 검색어.
        max_results (int): 검색할 최대 논문 수.
        download_folder (str): 다운로드할 폴더 경로.
    """
    # ArXiv 논문 검색
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate  # 최신 논문 우선 정렬
    )
    
    # 다운로드 폴더 생성
    os.makedirs(download_folder, exist_ok=True)
    
    # 검색 결과 처리 및 다운로드
    for result in search.results():
        title = result.title.replace("/", "-")  # 파일명에서 슬래시 제거
        pdf_url = result.pdf_url
        filename = os.path.join(download_folder, f"{title}.pdf")
        
        # PDF 다운로드
        print(f"Downloading: {title}")
        download_pdf(pdf_url, filename)

# PDF 다운로드 함수
def download_pdf(pdf_url, filename):
    """
    PDF 파일을 다운로드하는 함수.
    
    Args:
        pdf_url (str): PDF 파일 URL.
        filename (str): 저장할 파일명.
    """
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download PDF: {response.status_code}")

# 테스트 실행
search_arxiv_and_download(query="machine learning", max_results=3)