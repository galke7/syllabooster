PRAGMA foreign_keys = ON;

-- Categories
CREATE TABLE IF NOT EXISTS categories (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS main_settings (
  id INTEGER PRIMARY KEY,
  tab_home  TEXT NOT NULL,
  tab_docs  TEXT NOT NULL,
  tab_tasks TEXT NOT NULL,
  tab_notes TEXT NOT NULL,
  tab_alerts TEXT NOT NULL,
  tab_links TEXT NOT NULL,
  tab_highschool TEXT NOT NULL,
  home_title TEXT,
  home_description TEXT
);

-- home_items
CREATE TABLE IF NOT EXISTS home_items (
  id INTEGER PRIMARY KEY,
  course_name TEXT NOT NULL,
  teacher_name TEXT NOT NULL,
  intended_for TEXT NOT NULL,
  course_info TEXT,
  requirments TEXT,
  category TEXT,
  allow_valenteres INTEGER NOT NULL,
  valentieres_age TEXT,
  max_valetires INTEGER,
  additional_info TEXT
);

-- docs
CREATE TABLE IF NOT EXISTS docs (
  id INTEGER PRIMARY KEY,
  course_name TEXT NOT NULL,
  teacher_name TEXT NOT NULL,
  intended_for TEXT NOT NULL,
  course_info TEXT,
  requirments TEXT,
  category TEXT,
  allow_valenteres INTEGER NOT NULL,
  valentieres_age TEXT,
  max_valetires INTEGER,
  additional_info TEXT
);

-- tasks
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY,
  course_name TEXT NOT NULL,
  teacher_name TEXT NOT NULL,
  intended_for TEXT NOT NULL,
  course_info TEXT,
  requirments TEXT,
  category TEXT,
  allow_valenteres INTEGER NOT NULL,
  valentieres_age TEXT,
  max_valetires INTEGER,
  additional_info TEXT
);

-- notes
CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY,
  course_name TEXT NOT NULL,
  teacher_name TEXT NOT NULL,
  intended_for TEXT NOT NULL,
  course_info TEXT,
  requirments TEXT,
  category TEXT,
  allow_valenteres INTEGER NOT NULL,
  valentieres_age TEXT,
  max_valetires INTEGER,
  additional_info TEXT
);

-- alerts
CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY,
  course_name TEXT NOT NULL,
  teacher_name TEXT NOT NULL,
  intended_for TEXT NOT NULL,
  course_info TEXT,
  requirments TEXT,
  category TEXT,
  allow_valenteres INTEGER NOT NULL,
  valentieres_age TEXT,
  max_valetires INTEGER,
  additional_info TEXT
);

-- links
CREATE TABLE IF NOT EXISTS links (
  id INTEGER PRIMARY KEY,
  course_name TEXT NOT NULL,
  teacher_name TEXT NOT NULL,
  intended_for TEXT NOT NULL,
  course_info TEXT,
  requirments TEXT,
  category TEXT,
  allow_valenteres INTEGER NOT NULL,
  valentieres_age TEXT,
  max_valetires INTEGER,
  additional_info TEXT
);

-- highschool
CREATE TABLE IF NOT EXISTS highschool (
  id INTEGER PRIMARY KEY,
  course_name TEXT NOT NULL,
  teacher_name TEXT NOT NULL,
  intended_for TEXT NOT NULL,
  course_info TEXT,
  requirments TEXT,
  category TEXT,
  allow_valenteres INTEGER NOT NULL,
  valentieres_age TEXT,
  max_valetires INTEGER,
  additional_info TEXT
);

-- Triggers to enforce that category value exists in categories.name
-- For each table: BEFORE INSERT/UPDATE validate NEW.category against categories
-- home_items
CREATE TRIGGER IF NOT EXISTS trg_home_items_validate_category_insert
BEFORE INSERT ON home_items
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for home_items');
END;

CREATE TRIGGER IF NOT EXISTS trg_home_items_validate_category_update
BEFORE UPDATE ON home_items
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for home_items');
END;

-- docs
CREATE TRIGGER IF NOT EXISTS trg_docs_validate_category_insert
BEFORE INSERT ON docs
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for docs');
END;

CREATE TRIGGER IF NOT EXISTS trg_docs_validate_category_update
BEFORE UPDATE ON docs
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for docs');
END;

-- tasks
CREATE TRIGGER IF NOT EXISTS trg_tasks_validate_category_insert
BEFORE INSERT ON tasks
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for tasks');
END;

CREATE TRIGGER IF NOT EXISTS trg_tasks_validate_category_update
BEFORE UPDATE ON tasks
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for tasks');
END;

-- notes
CREATE TRIGGER IF NOT EXISTS trg_notes_validate_category_insert
BEFORE INSERT ON notes
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for notes');
END;

CREATE TRIGGER IF NOT EXISTS trg_notes_validate_category_update
BEFORE UPDATE ON notes
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for notes');
END;

-- alerts
CREATE TRIGGER IF NOT EXISTS trg_alerts_validate_category_insert
BEFORE INSERT ON alerts
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for alerts');
END;

CREATE TRIGGER IF NOT EXISTS trg_alerts_validate_category_update
BEFORE UPDATE ON alerts
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for alerts');
END;

-- links
CREATE TRIGGER IF NOT EXISTS trg_links_validate_category_insert
BEFORE INSERT ON links
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for links');
END;

CREATE TRIGGER IF NOT EXISTS trg_links_validate_category_update
BEFORE UPDATE ON links
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for links');
END;

CREATE TRIGGER IF NOT EXISTS trg_highschool_validate_category_insert
BEFORE INSERT ON highschool
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for highschool');
END;

CREATE TRIGGER IF NOT EXISTS trg_highschool_validate_category_update
BEFORE UPDATE ON highschool
FOR EACH ROW
WHEN NEW.category IS NOT NULL AND NOT EXISTS (SELECT 1 FROM categories c WHERE c.name = NEW.category)
BEGIN
  SELECT RAISE(ABORT, 'Invalid category for highschool');
END;