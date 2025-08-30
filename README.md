# Syllabooster — Flask + SQLite (Hebrew RTL)

A lightweight Flask web app with a modern, fully right-to-left (RTL) Hebrew UI. It shows a server-rendered **Home** page and six data tabs that load from a SQLite database and render as responsive cards with a collapse for details.

## Features

- **Backend:** Python 3.10+, Flask, SQLite3, Jinja2
- **Frontend:** Bootstrap 5 **RTL** (CDN), Bootstrap Icons (CDN), Heebo font (Google Fonts), Vanilla JS
- **UX:** Clean, mobile-first layout with a side nav on desktop and a bottom tab bar on mobile
- **Accessibility:** Proper landmarks/roles, `aria-*` attributes, focus visibility, and `dir="auto"` for mixed LTR/RTL text

## Project layout (key files)

- `schema.sql` — Database schema (tables for categories, settings, home items, and the six tab tables)
- `seed.sql` — Seed data (includes clearly marked `-- ******** <table> ********` blocks for each tab)
- `update-db.py` — Utility to replace a single tab’s seed data from a CSV and rebuild the DB
- `templates/base.html` — Bootstrap RTL, Icons, Heebo, and a Toast area for load errors
- `templates/index.html` — Main UI: side/bottom navigation, server-rendered Home, and JS that fetches tab data
- `static/style.css` — Minor visual polish and RTL tweaks
- `requirements.txt` — Python dependencies

## Quick start

1) Create and activate a virtualenv
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```
2.	Install dependencies
```bash
pip install -r requirements.txt
```
3.	Initialize the SQLite database
```bash
# Create app.db from schema + seed (requires sqlite3 CLI on PATH)
sqlite3 app.db < schema.sql
sqlite3 app.db < seed.sql
```
4.	Run the app (choose whichever fits your setup)
```bash
# Option A: direct
python app.py
```

```bash
# Option B: Flask runner
export FLASK_APP=app
flask run
```
	5.	Open in your browser
http://127.0.0.1:5000

API
	•	GET /api/<tab> where <tab> is one of:
	•	docs, tasks, notes, alerts, links, hs
(Home is server-rendered; only the six tabs load via API.)
	•	Returns a JSON array of rows. The allow_valenteres field is returned as a real boolean (true/false).

Example:
```bash
curl -s http://127.0.0.1:5000/api/docs | jq .
```

Frontend behavior (templates/index.html)
	•	Desktop: a vertical side nav (pills) with one link per tab
	•	Mobile: a fixed bottom tab bar
	•	The Home section is server-rendered. Other tabs toggle a list section and fetch their data from /api/<tab>.
	•	Each row renders as a card with:
	•	Title (course_name)
	•	Subtitle (teacher_name)
	•	Optional category badge
	•	A button to expand a details panel (intended_for, course_info, requirments, volunteering info, etc.)

----

Using update-db.py (CSV → seed.sql → app.db)

This helper replaces the seed data for one tab (e.g., docs) from a CSV, updates seed.sql in the correct block, and (by default) rebuilds app.db from schema.sql + seed.sql.

Basic usage
```bash
python3 update-db.py -f path/to/your-data.csv
```
- What happens:
You’ll be prompted to choose which tab to replace:
1. גן           -> table: docs
2. בית א׳-ב׳    -> table: tasks
3. בית ג׳-ד׳    -> table: notes
4. בית ה׳-ו׳    -> table: alerts
5. בית חט״ב     -> table: links
6. תיכון        -> table: highschool

- The script backs up app.db and seed.sql (timestamped copies in the project folder).
- It reads your CSV (UTF-8), normalizes headers (see below), and generates a fresh INSERT INTO <table>(...) VALUES ...; block.
- It locates the matching block in seed.sql by the marker line:

  -- ******** <table> ********

  and replaces only that block.

- Unless you pass --no-rebuild, it rebuilds app.db from schema.sql + seed.sql and prints a short preview of the new rows.

Flags
	•	-f, --file – path to CSV file (required)
	•	--db – path to SQLite DB (default: app.db)
	•	--schema – path to schema file (default: schema.sql)
	•	--seed – path to seed file (default: seed.sql)
	•	--no-rebuild – update seed.sql only (skip DB rebuild)

Expected CSV header (canonical column names)

The DB schema uses these exact column names (including historical typos), and the CSV is expected to provide them (order doesn’t matter):
course_name,teacher_name,intended_for,course_info,requirments,category,allow_valenteres,valentieres_age,max_valetires,additional_info

	•	id is not part of the CSV; IDs are auto-generated.
	•	allow_valenteres is parsed as boolean; accepted truthy values:
1, true, yes, y, on, כן, נכון

Everything else is treated as 0 (false).

	•	max_valetires is an integer. Blank/non-numeric values become NULL.

Accepted header aliases (auto-mapping)

You may title your CSV columns with any of the following aliases; the script maps them to the canonical names above:
	•	course_name → course_name, corese_name, course, course title, שם קורס, שם שיעור
	•	teacher_name → teacher_name, teacher, מורה, שם מורה
	•	intended_for → intended_for, target, מיועד ל
	•	course_info → course_info, description, about, תיאור, מידע על הקורס
	•	requirments → requirments, requirements, דרישות
	•	category → category, קטגוריה
	•	allow_valenteres → allow_valenteres, allow_volunteers, מתנדבים
	•	valentieres_age → valentieres_age, volunteers_age, גיל מתנדבים
	•	max_valetires → max_valetires, max_volunteers, מקס מתנדבים, כמות מתנדבים מקס
	•	additional_info → additional_info, notes, מידע נוסף

Tip: Export as UTF-8 CSV (e.g., Excel’s “CSV UTF-8 (Comma delimited)”).

Categories handling
	•	The script reads existing categories from the categories table (if app.db exists).
	•	If a row’s category is blank or unknown, it is mapped to כללי and a summary is printed at the end.

Requirements
Flask==3.0.3
Jinja2==3.1.4
Werkzeug==3.0.3
itsdangerous==2.2.0
click==8.1.7

Notes
	•	The Bootstrap/Icons/Fonts are loaded via CDN without SRI; for production you may want to pin versions and/or self-host.
	•	Everything is UTF-8; CSVs should be UTF-8 (with BOM tolerated).



---
Using Docker

Yearly DB update workflow (using your update-db.py)
	1.	Run the script on your workstation to update seed.sql from the CSV (skip DB rebuild—Docker will do it):
```bash
python3 update-db.py -f 2025-GAN.csv --no-rebuild
```
	2. Rebuild the image
```bash
docker build -t syllabooster:local .
```
	3. Run the container locally
```bash
docker run --rm -p 8080:8080 \
  -e PORT=8080 \
  -e DB_PATH=/app/app.db \
  syllabooster:local
```
	4. Test
```bash
curl -s http://localhost:8080/ | head
curl -s http://localhost:8080/api/docs | head
```


Enjoy! 🙂
