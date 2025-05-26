import requests
import pandas as pd
import urllib.parse
import os

# 저장 파일 이름만 지정 (현 디렉토리에 저장됨)
CSV_PATH = "대전_측정소_목록.csv"
XLSX_PATH = "대전_측정소_목록.xlsx"

# API 키와 URL 구성
API_KEY = "MNUICj9LF0yMX9b9cMQiBVz62JWYaqaGxBOIATmwvQgzkfdHQjzCouGaBLIzyg6MYGQOHqefVCRf3E23XoqVGA=="
ENCODED_KEY = urllib.parse.quote(API_KEY, safe='')

url = (
    f"http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getMsrstnList"
    f"?serviceKey={ENCODED_KEY}&returnType=json&numOfRows=1000&pageNo=1"
)

response = requests.get(url)

print("상태코드:", response.status_code)
print("본문 미리보기:", response.text[:200])

if response.status_code == 200:
    try:
        items = response.json()["response"]["body"]["items"]
        df = pd.DataFrame(items)

        # 대전 주소 필터링
        daejeon_df = df[df["addr"].str.contains("대전")]

        # 현재 경로에 CSV/XLSX 저장
        daejeon_df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
        daejeon_df.to_excel(XLSX_PATH, index=False)

        print(f"✅ 저장 완료 → {os.path.abspath(CSV_PATH)}, {os.path.abspath(XLSX_PATH)}")
    except Exception as e:
        print("⚠️ 파싱 실패:", e)
        print("본문:", response.text)
else:
    print("❌ 요청 실패:", response.status_code)
