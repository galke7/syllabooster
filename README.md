# סילאבוסטר — אפליקציית Flask + SQLite (RTL עברית)

אפליקציית ווב עם עיצוב מודרני ותמיכה מלאה ב-RTL עברית. 6 טאבים תחתיים (וגם נווט צד ב-desktop), כל אחד מציג רשימת פריטים מטבלה נפרדת ב-SQLite. פריטי הרשימה מוצגים ככרטיסי Bootstrap עם **כותרת** (corese_name), **כותרת משנה** (teacher_name) ופאנל מתמוטט לפרטים נוספים.

## טכנולוגיות
- Backend: Python 3.10+, Flask, SQLite3, Jinja2
- Frontend: Bootstrap 5 **RTL** (CDN), Bootstrap Icons (CDN), Vanilla JS
- UTF-8 בכל מקום

## התקנה והפעלה

1) צרו סביבת עבודה וירטואלית:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

	2.	התקינו תלויות:

pip install -r requirements.txt

	3.	צרו את מסד הנתונים וזרעו נתונים לדוגמה:

sqlite3 app.db < schema.sql
sqlite3 app.db < seed.sql

	4.	הריצו:

    # אפשרות א:
python app.py

# או אפשרות ב:
export FLASK_APP=app.py
flask run

	5.	פתחו את הדפדפן:

    http://127.0.0.1:5000

    נקודות API
	•	GET /api/<tab> כאשר <tab> אחד מהבאים: home, docs, tasks, notes, alerts, links
מחזיר מערך JSON של שורות. השדה allow_valenteres מוחזר כ-boolean אמיתי (true/false).

דוגמה:

curl -s http://127.0.0.1:5000/api/docs | jq .


קבצי הפרויקט
	•	app.py — שרת Flask, ראוטים, מטמון (TTL 60s), המרה ל-boolean, כותרות UTF-8.
	•	schema.sql — 8 טבלאות + טריגרים שמוודאים ש-category קיימת בטבלת categories.
	•	seed.sql — קטגוריות, רשומת הגדרות ראשית, ולפחות 5 שורות לכל אחת מ-6 הטבלאות.
	•	templates/base.html — Bootstrap RTL, Icons, Font Heebo, Toast לשגיאות.
	•	templates/index.html — מבנה ה-UI, נווט צד, תוכן בית, רשימות + renderList() מלא.
	•	static/style.css — טאצ׳ים עיצוביים עדינים ותמיכה ב-RTL.

נגישות
	•	שימוש בכפתורים אמיתיים לפתיחה/סגירה (Collapse) עם aria-expanded ו-aria-controls.
	•	מצב פוקוס נראה לעין (:focus-visible).
	•	dir="auto" בשדות טקסט כדי להתמודד עם עירוב RTL/LTR.

בעיות נפוצות
	•	ריק על המסך למרות 200 ל-/api/ — ודאו שהטמעתם את ה-renderList(rows) (נמצא ב-templates/index.html). בקוד כאן זה כבר כלול.
	•	שגיאת קטגוריה בהכנסה ידנית ל-DB — הטריגרים דוחים category שלא קיימת ב-categories.name.

בהצלחה! 🙂