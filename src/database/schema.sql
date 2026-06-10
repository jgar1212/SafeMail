CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_text TEXT,
    prediction TEXT,
    risk_score REAL,
    scan_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
