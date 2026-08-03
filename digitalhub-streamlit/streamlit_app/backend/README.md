# DigitalHub — Backend

FastAPI + PostgreSQL + SQLAlchemy backend for the DigitalHub analytics
platform: dataset ingestion, validation, cleaning, ETL, customer/sales
analytics, RFM segmentation, CLV and churn prediction (scikit-learn,
tracked in MLflow), product recommendations, and PDF report generation
(ReportLab).

## Requirements

- Python 3.11+
- PostgreSQL 14+ (or use the provided `docker-compose.yml`)

## Quickstart (local Postgres)

```bash
cp .env.example .env          # edit DB credentials if needed
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# make sure PostgreSQL is running and the database in .env exists, e.g.:
#   createdb shopsense

uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000`. Interactive docs:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI schema: `http://localhost:8000/api/openapi.json`

Tables are created automatically on startup (`Base.metadata.create_all` —
see `app/database/session.py`; swap for Alembic migrations before a real
production rollout). A default admin account is seeded on first startup:
`admin@shopsense.io` / `ChangeMe123!` (override via `DEFAULT_ADMIN_EMAIL` /
`DEFAULT_ADMIN_PASSWORD` in `.env`).

## Quickstart (Docker)

```bash
docker compose up --build
```

This starts Postgres + the API together; the API is on `http://localhost:8000`.

## Typical flow

1. `POST /api/v1/auth/register` (vendor) or `/auth/login` (admin/vendor) → JWT
2. `POST /api/v1/datasets/upload` (multipart CSV/XLSX) → `Dataset`
3. `POST /api/v1/datasets/{id}/validate` → schema/quality checks
4. `POST /api/v1/datasets/{id}/clean` → cleaning issues + cleaned CSV
5. `POST /api/v1/datasets/{id}/etl` → loads normalized `Customer`/`Order`/`Product` rows
6. `GET /api/v1/analytics/{id}/customers`, `/analytics/{id}/sales` → dashboards
7. `POST /api/v1/segmentation/{id}/rfm` → RFM scores + segment labels
8. `POST /api/v1/clv/{id}/train` then `GET /api/v1/clv/{id}/predict`
9. `POST /api/v1/churn/{id}/train` then `GET /api/v1/churn/{id}/predict`
10. `GET /api/v1/recommendations/{id}/...` — frequently-bought-together / similar / personalized
11. `POST /api/v1/reports/{id}/generate` then `GET /api/v1/reports/{report_id}/download` → PDF

Every dataset-scoped route expects a `Bearer` JWT from step 1.

## Dataset column expectations

The uploaded CSV/XLSX doesn't need an exact schema — `app/preprocessing/validators.py`
resolves common aliases (e.g. `order_id`/`invoice_no`, `amount`/`total`/`revenue`,
`order_date`/`date`/`purchase_date`). Required at minimum: an order identifier,
a customer identifier, a date, and an amount column. `product_id`/`sku`,
`category`, and `quantity` unlock recommendations and category breakdowns.

## MLflow

Tracking URI defaults to a local `file:///./mlruns` store (`MLFLOW_TRACKING_URI`
in `.env`). Inspect runs with:

```bash
mlflow ui --backend-store-uri ./mlruns
```

## Project layout

```
app/
  api/v1/         Route handlers, one module per domain (auth, datasets, etl, ...)
  auth/           JWT handling, password hashing, FastAPI auth dependencies
  database/       SQLAlchemy engine/session, table bootstrap, admin seeding
  models/         SQLAlchemy ORM models
  schemas/        Pydantic request/response models
  repository/     Data-access layer (generic BaseRepository + per-entity repos)
  services/       Business logic orchestrating repositories + preprocessing + ml
  preprocessing/  pandas-based validation, cleaning, feature engineering
  ml/             RFM, CLV (GradientBoostingRegressor), churn (RandomForest),
                  recommendations, MLflow helpers
  reports/        ReportLab PDF builder
  utils/          File handling, logging, shared response helpers
  main.py         FastAPI app, middleware, startup hooks
mlruns/           MLflow tracking store
uploads/          Raw uploaded files
cleaned_data/     Cleaned CSV output per dataset
reports/          Generated PDF reports
```

## Notes on modeling choices

- **CLV** is trained as a regression on RFM-style features (recency, frequency,
  average order value) against historical monetary value — a practical proxy
  since no separate "future spend" ground truth exists in an uploaded
  transaction export.
- **Churn** doesn't have an explicit label in typical order data either, so a
  proxy label is derived (recency beyond 1.5× the dataset's median counts as
  "churned") and a Random Forest is trained to predict *that*, which is what
  makes the feature-importance output meaningful rather than circular.
- Both are retrained per dataset via `POST /clv/{id}/train` and
  `POST /churn/{id}/train`, and every run is logged to MLflow with params,
  metrics, and the serialized model artifact.
