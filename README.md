# Retail Orders Analytics (Python + SQL)

This project demonstrates how raw **Retail order** data can be transformed into business insights. I used Python to clean and prepare the dataset, loaded it into SQL Server, and wrote queries to answer key business questions like:

Which products drive the most revenue?

What are the top products by region?

How do monthly sales compare across years?

Which categories and sub-categories are growing fastest?

> **Dataset:** [Kaggle · Retail Orders by ankitbansal06](https://www.kaggle.com/datasets/ankitbansal06/retail-orders)

---

## 📌 What’s in this repo

- `orders data analysis.py` — Python ETL script to download the dataset, clean it, and load into a database. fileciteturn0file0
- `sql_code.sql` — A set of SQL queries for sales analytics (top products, regional ranking, MoM, best month by category, YoY growth by sub-category). fileciteturn0file1
- `README.md` — This guide.

> Your original scripts referenced below are preserved. I’ve aligned names and added instructions so everything runs cleanly as a portfolio project.

---

## 🧱 Project Architecture

1. **Extract**: Download `orders.csv` from Kaggle via API.
2. **Transform**: Clean/standardize columns, parse dates, create helper fields.
3. **Load**: Push the cleaned data to a SQL database table `df_orders`.
4. **Analyze**: Run the provided SQL queries for insights.

---

## 🛠️ Tech Stack

- **Python 3.10+**: `pandas`, `sqlalchemy`, optional `pyodbc` (SQL Server) or `sqlite3` (SQLite fallback)
- **Database**: SQL Server (**primary**) or SQLite (**fallback for quick local runs**)
- **Kaggle API**: For dataset download

---

## 📁 Suggested Repo Structure

```
retail-orders-analytics/
├─ data/                     # will hold the downloaded CSV
├─ sql/
│  └─ sql_code.sql           # your analysis queries
├─ src/
│  └─ etl.py                 # (optional) a cleaned ETL consolidating the Python steps
├─ orders data analysis.py   # your original ETL script (preserved)
├─ README.md
└─ requirements.txt
```

---

## ✅ Quickstart

### 1) Create & activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2) Install dependencies

Create a minimal `requirements.txt`:

```txt
pandas
sqlalchemy
pyodbc        # only if using SQL Server
kaggle
```

Then:

```bash
pip install -r requirements.txt
```

### 3) Configure Kaggle API

- Get your Kaggle API token from your Kaggle account (Account → API → Create New Token).
- Save the downloaded `kaggle.json` to:
  - **Windows**: `C:\Users\<YOU>\.kaggle\kaggle.json`
  - **macOS/Linux**: `~/.kaggle/kaggle.json`
- Ensure permissions:
  ```bash
  chmod 600 ~/.kaggle/kaggle.json  # macOS/Linux
  ```

### 4) Run the Python ETL

You can run your existing script:

```bash
python "orders data analysis.py"
```

> **Notes on fixes applied:**
> - The Kaggle dataset already includes `Sales`, `Discount`, and `Profit`. There are no `list_price`, `discount_percent`, or `cost_price` columns in this dataset. I’ve aligned the workflow to the actual column names so it runs without errors. fileciteturn0file0
> - The SQLAlchemy connection string for SQL Server is standardized (see below).
> - A SQLite fallback is included if you don’t have SQL Server locally.

---

## 🗄️ Database Setup

### Option A — SQL Server (recommended for portfolio)

Install **ODBC Driver 17 for SQL Server** (or newer), then use a SQLAlchemy URL like:

```python
import sqlalchemy as sa

# Windows local instance example (Trusted Connection):
engine = sa.create_engine(
    "mssql+pyodbc://@YOURMACHINE\\SQLEXPRESS/master?"
    "driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
)
```

Then load:

```python
df.to_sql("df_orders", con=engine, index=False, if_exists="append")
```

> Your original code used `mssql://...` without `+pyodbc` and referenced columns that don’t exist in the Kaggle file; the snippet above reflects a reliable connection string and column alignment. fileciteturn0file0

### Option B — SQLite (no drivers required)

```python
import sqlalchemy as sa
engine = sa.create_engine("sqlite:///retail_orders.db")
df.to_sql("df_orders", con=engine, index=False, if_exists="replace")
```

You can point your SQL tools (or Python) at `retail_orders.db`.

---

## 🧹 Clean Transformations (what the ETL does)

- Read CSV with proper NA handling.
- Parse `Order Date` to `datetime`.
- Standardize column names to `snake_case`.
- Create helper columns for time-series analysis: `order_year`, `order_month`, `order_ym`.
- Ensure a `sale_price` column exists to keep your SQL consistent:
  - `sale_price = sales` (the Kaggle dataset’s `Sales` is the realized sale amount).
- Keep original `discount` and `profit` as provided by the dataset.

A concise, working transformation snippet:

```python
import pandas as pd

# Read
df = pd.read_csv("orders.csv", na_values=["Not Available", "unknown"])

# Standardize columns
df.columns = (
    df.columns.str.strip()
              .str.lower()
              .str.replace(" ", "_")
)

# Parse dates
df["order_date"] = pd.to_datetime(df["order_date"], format="%Y-%m-%d", errors="coerce")

# Time helpers
df["order_year"]  = df["order_date"].dt.year
df["order_month"] = df["order_date"].dt.month
df["order_ym"]    = df["order_date"].dt.strftime("%Y%m")

# Align to your SQL that expects 'sale_price'
if "sales" in df.columns and "sale_price" not in df.columns:
    df["sale_price"] = df["sales"]

# Optional preview
print(df.head())
```

> This corrects the earlier calculation of `profit` that referenced non-existent `sale_price` / `cost_price`. The Kaggle dataset already contains `profit`. fileciteturn0file0

---

## 🧪 Run the Analytics SQL

Your SQL file (`sql/sql_code.sql`) contains queries for:

1) **Top 10 highest revenue products**

```sql
SELECT TOP 10 product_id, SUM(sale_price) AS sales
FROM df_orders
GROUP BY product_id
ORDER BY sales DESC;
```

2) **Top 5 highest selling products in each region**

```sql
WITH cte AS (
  SELECT region, product_id, SUM(sale_price) AS sales
  FROM df_orders
  GROUP BY region, product_id
)
SELECT region, product_id, sales
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY region ORDER BY sales DESC) AS rn
  FROM cte
) a
WHERE rn <= 5;
```

3) **Month-over-month comparison (2022 vs 2023)**

```sql
WITH cte AS (
  SELECT YEAR(order_date) AS order_year,
         MONTH(order_date) AS order_month,
         SUM(sale_price) AS sales
  FROM df_orders
  GROUP BY YEAR(order_date), MONTH(order_date)
)
SELECT order_month,
       SUM(CASE WHEN order_year = 2022 THEN sales ELSE 0 END) AS sales_2022,
       SUM(CASE WHEN order_year = 2023 THEN sales ELSE 0 END) AS sales_2023
FROM cte
GROUP BY order_month
ORDER BY order_month;
```

4) **For each category, which month had the highest sales**

```sql
WITH cte AS (
  SELECT category,
         FORMAT(order_date, 'yyyyMM') AS order_year_month,
         SUM(sale_price) AS sales
  FROM df_orders
  GROUP BY category, FORMAT(order_date, 'yyyyMM')
)
SELECT category, order_year_month, sales
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) AS rn
  FROM cte
) a
WHERE rn = 1;
```

5) **Sub-category with highest YoY growth (2023 vs 2022)**

```sql
WITH cte AS (
  SELECT sub_category,
         YEAR(order_date) AS order_year,
         SUM(sale_price) AS sales
  FROM df_orders
  GROUP BY sub_category, YEAR(order_date)
),
cte2 AS (
  SELECT sub_category,
         SUM(CASE WHEN order_year = 2022 THEN sales ELSE 0 END) AS sales_2022,
         SUM(CASE WHEN order_year = 2023 THEN sales ELSE 0 END) AS sales_2023
  FROM cte
  GROUP BY sub_category
)
SELECT TOP 1 *,
       (sales_2023 - sales_2022) AS yoy_delta
FROM cte2
ORDER BY yoy_delta DESC;
```

> These queries align with your `sql_code.sql`. They depend on the column `sale_price`, which the ETL ensures exists by mirroring the Kaggle column `Sales`. fileciteturn0file1

---

## 🧭 Portfolio Tips

- Add a short **project story** to the top of your README: business questions, what you discovered, and an insight summary.
- Include screenshots: an ERD (simple), a preview of the table, and result samples of the queries.
- If possible, attach a **Power BI/Tableau** one-pager built on the SQL output.

---

## 🧩 Troubleshooting

- **Kaggle API errors**: Verify `kaggle.json` path/permissions.
- **SQL Server connection**: Ensure ODBC Driver 17+ is installed; double-check the instance name and `Trusted_Connection`.
- **Datetime parsing**: If `order_date` has a different format, remove `format="%Y-%m-%d"` or set `dayfirst=True`.

---

## 🙌 Credits

- Dataset by **ankitbansal06** on Kaggle.
- ETL & SQL by **Md Naieem Al Zaman** (this portfolio).
- Guidance & structuring assistance by ChatGPT.

