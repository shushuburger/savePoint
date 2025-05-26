import os
import json
import pandas as pd

# 현재 average.py 파일 기준 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "대전_미세먼지_데이터.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "대전_구별_미세먼지_요약.json")

# JSON 파일 불러오기
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# 측정소 → 정확한 구 매핑
station_to_district = {
    "읍내동": "대덕구",
    "문평동": "대덕구",
    "문창동": "중구",
    "구성동": "유성구",
    "노은동": "유성구",
    "상대동(대전)": "유성구",
    "관평동": "유성구",
    "지족동": "유성구",
    "대흥동1": "중구",
    "성남동1": "중구",
    "대성동": "동구",
    "정림동": "서구",
    "둔산동": "서구",
    "월평동": "서구"
}

# 구 컬럼 추가
df["구"] = df["측정소"].map(station_to_district)

# 수치형 컬럼 변환 (숫자 아닌 값 처리 포함)
numeric_cols = ["PM10", "PM2.5", "통합지수", "오존", "이산화질소", "일산화탄소", "아황산가스"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 구별 평균 계산
grouped = df.groupby("구")[numeric_cols].mean().round(2).reset_index()

# ✅ "대전광역시 ○○구" 형식으로 구 이름 변경
grouped["구"] = grouped["구"].apply(lambda x: f"대전광역시 {x}")

# ✅ 딕셔너리 구조로 변환
grouped.set_index("구", inplace=True)
grouped_dict = grouped.to_dict(orient="index")

# ✅ JSON 저장
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(grouped_dict, f, ensure_ascii=False, indent=2)

print(f"\n✅ 저장 완료: {OUTPUT_PATH}")
