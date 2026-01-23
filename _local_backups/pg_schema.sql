CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    owner_user_id BIGINT NOT NULL,
    code_name TEXT NOT NULL,
    case_number TEXT,
    court TEXT,
    judge TEXT,
    fin_manager TEXT,
    stage TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cases_owner ON cases(owner_user_id);

CREATE TABLE IF NOT EXISTS profiles (
    owner_user_id BIGINT PRIMARY KEY,
    full_name TEXT,
    role TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS case_cards (
    case_id INTEGER NOT NULL,
    owner_user_id BIGINT NOT NULL,
    data TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    court_name TEXT,
    court_address TEXT,
    judge_name TEXT,
    debtor_full_name TEXT,
    PRIMARY KEY (case_id, owner_user_id),
    CONSTRAINT fk_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE
);
