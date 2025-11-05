CREATE TABLE IF NOT EXISTS contractors (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE,
  ticker TEXT UNIQUE,
  sector TEXT
);

CREATE TABLE IF NOT EXISTS stock_prices (
  id INTEGER PRIMARY KEY,
  contractor_id INTEGER,
  date TEXT,
  open REAL, close REAL, high REAL, low REAL, volume REAL,
  UNIQUE(contractor_id, date)
);

CREATE TABLE IF NOT EXISTS workforce (
  id INTEGER PRIMARY KEY,
  series_id TEXT,           -- BLS series (e.g., CEU9091000001)
  date TEXT,                -- YYYY-MM-DD
  value REAL,
  UNIQUE(series_id, date)
);

CREATE TABLE IF NOT EXISTS agency_budgets (
  id INTEGER PRIMARY KEY,
  toptier_code TEXT,
  agency_name TEXT,
  fiscal_year INTEGER,
  outlay_amount REAL,
  obligated_amount REAL,
  UNIQUE(toptier_code, fiscal_year)
);
