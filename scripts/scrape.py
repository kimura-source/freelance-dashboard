import requests, json, time, datetime, re
from pathlib import Path


FS_AGENTS = [
    {"id": 42,  "n": "レバテックフリーランス",          "fhid": 1,  "exact": True},
    {"id": 7,   "n": "ビズリンク(Bizlink)",              "fhid": 23, "exact": True},
    {"id": 71,  "n": "ITプロパートナーズ(ITPRO PARTNERS)","fhid": 28, "exact": True},
    {"id": 1,   "n": "Midworks（ミッドワークス）",        "fhid": 15, "exact": True},
    {"id": 2,   "n": "ココナラテック",                   "fhid": 7,  "exact": True},
    {"id": 3,   "n": "フォスターフリーランス",           "fhid": 6,  "exact": True},
    {"id": 4,   "n": "ギークスジョブ(GEECHS JOB)",       "fhid": 8,  "exact": True},
    {"id": 5,   "n": "テクフリ(テックキャリアフリーランス)", "fhid": 14, "exact": True},
    {"id": 21,  "n": "アットエンジニア",                 "fhid": 18, "exact": True},
    {"id": 25,  "n": "Humalance(ヒューマランス)",         "fhid": 29, "exact": True},
    {"id": 37,  "n": "PE-BANK",                          "fhid": 9,  "exact": True},
    {"id": 43,  "n": "レバテッククリエイター",           "fhid": 2,  "exact": True},
    {"id": 56,  "n": "キャリアプラス",                   "fhid": 4,  "exact": True},
    {"id": 75,  "n": "TechTreat(テックトリート)",         "fhid": 30, "exact": True},
    {"id": 98,  "n": "mijicaフリーランス",               "fhid": 13, "exact": True},
    {"id": 103, "n": "meetX FREELANCE",                  "fhid": 22, "exact": True},
    {"id": 106, "n": "ROSCA freelance",                  "fhid": 32, "exact": True},
    {"id": 130, "n": "Findy Freelance（ファインディフリーランス）", "fhid": 37, "exact": True},
    {"id": 158, "n": "TECHBIZ",                          "fhid": 40, "exact": True},
    {"id": 161, "n": "FLEXY(フレキシー)",                "fhid": 20, "exact": True},
    {"id": 47,  "n": "1 on 1 Freelance",                 "fhid": 34, "exact": True},
]

H = {"User-Agent": "Mozilla/5.0 (compatible; dashboard-bot/1.0)"}


def get_fs_count(agent_id):
    """フリーランススタートの「全XX件中」を直接取得する"""
    try:
        url = f"https://freelance-start.com/agents/{agent_id}/job"
        r = requests.get(url, headers=H, timeout=15)
        if r.status_code != 200:
            return 0, 0
        # 「全27,945件中1-10件を表示中」のような文字列から件数を取得
        m = re.search(r'全([d,]+)件中', r.text)
        if m:
            tot = int(m.group(1).replace(',', ''))
        else:
            # 「求人案件情報はありません」の場合は0
            if "求人案件情報はありません" in r.text:
                return 0, 0
            tot = 0
        # 募集中件数はページ1の終了案件数から推定（totからclosedを引く）
        # closedは別途ページから取得を試みる
        # シンプルに: open = tot - closed。closedはページ内テキストから
        closed_m = re.search(r'終了[^d]*([d,]+)件', r.text)
        closed = int(closed_m.group(1).replace(',', '')) if closed_m else 0
        open_count = tot - closed
        return tot, open_count
    except Exception as e:
        print(f"  Error FS {agent_id}: {e}")
        return 0, 0


def scrape_fh(fhid):
    try:
        r = requests.get(f"https://freelance-hub.jp/agent/{fhid}/", headers=H, timeout=15)
        if r.status_code != 200:
            return 0, 0
        m = re.search(r'([d,]+)\s*件', r.text)
        if m:
            tot = int(m.group(1).replace(',', ''))
            return tot, tot
        return 0, 0
    except Exception as e:
        print(f"  Error FH {fhid}: {e}")
        return 0, 0


def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    results_fs = []
    for ag in FS_AGENTS:
        print(f"  FS {ag['id']} {ag['n']} ...", end=" ", flush=True)
        tot, opn = get_fs_count(ag["id"])
        closed = tot - opn
        print(f"tot={tot} open={opn} closed={closed}")
        results_fs.append({
            "id":    ag["id"],
            "n":     ag["n"],
            "tot":   tot,
            "open":  opn,
            "cl":    closed,
            "fhid":  ag["fhid"],
            "exact": ag["exact"],
        })
        time.sleep(0.5)

    results_fh = []
    seen_fh = set()
    for ag in FS_AGENTS:
        fhid = ag["fhid"]
        if fhid in seen_fh:
            continue
        seen_fh.add(fhid)
        print(f"  FH {fhid} ...", end=" ", flush=True)
        tot, opn = scrape_fh(fhid)
        print(f"tot={tot} open={opn}")
        results_fh.append({
            "id":   fhid,
            "n":    ag["n"],
            "tot":  tot,
            "open": opn,
            "cl":   0,
        })
        time.sleep(0.5)

    out = {
        "updated":     now.isoformat(),
        "updatedDate": now.strftime("%Y年%m月%d日 %H:%M"),
        "fs":          results_fs,
        "fh":          results_fh,
    }
    p = Path(__file__).parent.parent / "data" / "data.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved to {p}  ({len(results_fs)} FS agents, {len(results_fh)} FH agents)")


if __name__ == "__main__":
    main()
