import requests, json, time, datetime, re, sys
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

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

COUNT_PATTERNS = [
    r'([d,]+)件の求人・案件',
    r'全([d,]+)件中',
    r'求人・案件（([d,]+)件）',
    r'"totalCount"\s*:\s*(\d+)',
    r'"jobCount"\s*:\s*(\d+)',
    r'(\d{4,})件',
]


def fetch_page(url, retries=2):
    for i in range(retries + 1):
        try:
            r = requests.get(url, headers=H, timeout=20)
            if r.status_code == 200 and len(r.text) > 1000:
                return r.text
            print("status=%d len=%d" % (r.status_code, len(r.text)), flush=True)
        except Exception as e:
            print("err=%s" % e, flush=True)
        time.sleep(1)
    return None


def extract_count(html, debug=False):
    if debug:
        print("HTML_LEN=%d" % len(html), flush=True)
        for pat in COUNT_PATTERNS:
            m = re.search(pat, html)
            hit = m.group(0) if m else "NO_MATCH"
            print("  PAT=%s -> %s" % (pat, hit), flush=True)
        all_nums = re.findall(r'(\d{4,})件', html)
        print("  ALL_4PLUS_NUMS=%s" % str(all_nums[:10]), flush=True)
    for pat in COUNT_PATTERNS:
        m = re.search(pat, html)
        if m:
            return int(m.group(1).replace(',', ''))
    return None


def get_fs_count(agent_id, debug=False):
    html = fetch_page("https://freelance-start.com/agents/%d/job?page=1" % agent_id)
    if html is None:
        print("BLOCKED", flush=True)
        return 0, 0
    if "求人案件情報はありません" in html:
        return 0, 0

    tot = extract_count(html, debug=debug)
    if tot:
        closed_m = re.search(r'終了[^\d]*([\d,]+)件', html)
        closed = int(closed_m.group(1).replace(',', '')) if closed_m else 0
        return tot, max(0, tot - closed)

    print("WARN:fallback", flush=True)
    lo = binary_search_pages(agent_id)
    return lo * 20, lo * 20


def binary_search_pages(agent_id):
    def chk(p):
        html = fetch_page("https://freelance-start.com/agents/%d/job?page=%d" % (agent_id, p))
        return html is not None and "求人案件情報はありません" not in html

    if not chk(1):
        return 0
    lo, hi = 1, 2000
    while chk(hi):
        hi = min(hi * 2, 100000)
        time.sleep(0.2)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if chk(mid):
            lo = mid
        else:
            hi = mid - 1
        time.sleep(0.2)
    return lo


def scrape_fh(fhid):
    try:
        r = requests.get("https://freelance-hub.jp/agent/%d/" % fhid, headers=H, timeout=20)
        if r.status_code != 200:
            return 0, 0
        m = re.search(r'([\d,]+)\s*件', r.text)
        return (int(m.group(1).replace(',', '')), int(m.group(1).replace(',', ''))) if m else (0, 0)
    except Exception as e:
        print("FH err %d: %s" % (fhid, e), flush=True)
        return 0, 0


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    print("Started %s" % now.strftime('%Y-%m-%d %H:%M JST'), flush=True)

    results_fs = []
    first = True
    for ag in FS_AGENTS:
        print("  FS %d %s ..." % (ag["id"], ag["n"]), end=" ", flush=True)
        tot, opn = get_fs_count(ag["id"], debug=first)
        first = False
        print("tot=%d open=%d" % (tot, opn), flush=True)
        results_fs.append({
            "id": ag["id"], "n": ag["n"], "tot": tot,
            "open": opn, "cl": tot - opn,
            "fhid": ag["fhid"], "exact": ag["exact"],
        })
        time.sleep(0.5)

    results_fh = []
    seen = set()
    for ag in FS_AGENTS:
        if ag["fhid"] in seen:
            continue
        seen.add(ag["fhid"])
        print("  FH %d ..." % ag["fhid"], end=" ", flush=True)
        tot, opn = scrape_fh(ag["fhid"])
        print("tot=%d open=%d" % (tot, opn), flush=True)
        results_fh.append({"id": ag["fhid"], "n": ag["n"], "tot": tot, "open": opn, "cl": 0})
        time.sleep(0.5)

    out = {
        "updated":     now.isoformat(),
        "updatedDate": now.strftime("%Y\u5e74%m\u6708%d\u65e5 %H:%M"),
        "fs": results_fs, "fh": results_fh,
    }
    p = Path(__file__).parent.parent / "data" / "data.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Done. FS=%d FH=%d" % (len(results_fs), len(results_fh)), flush=True)


if __name__ == "__main__":
    main()
