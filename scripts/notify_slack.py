import json, urllib.request, os
from pathlib import Path

def main():
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        print("SLACK_WEBHOOK_URL not set, skipping")
        return

    d = json.loads(Path("data/data.json").read_text(encoding="utf-8"))
    updated = d.get("updatedDate", "")
    fs = d.get("fs", [])
    fh = d.get("fh", [])

    fs_with_jobs = [r for r in fs if r.get("tot", 0) > 0]
    fs_open_sum = sum(r.get("open", 0) for r in fs_with_jobs)
    fh_open_sum = sum(r.get("open", 0) for r in fh)
    fh_with_jobs = [r for r in fh if r.get("tot", 0) > 0]

    fh_map = {r["id"]: r for r in fh}
    both_count = len([r for r in fs if r.get("fhid") and fh_map.get(r["fhid"]) and r.get("tot", 0) > 0])

    CHARGE_APP, UNIT_PRICE = 1700, 43000
    total_rev = sum(
        round(CHARGE_APP * (r["open"] / fs_open_sum)) * UNIT_PRICE
        for r in fs_with_jobs if fs_open_sum > 0
    )

    top5 = sorted(fs_with_jobs, key=lambda r: r.get("open", 0), reverse=True)[:5]
    top5_txt = "\n".join(f"  {i+1}. {r['n']}：{r['open']:,}件" for i, r in enumerate(top5))

    msg = f"""📊 *フリーランスエージェント 日次レポート*
更新：{updated}

*📌 KPIサマリー*
- FS掲載：{len(fs_with_jobs)}社 ／ FS募集中：*{fs_open_sum:,}件*
- FH掲載：{len(fh_with_jobs)}社 ／ FH募集中：*{fh_open_sum:,}件*
- 両サイト共通：{both_count}社
- 成果報酬総額（想定）：*¥{total_rev:,}*

*🏆 FS募集中トップ5*
{top5_txt}

🔗 <https://splendid-hummingbird-7b0ae2.netlify.app|ダッシュボードを見る>"""

    data = json.dumps({"text": msg}).encode("utf-8")
    req = urllib.request.Request(webhook, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        print(f"Slack OK: {res.status}")

if __name__ == "__main__":
    main()
