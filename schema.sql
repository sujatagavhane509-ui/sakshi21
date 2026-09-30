-- Reference schema (SQLAlchemy creates these tables automatically on startup).
CREATE TABLE users (
  id            INTEGER PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  email         VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at    TIMESTAMP NOT NULL
);

CREATE TABLE financial_records (
  id                    INTEGER PRIMARY KEY,
  user_id               INTEGER NOT NULL REFERENCES users(id),
  credit_score          INTEGER NOT NULL CHECK (credit_score BETWEEN 300 AND 900),
  monthly_income        REAL NOT NULL,
  monthly_expenses      REAL NOT NULL,
  monthly_debt_payments REAL NOT NULL,
  credit_limit          REAL NOT NULL,
  credit_used           REAL NOT NULL,
  missed_payments       INTEGER NOT NULL DEFAULT 0,
  debt_to_income        REAL NOT NULL,
  utilization           REAL NOT NULL,
  created_at            TIMESTAMP NOT NULL
);
CREATE INDEX ix_records_user ON financial_records(user_id);

-- Example: score history for one user (feeds the dashboard line chart)
-- SELECT created_at, credit_score FROM financial_records WHERE user_id = 1 ORDER BY created_at;
