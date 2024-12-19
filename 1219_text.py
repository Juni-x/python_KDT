import pytesseract
from pdf2image import convert_from_path
import os

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def pdf_to_text(file_path, output_folder="images", lang="eng"):
    """
    PDF 파일에서 텍스트를 추출.
    
    Args:
        file_path (str): PDF 파일 경로.
        output_folder (str): 페이지 이미지를 저장할 폴더.
        lang (str): Tesseract 언어 설정 (기본값은 영어).
    Returns:
        str: PDF에서 추출된 전체 텍스트.
    """
    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {file_path}")
    
    # PDF를 이미지로 변환
    images = convert_from_path(file_path)
    os.makedirs(output_folder, exist_ok=True)

    full_text = ""
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")
        image.save(image_path, "PNG")  # 이미지를 PNG로 저장

        # OCR 수행
        text = pytesseract.image_to_string(image, lang=lang)
        full_text += text + "\n"

    return full_text

def extract_conclusion_from_text(text):
    """
    텍스트에서 '결론' 부분을 추출.
    
    Args:
        text (str): PDF에서 추출된 전체 텍스트.
    Returns:
        str: '결론' 부분의 텍스트.
    """
    # 텍스트를 소문자로 변환하여 '결론' 탐지
    text_lower = text.lower()
    conclusion_start = text_lower.find("conclusion")
    if conclusion_start == -1:
        return "결론 섹션을 찾을 수 없습니다."

    # '결론' 이후 텍스트 가져오기
    conclusion_text = text[conclusion_start:]
    conclusion_excerpt = "\n".join(conclusion_text.split("\n")[:10])  # 상위 10줄만 추출
    return conclusion_excerpt

# 경로 설정
pdf_file = "/Users/juni/Desktop/python_KDT/downloads/example.pdf"  # PDF 파일 경로 수정
output_folder = "/Users/juni/Desktop/python_KDT/downloads/images"  # 이미지 저장 폴더 수정

# PDF에서 텍스트 추출
try:
    print("PDF에서 텍스트 추출 중...")
    text = pdf_to_text(pdf_file, output_folder=output_folder, lang="eng")
    print("추출된 텍스트:")
    print(text[:500])  # 일부 텍스트 출력

    # 결론 부분 추출
    conclusion = extract_conclusion_from_text(text)
    print("\n결론 부분:")
    print(conclusion)

except Exception as e:
    print(f"오류 발생: {e}")