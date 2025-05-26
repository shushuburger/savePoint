import requests
import pandas as pd
import time
import os
from datetime import datetime

# API 키 (인코딩된 상태 그대로)
API_KEY = "MNUICj9LF0yMX9b9cMQiBVz62JWYaqaGxBOIATmwvQgzkfdHQjzCouGaBLIzyg6MYGQOHqefVCRf3E23XoqVGA%3D%3D"

# 현재 파일 위치 기준 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 경로 설정
STATION_FILE = os.path.join(BASE_DIR, "대전_측정소_목록.xlsx")
CSV_FILE = os.path.join(BASE_DIR, "대전_미세먼지_데이터.csv")
XLSX_FILE = os.path.join(BASE_DIR, "대전_미세먼지_데이터.xlsx")
JSON_FILE = os.path.join(BASE_DIR, "대전_미세먼지_데이터.json")  # ✅ 추가

# 측정소 목록 불러오기
station_df = pd.read_excel(STATION_FILE)
daejeon_stations = station_df["stationName"].dropna().unique().tolist()

def fetch_dust_data():
    results = []
    for station in daejeon_stations:
        url = (
            f"http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/"
            f"getMsrstnAcctoRltmMesureDnsty"
            f"?serviceKey={API_KEY}"
            f"&returnType=json"
            f"&numOfRows=1"
            f"&pageNo=1"
            f"&stationName={station}"
            f"&dataTerm=DAILY"
            f"&ver=1.0"
        )
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                body = res.json().get("response", {}).get("body", {})
                items = body.get("items", [])
                if items:
                    item = items[0]
                    results.append({
                        "수집시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "측정시각": item.get("dataTime", ""),
                        "측정소": station,
                        "PM10": item.get("pm10Value", ""),
                        "PM2.5": item.get("pm25Value", ""),
                        "통합지수": item.get("khaiValue", ""),
                        "오존": item.get("o3Value", ""),
                        "이산화질소": item.get("no2Value", ""),
                        "일산화탄소": item.get("coValue", ""),
                        "아황산가스": item.get("so2Value", "")
                    })
                else:
                    print(f"⚠️ {station} → 측정 데이터 없음 (items 비어 있음)")
            else:
                print(f"❌ {station} 요청 실패: {res.status_code}")
        except Exception as e:
            print(f"⚠️ {station} 오류: {e}")
        time.sleep(0.2)
    return pd.DataFrame(results)

def append_and_save(new_df):
    if new_df.empty:
        print("⚠️ 새로 수집된 데이터가 없습니다.")
        return

    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    # 저장 (CSV, Excel, JSON)
    combined_df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    combined_df.to_excel(XLSX_FILE, index=False)
    combined_df.to_json(JSON_FILE, orient="records", force_ascii=False, indent=2)  # ✅ JSON 저장

    print(f"✅ 저장 완료 ({len(new_df)}개 추가됨) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 수집 루프 시작
while True:
    print("📡 미세먼지 데이터 수집 중...")
    new_data = fetch_dust_data()
    append_and_save(new_data)

    print("🕒 다음 수집까지 1시간 대기...\n")
    time.sleep(60 * 60)
