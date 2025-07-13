import math, csv, time, random
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm               # 진행률 표시용

BASE_URL  = "https://www.credly.com/mgmt/organizations/b3eb6cfd-544b-4e22-97cf-fd89de8be3ff/badges/earners?page={}"   # 페이지 번호 자리
TOTAL     = 875                       # 총 항목 수
PER_PAGE  = 50                        # 한 페이지당 항목 수
PAGES     = math.ceil(TOTAL / PER_PAGE)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def parse_items(html: str):
    soup = BeautifulSoup(html, "html.parser")
    nodes = soup.select("div.data-table__rows")        # ← 사이트 구조에 맞춰 수정
    return [n.get_text(strip=True) for n in nodes]

def main():
    with open("output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item_name"])           # 헤더
        with requests.Session() as s:
            s.headers.update(HEADERS)
             # ① 로그인: 여기에서 한 번만 수행  
            login_data = {"id": "gwkim@inpsyt.co.kr", "pw": "nuuhak@0106"}  
            login_resp = s.post("https://www.credly.com/users/sign_in", data=login_data, timeout=15)  
            if login_resp.status_code != 200:  
                raise SystemExit(f"로그인 실패: {login_resp.status_code}")

        # 필요 시 CSRF 토큰, 세션 쿠키 확인  
        # print(login_resp.cookies)
            for page in tqdm(range(1, PAGES + 1)):
                url  = BASE_URL.format(page)
                resp = s.get(url, timeout=15)
                if resp.status_code != 200:
                    print("warn: HTTP", resp.status_code, url)
                    break
                items = parse_items(resp.text)
                if not items:                    # 예외 처리
                    print("warn: no items on", url)
                    break
                for name in items:
                    writer.writerow([name])
                time.sleep(random.uniform(0.8, 1.5))  # 레이트 리밋 방지
    print("done → output.csv")

if __name__ == "__main__":
    main()
