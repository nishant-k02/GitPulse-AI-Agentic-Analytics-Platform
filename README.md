# GitHub Agentic Analytics – Bonus Assignment 1

This project implements an **agentic, LLM-driven analytics system** over GitHub repository statistics stored in **PostgreSQL**.  
You can:

- Fetch GitHub data and store it as CSVs.
- Load the data into a relational schema in Postgres.
- Ask **natural-language questions** in a **Streamlit** UI.
- Let a **LangGraph + gpt-4o-mini agent** dynamically generate Python + SQL, run it in a **Python REPL**, and return:
  - Text / tabular outputs (markdown tables)
  - Visualizations (Matplotlib, Prophet, Statsmodels) when requested.

> All paths and commands below are written relative to this `src/` directory.

---

### Note: Missing dependency in requirements.txt file

- Install it inside your venv after running requirements.txt file:

    - tabulate

        `pip install tabulate`

    - Ensure you have the modern `prophet` package:

        `pip uninstall -y fbprophet prophet`

        `pip install prophet`

---

## 0. Project Structure

```text
src/
├── agentic
│   ├── tools.py              # Helper tools for SQL → Polars and other utilities
│   └── workflow.py           # LangGraph workflow + Python REPL executor
├── data
│   ├── processed             # (optional) for any derived data
│   └── raw                   # CSVs generated from GitHub
│       ├── commits.csv
│       ├── issues.csv
│       ├── pulls.csv
│       └── repos.csv
├── db
│   ├── connection.py         # Postgres connection helper
│   └── schema.sql            # DDL for repos / issues / pulls / commits tables
├── github_pipeline
│   ├── fetch_github_data.py  # Fetch data from GitHub API and write CSVs
│   └── load_to_postgres.py   # Create tables + load CSVs into Postgres
├── streamlit_app
│   └── app.py                # Streamlit UI for the agentic analytics app
├── .gitignore
├── README.md                 
└── requirements.txt          # Python dependencies

```
## 1. Prerequisites
### 1.1 Software

- Python: 3.11 is recommended (3.10 also works; used during development).
- PostgreSQL: 14+ (tested with 16 via Homebrew on macOS).
- Git: any recent version.
- A modern browser: Chrome, Safari.

### 1.2 Accounts & API Keys

- GitHub Personal Access Token (PAT)
    - Required if you want to re-fetch data from GitHub (rather than using the provided CSVs). (inside config.py line no: 18)
    - from terminal:

        `export OPENAI_API_KEY="sk-..."`         # required
- OpenAI API key
    - Required to run the agentic workflow using gpt-4o-mini. (inside config.py line no: 26)
    - from terminal:
      
        `export GITHUB_TOKEN="github_pat_..."`   # optional but recommended for re-fetching

## 2. Python Environment Setup
All commands below assume you are inside the project root that contains `src`:
`cd /path/to/Bonus Assignment 1`

### 2.1. Create and activate a virtual environment

- Create venv:
  
    `python3.11 -m venv venv`
- Activate it:
  
    `source venv/bin/activate` # macOS / Linux

    `.\venv\Scripts\activate `   # Windows PowerShell / CMD
  
You should now see (venv) at the start of your shell prompt.

### 2.2. Install Python packages
- From the project root (same level as `src/`):

    `cd src`
    
    `pip install --upgrade pip`
    
    `pip install -r requirements.txt`

## 3. PostgreSQL Setup

### 3.1. Install and start Postgres (macOS via Homebrew)

    `brew install postgresql@16`
    `brew services start postgresql@16`

### 3.2 Create database and user

- Open `psql`:

    `psql postgres`

- Run the following SQL:

    `CREATE ROLE bonus_user WITH LOGIN PASSWORD 'bonus_pass';`

    `CREATE DATABASE bonus_db OWNER bonus_user;`

    `GRANT ALL PRIVILEGES ON DATABASE bonus_db TO bonus_user;`
    
    `\q`

## 4. Data Pipeline: From GitHub → CSV → Postgres

- If you want to refetch the data from the repos:

    `python -m github_pipeline.fetch_github_data`

### 4.1. Load CSVs into Postgres

 -  To store the data of csv into the postgres db:

    `python -m github_pipeline.load_to_postgres`

## 5. Running the Streamlit App

- Run the below command to excecute the application:

    `streamlit run src/streamlit_app/app.py`

- See the output at below url:

    `Local URL: http://localhost:8501`
    `Network URL: http://192.168.x.x:8501`
