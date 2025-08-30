Syllabooster — Flask + SQLite (Hebrew RTL)

A lightweight Flask web app with a modern, fully right-to-left (RTL) Hebrew UI. It shows a server-rendered Home page and six data tabs that load from a SQLite database and render as responsive cards with a collapse for details.

Features
	•	Backend: Python 3.10+, Flask, SQLite3, Jinja2
	•	Frontend: Bootstrap 5 RTL (CDN), Bootstrap Icons (CDN), Heebo font (Google Fonts), Vanilla JS
	•	UX: Clean, mobile-first layout with a side nav on desktop and a bottom tab bar on mobile
	•	Accessibility: Proper landmarks/roles, aria-* attributes, focus visibility, and dir="auto" for mixed LTR/RTL text

⸻

Project layout (key files)
	•	schema.sql — Database schema (tables for categories, settings, home items, and the six tab tables)
	•	seed.sql — Seed data (includes clearly marked -- ******** <table> ******** blocks for each tab)
	•	update-db.py — Utility to replace a single tab’s seed data from a CSV and rebuild the DB
	•	templates/base.html — Bootstrap RTL, Icons, Heebo, and a Toast area for load errors
	•	templates/index.html — Main UI: side/bottom navigation, server-rendered Home, and JS that fetches tab data
	•	static/style.css — Minor visual polish and RTL tweaks
	•	requirements.txt — Python dependencies

⸻

Quick start (local)
	1.	Create and activate a virtualenv

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

	2.	Install dependencies

pip install -r requirements.txt

	3.	Initialize the SQLite database

# Create app.db from schema + seed (requires sqlite3 CLI on PATH)
sqlite3 app/app.db < schema.sql
sqlite3 app/app.db < seed.sql

	4.	Run the app

export FLASK_APP=app
export DB_PATH="$(pwd)/app/app.db"
flask run

	5.	Open in your browser
http://127.0.0.1:5000

⸻

API
	•	GET /api/<tab> where <tab> is one of:
docs, tasks, notes, alerts, links, hs
(Home is server-rendered; only the six tabs load via API.)
	•	Returns a JSON array of rows. The allow_valenteres field is returned as a real boolean (true/false).

Example:

curl -s http://127.0.0.1:5000/api/docs | jq .


⸻

Frontend behavior (templates/index.html)
	•	Desktop: a vertical side nav (pills) with one link per tab
	•	Mobile: a fixed bottom tab bar
	•	The Home section is server-rendered. Other tabs toggle a list section and fetch their data from /api/<tab>.
	•	Each row renders as a card with:
	•	Title (course_name)
	•	Subtitle (teacher_name)
	•	Optional category badge
	•	A button to expand a details panel (intended_for, course_info, requirments, volunteering info, etc.)

⸻

Using update-db.py (CSV → seed.sql → app.db)

This helper replaces the seed data for one tab (e.g., docs) from a CSV, updates seed.sql in the correct block, and (by default) rebuilds app.db from schema.sql + seed.sql.

Basic usage

python3 update-db.py -f path/to/your-data.csv

	•	You’ll be prompted to choose which tab to replace:
	1.	גן           -> table: docs
	2.	בית א׳-ב׳    -> table: tasks
	3.	בית ג׳-ד׳    -> table: notes
	4.	בית ה׳-ו׳    -> table: alerts
	5.	בית חט״ב     -> table: links
	6.	תיכון        -> table: highschool
	•	The script backs up app.db and seed.sql (timestamped copies in the project folder).
	•	It reads your CSV (UTF-8), normalizes headers (see below), and generates a fresh:

INSERT INTO <table>(...) VALUES (...), (...), ...;


	•	It locates the matching block in seed.sql by the marker line:

-- ******** <table> ********

and replaces only that block.

	•	Unless you pass --no-rebuild, it rebuilds app.db from schema.sql + seed.sql and prints a short preview.

Flags

-f, --file      path to CSV file (required)
--db            path to SQLite DB (default: app.db)
--schema        path to schema file (default: schema.sql)
--seed          path to seed file (default: seed.sql)
--no-rebuild    update seed.sql only (skip DB rebuild)

Expected CSV header (canonical column names)

The DB schema uses these exact names (including historical typos); the CSV should provide them (order doesn’t matter):

course_name,teacher_name,intended_for,course_info,requirments,category,allow_valenteres,valentieres_age,max_valetires,additional_info

	•	id is not part of the CSV; IDs are auto-generated.
	•	allow_valenteres is parsed as boolean; accepted truthy values: 1, true, yes, y, on, כן, נכון
Everything else is treated as 0 (false).
	•	max_valetires is an integer. Blank/non-numeric values become NULL.

Accepted header aliases (auto-mapping)
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

⸻

Requirements (Python)

Flask==3.0.3
Jinja2==3.1.4
Werkzeug==3.0.3
itsdangerous==2.2.0
click==8.1.7

Notes
	•	Bootstrap/Icons/Fonts are loaded via CDN without SRI; for production you may want to pin versions and/or self-host.
	•	Everything is UTF-8; CSVs should be UTF-8 (BOM tolerated).

⸻

Using Docker (local)

Yearly DB update workflow (using your update-db.py)
	1.	Update seed.sql from CSV (skip local DB rebuild—Docker will do it):

python3 update-db.py -f 2025-GAN.csv --no-rebuild

	2.	Build the image

docker build -t syllabooster:local .

	3.	Run the container locally

docker run --rm -p 8080:8080 \
  -e PORT=8080 \
  -e DB_PATH=/app/app.db \
  syllabooster:local

	4.	Test

curl -s http://localhost:8080/ | head
curl -s http://localhost:8080/api/docs | head


⸻

Deploying to Cloud Run (bundled, read-only SQLite)

This app is containerized and runs great on Cloud Run with a bundled, read-only SQLite DB.

Prerequisites
	•	Google Cloud project + owner/editor access
	•	Artifact Registry & Cloud Run APIs enabled
	•	gcloud CLI authenticated
	•	(Optional) Domain you control (for custom domain), hosted in Cloud DNS

1) Build and push the image

# Set once per shell
PROJECT_ID="YOUR_PROJECT_ID"
REGION="us-central1"                     # choose a supported Cloud Run region
REPO="syllabooster"                      # Artifact Registry repo name
TAG="$(date +%Y%m%d-%H%M%S)"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/syllabooster:${TAG}"

# (One-time) create repo
gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Syllabooster containers"

# Auth Docker to Artifact Registry
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q

# Build (Apple Silicon: force linux/amd64)
docker buildx build --platform linux/amd64 -t "$IMAGE" .

# Push
docker push "$IMAGE"

2) Deploy (standard “no-canary”)

SERVICE="syllabooster"

gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars DB_PATH=/app/app.db

# Route 100% traffic to the latest revision
gcloud run services update-traffic "$SERVICE" --region "$REGION" --to-latest

Cost guardrails

# Keep it cheap in dev: at most 3 instances; scales to zero when idle
gcloud run services update "$SERVICE" --region "$REGION" \
  --max-instances 3 --min-instances 0 --concurrency 80


⸻

Canary releases with tags (recommended)

This flow gives you a tag URL for testing before shifting user traffic. It also avoids the common “latestReady race”.

Deterministic tag URL:
https://<TAG>---<SERVICE>-<PROJECT_NUMBER>.<REGION>.run.app
Example for tag canary: https://canary---syllabooster-<PN>.us-central1.run.app

A) Deploy without traffic, then tag and test

# 1) Deploy with no traffic (creates a new revision)
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars DB_PATH=/app/app.db \
  --no-traffic

# 2) Get the latest *created* revision (avoids Ready race)
REV_CREATED="$(gcloud run services describe "$SERVICE" --region "$REGION" \
  --format='value(status.latestCreatedRevisionName)')"
echo "Latest created revision: $REV_CREATED"

# 3) Attach the canary tag to that revision (no traffic change)
gcloud run services update-traffic "$SERVICE" --region "$REGION" \
  --set-tags canary="$REV_CREATED"

# 4) Build and hit the tag URL
PN="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
TAG_URL="https://canary---${SERVICE}-${PN}.${REGION}.run.app"
echo "$TAG_URL"
curl -sS "$TAG_URL/health"

Why this works: revisions at 0% traffic may sit non-Ready until there’s a traffic path (a tag URL or % of traffic). Hitting the tag URL “activates” the revision.

B) Gradually shift traffic to the canary

# send 10% to the tagged canary
gcloud run services update-traffic "$SERVICE" --region "$REGION" \
  --to-tags canary=10

# promote to 100% when satisfied
gcloud run services update-traffic "$SERVICE" --region "$REGION" \
  --to-tags canary=100

# (optional) remove the tag afterwards
gcloud run services update-traffic "$SERVICE" --region "$REGION" \
  --remove-tags canary

C) Tag during deploy (one-liner variant)

# You can create/refresh the canary tag at deploy time
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars DB_PATH=/app/app.db \
  --tag canary \
  --no-traffic


⸻

Verify & debug deployments

Where is traffic going?

gcloud run services describe "$SERVICE" --region "$REGION" \
  --format='yaml(status.url,status.traffic,status.latestReadyRevisionName)'

List revisions, tags, readiness & digests

gcloud run revisions list --service "$SERVICE" --region "$REGION" \
  --format='table(name, tags, trafficPercent, status.conditions[?type="Ready"].status, status.imageDigest, createTime)'

Explain a stuck revision

gcloud run revisions describe "$REV_CREATED" --region "$REGION" \
  --format='table(status.conditions[].type,status.conditions[].status,status.conditions[].message)'

Recent logs for a specific revision

gcloud logs read --region "$REGION" \
  'resource.type="cloud_run_revision"
   resource.labels.service_name="'"$SERVICE"'"
   labels."run.googleapis.com/revision_name"="'"$REV_CREATED"'"' \
  --limit 100 --freshness=2h


⸻

Force a fresh image (avoid cache) & identify builds

# Force rebuild and push
docker buildx build --platform linux/amd64 -t "$IMAGE" --push --no-cache --pull .

# OR embed a build id you can display on /health or /__version
docker buildx build --platform linux/amd64 \
  --build-arg BUILD_ID="$(date -u +%Y%m%d-%H%M%S)" \
  -t "$IMAGE" --push .


⸻

Custom domain (Cloud Run Domain Mapping + Cloud DNS)

(Optional) Map a subdomain without a load balancer / static IP
	1.	Verify the base domain (one-time)

gcloud domains list-user-verified
# If needed
gcloud domains verify yourdomain.com

	2.	Create the domain mapping

APP_HOST="app.yourdomain.com"

gcloud beta run domain-mappings create \
  --region "$REGION" \
  --service "$SERVICE" \
  --domain "$APP_HOST"

	3.	Add the DNS record (Cloud DNS)

ZONE="your-cloud-dns-zone-name"          # zone that serves yourdomain.com
FQDN="${APP_HOST}."
TARGET="ghs.googlehosted.com."

# Ensure no conflicting records exist
gcloud dns record-sets list --zone="$ZONE" --name="$FQDN"

# Add the CNAME
gcloud dns record-sets transaction start --zone="$ZONE"
gcloud dns record-sets transaction add \
  --zone="$ZONE" --name="$FQDN" --type=CNAME --ttl=300 "$TARGET"
gcloud dns record-sets transaction execute --zone="$ZONE"

	4.	Verify DNS & certificate

# DNS
dig +short CNAME "$FQDN"
dig +short "$FQDN"

# Domain mapping & managed cert
gcloud beta run domain-mappings describe \
  --region "$REGION" \
  --domain "$APP_HOST" \
  --format='yaml(status,resourceRecords)'

# Test HTTPS
curl -I "https://${APP_HOST}/health"


⸻

Yearly DB refresh in production
	•	Update seed.sql from your CSV:

python3 update-db.py -f path/to/data.csv --no-rebuild

	•	Rebuild & push a new image, then canary or to-latest as above.
	•	The Docker build regenerates /app/app.db from schema.sql + seed.sql.

⸻

Troubleshooting
	•	500 on Cloud Run → ensure:
	•	DB_PATH=/app/app.db is set
	•	Code opens SQLite in read-only mode (mode=ro&immutable=1) when running on Cloud Run
	•	Revision never Ready at 0% → tag it and hit the tag URL (curl) to activate, or send a small % of traffic.
	•	Old revision serving traffic → gcloud run services update-traffic "$SERVICE" --region "$REGION" --to-latest
	•	DNS not working → check dig, ensure the CNAME exists and no conflicting records at that name.

⸻

Enjoy! 🚀