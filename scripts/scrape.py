import requests, json, time, datetime, re
from pathlib import Path

FS_AGENTS = [
    {"id": 42, "n": "レバテックフリーランス", "fhid": 1, "exact": True},
    {"id": 7,  "n": "ビズリンク(Bizlink)", "fhid": 23, "exact": True},
    {"id": 71, "n": "ITプロパートナーズ(ITPRO PARTNERS)", "fhid": None, "exact": True},
    {"id": 1,  "n": "Midworks（ミッドワークス）", "fhid": 20, "exact": True},
    {"id": 2,  "n": "ココナラテック", "fhid": 9, "exact": True},
    {"id": 3,  "n": "フォスターフリーランス", "fhid": 28, "exact": True},
    {"id": 4,  "n": "ギークスジョブ(GEECHS JOB)", "fhid": None, "exact": True},
    {"id": 5,  "n": "テクフリ(テックキャリアフリーランス)", "fhid": None, "exact": True},
    {"id": 21, "n": "アットエンジニア", "fhid": 7, "exact": True},
    {"id": 25, "n": "Humalance(ヒューマランス)", "fhid": 15},
    {"id": 37, "n": "PE-BANK", "fhid": 53, "exact": True},
    {"id": 43, "n": "レバテッククリエイター", "fhid": 2, "exact": True},
    {"id": 56, "n": "キャリアプラス", "fhid": 19, "exact": True},
    {"id": 75, "n": "TechTreat(テックトリート)", "fhid": None, "exact": True},
    {"id": 98, "n": "mijicaフリーランス", "fhid": 34, "exact": True},
    {"id": 103,"n": "meetX FREELANCE", "fhid": 45, "exact": True},
    {"id": 106,"n": "ROSCA freelance", "fhid": 61},
    {"id": 130,"n": "Findy Freelance（ファインディフリーランス）", "fhid": 60, "exact": True},
    {"id": 158,"n": "TECHBIZ", "fhid": None, "exact": True},
    {"id": 161,"n": "FLEXY(フレキシー)", "fhid": 30, "exact": True},
    {"id": 47, "n": "1 on 1 Freelance", "fhid": 36},
]

FH_AGENTS = [
    {"id": 1,  "n": "レバテックフリーランス"},
    {"id": 2,  "n": "レバテッククリエイター"},
    {"id": 3,  "n": "Next Career Freelance"},
    {"id": 4,  "n": "SEES(シーズ)"},
    {"id": 5,  "n": "CloudBuilders"},
    {"id": 6,  "n": "GrowthTech"},
    {"id": 7,  "n": "アットエンジニア"},
    {"id": 8,  "n": "Webist"},
    {"id": 9,  "n": "ココナラテック"},
    {"id": 10, "n": "フリーコンサルBiz"},
    {"id": 12, "n": "Freed Job"},
    {"id": 13, "n": "ランサーズエージェント"},
    {"id": 14, "n": "テックビズフリーランス"},
    {"id": 15, "n": "Humalance"},
    {"id": 16, "n": "HiPro Tech"},
    {"id": 17, "n": "フリーランスのミカタ"},
    {"id": 18, "n": "Relance"},
    {"id": 19, "n": "キャリアプラス"},
    {"id": 20, "n": "Midworks"},
    {"id": 22, "n": "フリコン"},
    {"id": 23, "n": "ビズリンク"},
    {"id": 24, "n": "チョクフリ"},
    {"id": 28, "n": "フォスターフリーランス"},
    {"id": 30, "n": "FLEXY"},
    {"id": 34, "n": "mijicaフリーランス"},
    {"id": 35, "n": "オルタナエクス"},
    {"id": 36, "n": "1 on 1 Freelance"},
    {"id": 38, "n": "コンプロフリーランス"},
    {"id": 39, "n": "テックリーチ"},
    {"id": 41, "n": "Freelance match"},
    {"id": 44, "n": "フリーランスポート"},
    {"id": 45, "n": "meetX FREELANCE"},
    {"id": 46, "n": "World in Freelance"},
    {"id": 47, "n": "プロエンジニア"},
    {"id": 53, "n": "Pe-BANK フリーランス"},
    {"id": 60, "n": "Findy Freelance"},
    {"id": 61, "n": "ROSCA freelance"},
]

H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
     "Accept": "text/html", "Accept-Language": "ja"}

def chk(id, p):
    try:
        r = requests.get(f"https://freelance-start.com/agents/{id}/job?page={p}", headers=H, timeout=15)
        return r.status_code == 200 and "求人案件情報はありません" not in r.text
    except Exception:
        return False

def bs(id):
    if not chk(id, 1):
        return 0
    lo, hi = 1, 2000
    while chk(id, hi):
        hi *= 2
        if hi > 100000:
            hi = 100000
            break
        time.sleep(0.3)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if chk(id, mid):
            lo = mid
        else:
            hi = mid - 1
        time.sleep(0.3)
    return lo

def scrape_fh(id):
    try:
        r = requests.get(f"https://freelance-hub.jp/agent/{id}/", headers=H, timeout=15)
        if r.status_code != 200:
            return 0, 0
        # metaタグから件数取得（description等）
        m = re.search(r'(\d[\d,]+)\s*件', r.text)
        if m:
            tot = int(m.group(1).replace(',', ''))
            return tot, tot
        return 0, 0
    except Exception:
        return 0, 0

def main():
    print(f"=== start {datetime.datetime.now()} ===")

    # FS スクレイピング
    fs_results = []
    for i, a in enumerate(FS_AGENTS):
        print(f"[FS {i+1}/{len(FS_AGENTS)}] {a['n']}", flush=True)
        lp = bs(a["id"])
        o = lp * 20
        r = {"id": a["id"], "n": a["n"], "tot": o, "open": o, "cl": 0, "fhid": a.get("fhid")}
        if a.get("exact"):
            r["exact"] = True
        fs_results.append(r)
        time.sleep(1.0)

    # FH スクレイピング
    fh_results = []
    for i, a in enumerate(FH_AGENTS):
        print(f"[FH {i+1}/{len(FH_AGENTS)}] {a['n']}", flush=True)
        tot, opn = scrape_fh(a["id"])
        fh_results.append({"id": a["id"], "n": a["n"], "tot": tot, "open": opn, "cl": 0})
        time.sleep(0.8)

    now = datetime.datetime.now()
    out = {
        "updated": now.strftime("%Y-%m-%dT%H:%M:%S+09:00"),
        "updatedDate": now.strftime("%Y年%m月%d日 %H:%M"),
        "fs": fs_results,
        "fh": fh_results,
    }
    Path("data").mkdir(exist_ok=True)
    Path("data/data.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("=== done ===")

if __name__ == "__main__":
    main()
