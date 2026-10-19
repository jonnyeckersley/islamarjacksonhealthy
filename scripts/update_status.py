
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from html.parser import HTMLParser

SOURCE = "https://www.baltimoreravens.com/team/injury-report/index-app"
OUTPUT = Path("status.json")


class TableReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.table = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row:
                self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def get_status():
    req = Request(
        SOURCE,
        headers={"User-Agent": "Mozilla/5.0 (compatible; InjuryStatusBot/1.0)"}
    )
    with urlopen(req, timeout=25) as response:
        html = response.read().decode("utf-8", errors="replace")

    # Conservative safeguard: the official page can retain last game's report.
    # A recent date must be visible; otherwise return UNKNOWN.
    plain = re.sub(r"<[^>]*>", " ", html)
    now = datetime.now(timezone.utc)
    dates = []
    for month, day, year in re.findall(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d{2})\b", plain, re.I):
        try:
            dt = datetime.strptime(f"{month} {day} {year}", "%B %d %Y").replace(tzinfo=timezone.utc)
            if timedelta(days=-1) <= now - dt <= timedelta(days=2):
                dates.append(dt)
        except ValueError:
            pass
    if not dates:
        raise ValueError("No recent dated injury report could be verified")
    report_date = max(dates).date().isoformat()

    parser = TableReader()
    parser.feed(html)

    for table in parser.tables:
        for row in table:
            if not row or not re.search(r"\bLamar\s+Jackson\b", row[0], re.I):
                continue

            # Expected: Player, Position, Injury, practice days, Game Status
            if len(row) < 5 or row[1].upper() != "QB":
                continue

            injury = row[2]
            game = row[-1].strip().upper()
            practice = [
                x.upper().strip()
                for x in row[3:-1]
                if x.upper().strip() in ("FP", "LP", "DNP")
            ]
            latest = practice[-1] if practice else None

            if game in ("OUT", "DOUBTFUL", "QUESTIONABLE"):
                status = "NO"
                detail = "Game designation: " + game.title()
            elif game not in ("", "-", "(-)", "NONE"):
                status = "UNKNOWN"
                detail = "Unrecognised game designation"
            elif latest in ("DNP", "LP"):
                status = "NO"
                detail = "Latest practice: " + latest
            elif latest == "FP":
                status = "YES"
                detail = "Full practice participation"
            else:
                status = "UNKNOWN"
                detail = "No confirmed participation information"

            return {
                "status": status,
                "injury": injury,
                "detail": detail,
                "practice": latest,
                "gameStatus": game,
                "reportDate": report_date,
            }

    raise ValueError("Lamar Jackson not found in a verified injury table")


def main():
    result = {
        "status": "UNKNOWN",
        "injury": None,
        "detail": "Unable to verify current injury information",
        "practice": None,
        "gameStatus": None,
        "reportDate": None,
    }

    try:
        result = get_status()
    except Exception as error:
        print("Injury report unavailable:", error)

    result["reason"] = result["detail"]
    result["source_url"] = SOURCE
    result["updated_at"] = datetime.now(timezone.utc).isoformat()
    result["source"] = SOURCE
    result["updatedAt"] = datetime.now(timezone.utc).isoformat()
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
