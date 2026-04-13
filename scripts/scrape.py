import json, time, datetime, re
from pathlib import Path

FS_AGENTS = [
    {"id": 42,  "n": "レバテックフリーランス",               "fhid": 1,  "exact": True},
    {"id": 7,   "n": "ビズリンク(Bizlink)",                  "fhid": 23, "exact": True},
    {"id": 71,  "n": "ITプロパートナーズ(ITPRO PARTNERS)",   "fhid": 28, "exact": True},
    {"id": 1,   "n": "Midworks（ミッドワークス）",            "fhid": 15, "exact": True},
    {"id": 2,   "n": "ココナラテック",                       "fhid": 7,  "exact": True},
    {"id": 3,   "n": "フォスターフリーランス",               "fhid": 6,  "exact": True},
    {"id": 4,   "n": "ギークスジョブ(GEECHS JOB)",           "fhid": 8,  "exact": True},
    {"id": 5,   "n": "テクフリ(テックキャリアフリーランス)", "fhid": 14, "exact": True},
    {"id": 21,  "n": "アットエンジニア",                     "fhid": 18, "exact": True},
    {"id": 25,  "n": "Humalance(ヒューマランス)",             "fhid": 29, "exact": True},
    {"id": 37,  "n": "PE-BANK",                              "fhid": 9,  "exact": True},
    {"id": 43,  "n": "レバテッククリエイター",               "fhid": 2,  "exact": True},
    {"id": 56,  "n": "キャリアプラス",                       "fhid": 4,  "exact": True},
    {"id": 75,  "n": "TechTreat(テックトリート)",             "fhid": 30, "exact": True},
    {"id": 98,  "n": "mijicaフリーランス",                   "fhid": 13, "exact": True},
    {"id": 103, "n": "meetX FREELANCE",                      "fhid": 22, "exact": True},
    {"id": 106, "n": "ROSCA freelance",                      "fhid": 32, "exact": True},
    {"id": 130, "n": "Findy Freelance（ファインディフリーランス）", "fhid": 37, "exact": True},
    {"id": 158, "n": "TECHBIZ",                              "fhid": 40, "exact": True},
    {"id": 161, "n": "FLEXY(フレキシー)",                    "fhid": 20, "exact": True},
    {"id": 47,  "n": "1 on 1 Freelance",                     "fhid": 34, "exact": True},
]

COUNT_PATTERNS = [
    r'全([d,]+)件中',
    r'([d,]+)件の求人・案件',
    r'求人・案件（([d,]+)件）',
]


def get_fs_count(page, agent_id):
    """Playwright pageオブジェクトを使ってFS件数を取得"""
    url = "https://freelance-start.com/agents/%d/job?page=1" % agent_id
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        html = page.content()
        
        if "求人案件情報はありません" in html:
            return 0, 0
        
        for pat in COUNT_PATTERNS:
            m = re.search(pat, html)
            if m:
                tot = int(m.group(1).replace(",", ""))
                closed_m = re.search(r"終了[^d]*([d,]+)件", html)
                closed = int(closed_m.group(1).replace(",", "")) if closed_m else 0
                return tot, max(0, tot - closed)
        
        print("  WARN: no count pattern found", flush=True)
        return 0, 0
    except Exception as e:
        print("  ERR: %s" % str(e)[:50], flush=True)
        return 0, 0


def get_fh_count(page, fhid):
    """Playwright pageオブジェクトを使ってFH件数を取得"""
    url = "https://freelance-hub.jp/agent/%d/" % fhid
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1000)
        html = page.content()
        m = re.search(r"([d,]+)s*件", html)
        if m:
            tot = int(m.group(1).replace(",", ""))
            return tot, tot
        return 0, 0
    except Exception as e:
        print("  FH ERR: %s" % str(e)[:50], flush=True)
        return 0, 0


def main():
    from playwright.sync_api import sync_playwright
    
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    print("Started %s" % now.strftime("%Y-%m-%d %H:%M JST"), flush=True)

    results_fs = []
    results_fh = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
        )
        page = context.new_page()

        # FS スクレイプ
        for ag in FS_AGENTS:
            print("  FS %d %s ..." % (ag["id"], ag["n"]), end=" ", flush=True)
            tot, opn = get_fs_count(page, ag["id"])
            print("tot=%d open=%d" % (tot, opn), flush=True)
            results_fs.append({
                "id": ag["id"], "n": ag["n"], "tot": tot,
                "open": opn, "cl": tot - opn,
                "fhid": ag["fhid"], "exact": ag["exact"],
            })
            time.sleep(0.5)

        # FH スクレイプ
        seen = set()
        for ag in FS_AGENTS:
            if ag["fhid"] in seen:
                continue
            seen.add(ag["fhid"])
            print("  FH %d ..." % ag["fhid"], end=" ", flush=True)
            tot, opn = get_fh_count(page, ag["fhid"])
            print("tot=%d open=%d" % (tot, opn), flush=True)
            results_fh.append({
                "id": ag["fhid"], "n": ag["n"],
                "tot": tot, "open": opn, "cl": 0,
            })
            time.sleep(0.3)

        browser.close()

    out = {
        "updated":     now.isoformat(),
        "updatedDate": now.strftime("%Y年%m月%d日 %H:%M"),
        "fs": results_fs,
        "fh": results_fh,
    }
    p = Path(__file__).parent.parent / "data" / "data.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Done. FS=%d FH=%d" % (len(results_fs), len(results_fh)), flush=True)


if __name__ == "__main__":
    main()
