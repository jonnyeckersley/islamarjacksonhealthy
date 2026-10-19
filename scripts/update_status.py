
import json
import re
from datetime import datetime, timezone
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
            }

    raise ValueError("Lamar Jackson not found in a verified injury table")


def main():
    result = {
        "status": "UNKNOWN",
        "injury": None,
        "detail": "Unable to verify current injury information",
        "practice": None,
        "gameStatus": None,
    }

    try:
        result = get_status()
    except Exception as error:
        print("Injury report unavailable:", error)

    result["source"] = SOURCE
    result["updatedAt"] = datetime.now(timezone.utc).isoformat()
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
