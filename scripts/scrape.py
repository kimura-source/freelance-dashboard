import requests, json, time, datetime
from pathlib import Path

FS_AGENTS = [
      {"id": 42, "name": "レバテックフリーランス", "fhid": 1},
      {"id": 7, "name": "ビズリンク(Bizlink)", "fhid": 23},
      {"id": 71, "name": "ITプロパートナーズ", "fhid": None},
      {"id": 1, "name": "Midworks", "fhid": 20},
      {"id": 2, "name": "ココナラテック", "fhid": 9},
      {"id": 3, "name": "フォスターフリーランス", "fhid": 28},
      {"id": 4, "name": "ギークスジョブ", "fhid": None},
      {"id": 5, "name": "テクフリ", "fhid": None},
      {"id": 21, "name": "アットエンジニア", "fhid": 7},
      {"id": 25, "name": "Humalance", "fhid": 15},
      {"id": 37, "name": "PE-BANK", "fhid": 53},
      {"id": 43, "name": "レバテッククリエイター", "fhid": 2},
      {"id": 56, "name": "キャリアプラス", "fhid": 19},
      {"id": 59, "name": "エンジニアファクトリー", "fhid": None},
      {"id": 75, "name": "TechTreat", "fhid": None},
      {"id": 98, "name": "mijicaフリーランス", "fhid": 34},
      {"id": 103, "name": "meetX FREELANCE", "fhid": 45},
      {"id": 106, "name": "ROSCA freelance", "fhid": 61},
      {"id": 130, "name": "Findy Freelance", "fhid": 60},
      {"id": 158, "name": "TECHBIZ", "fhid": None},
      {"id": 161, "name": "FLEXY", "fhid": 30},
      {"id": 174, "name": "テクワーク", "fhid": None},
      {"id": 170, "name": "Stylee", "fhid": None},
      {"id": 82, "name": "アサインナビ", "fhid": None},
]

H = {"User-Agent": "Mozilla/5.0", "Accept": "text/html", "Accept-Language": "ja"}

def chk(id, p):
      try:
                r = requests.get(f"https://freelance-start.com/agents/{id}/job?page={p}", headers=H, timeout=15)
                return r.status_code == 200 and "求人案件情報はありません" not in r.text
            except:
        return False

              def bs(id):
                    if not chk(id, 1): return 0
                          lo, hi = 1, 2000
                    while chk(id, hi):
                              hi *= 2
                              if hi > 100000: hi = 100000; break
                                        time.sleep(0.3)
                          while lo < hi:
                                    mid = (lo + hi + 1) // 2
                                    if chk(id, mid): lo = mid
      else: hi = mid - 1
                time.sleep(0.3)
    return lo

def main():
      print(f"=== start {datetime.datetime.now()} ===")
    results = []
    for i, a in enumerate(FS_AGENTS):
              print(f"[{i+1}/{len(FS_AGENTS)}] {a['name']}", flush=True)
              lp = bs(a["id"])
              o = lp * 20
              print(f"  -> last_page={lp}, open={o}", flush=True)
              results.append({"id": a["id"], "n": a["name"], "tot": o, "open": o, "cl": 0, "fhid": a.get("fhid"), "lastPage": lp})
              time.sleep(1.0)
          now = datetime.datetime.now()
    out = {"updated": now.strftime("%Y-%m-%dT%H:%M:%S+09:00"), "updatedDate": now.strftime("%Y年%m月%d日 %H:%M"), "fs": results}
    Path("data").mkdir(exist_ok=True)
    Path("data/data.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("=== done ===")

if __name__ == "__main__":
      main()
