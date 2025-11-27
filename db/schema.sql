CREATE TABLE IF NOT EXISTS repos (
    id SERIAL PRIMARY KEY,
    full_name TEXT UNIQUE,
    owner TEXT,
    name TEXT,
    stars INT,
    forks INT,
    open_issues INT,
    watchers INT,
    fetched_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS issues (
    id BIGINT PRIMARY KEY,
    repo_full_name TEXT,
    number INT,
    state TEXT,
    created_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    is_pull_request BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_issues_repo_created
    ON issues (repo_full_name, created_at);

CREATE TABLE IF NOT EXISTS pulls (
    id BIGINT PRIMARY KEY,
    repo_full_name TEXT,
    number INT,
    state TEXT,
    created_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    merged_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS commits (
    id SERIAL PRIMARY KEY,
    repo_full_name TEXT,
    sha TEXT,
    committed_at TIMESTAMPTZ
);
