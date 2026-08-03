# DigitalHub — Streamlit Frontend

A full Streamlit rewrite of the DigitalHub React frontend, covering both the
Admin and Vendor portals. **The FastAPI backend is unchanged** — this app is
a pure client calling the same REST API.

## What's included

**Admin portal**: Dashboard, Upload Dataset, Data Validation, Data Cleaning,
Customer Analytics, CLV Prediction, Churn Prediction, Sales Analytics,
Vendor Management, Vendor Details, Reports, Settings.

**Vendor portal**: Dashboard (with Recommendations), My Products (full CRUD
+ image upload/preview + delete confirmation), Orders, Inventory, Sales
Analytics, Reports, Profile.

Plus: Login and Vendor Registration.

## Important note on the Reports page

Your backend currently only has the **combined** report endpoint
(`POST /reports/{dataset_id}/generate` → one PDF covering everything). The
"4 separate report types" (Sales/Inventory/Vendor/Customer) work was
discussed but never merged into the backend, so this page is built against
what actually exists today. Once you add the 4 distinct endpoints, this page
is the one to update.

## Running it

This is a **separate folder from your existing frontend** — it doesn't touch
`src/` or `backend/` at all. Drop `streamlit_app/` alongside your existing
project (or wherever you like), then:

```bash
cd streamlit_app
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Point at your backend (defaults to http://localhost:8000/api/v1 if unset)
export BACKEND_URL=http://localhost:8000/api/v1      # Windows (PowerShell): $env:BACKEND_URL="..."

streamlit run app.py
```

Make sure your FastAPI backend is running first (`uvicorn app.main:app --reload`
from your `backend/` folder) — this app has nothing to render without it.

Login with your existing admin account (e.g. `admin@digitalhub.io` /
`ChangeMe123!`), or register a new vendor from the registration tab — both
portals are fully functional.

## Structure

```
streamlit_app/
  app.py                      Entry point: login/register gate, role-based nav
  requirements.txt
  .streamlit/config.toml      Light theme (indigo primary, matches original palette)
  core/
    api_client.py             requests wrapper: auth headers, error handling, file downloads
    auth.py                   Session-state-based login/register/logout, require_dataset() guard
    theme.py                  CSS injection + badge/status-pill helpers
    utils.py                  Currency/number/date formatting
  pages_admin/
    dashboard.py
    upload_dataset.py
    data_validation.py
    data_cleaning.py
    customer_analytics.py
    clv_prediction.py
    churn_prediction.py
    sales_analytics.py
    vendor_management.py
    vendor_details.py
    reports.py
    settings.py
  pages_vendor/
    dashboard.py               Includes the Recommendations section
    my_products.py             Full CRUD with image upload/preview, delete confirmation
    orders.py
    inventory.py                Stock levels + category breakdown chart
    sales_analytics.py
    reports.py
    profile.py
```

## Design notes

- **Theme**: light background, indigo (`#6366F1`) primary accent, dark
  sidebar (`#111827`) — same palette family as the original app, chosen
  fresh rather than pixel-matched (per your instruction).
- **Navigation**: uses `st.navigation()` with grouped sections (Overview /
  Data Management / Insights / Marketplace / System), mirroring your
  original sidebar's grouping.
- **Charts**: Plotly (area/line/bar/pie) instead of Recharts — closest
  equivalent for interactive, styled charts in Streamlit.
- **CLV/Churn pages**: auto-train on first view if no model exists yet,
  matching the auto-train behavior already in your React app — no manual
  "Train Model" click required.
- **Vendor Details**: since Streamlit doesn't have React-Router-style URL
  params by default, navigating from Vendor Management "View" button sets
  `st.session_state.selected_vendor_id` and switches page; Vendor Details
  also has a dropdown fallback if opened directly.
- **Dataset context**: `st.session_state.active_dataset` stands in for the
  original `DatasetContext` — set once on Upload, read by every page that
  needs it via `require_dataset()`.
- **My Products (Vendor)**: image upload uses `st.file_uploader` +
  multipart POST/PUT; existing product images preview via `st.image`.
  Delete uses a two-step confirm pattern (click Delete → inline warning +
  Confirm/Cancel) since Streamlit has no native modal dialog.
- **Vendor Recommendations**: surfaced as a section on the Vendor Dashboard
  (not a separate nav item), matching how it was added to the React app.

## Known limitations (being upfront)

- I don't have a live Streamlit/FastAPI environment to run this end-to-end
  in my sandbox — every file is syntax-checked (`py_compile`), and every API
  call is built from the exact request/response contracts established while
  building your backend, but this hasn't been click-tested against a running
  server. Please run it locally and expect a few rough edges.
- CSV/PDF download buttons call the backend eagerly on every page load
  (Streamlit's `download_button` needs the file bytes upfront) — functional,
  but means the Reports page does a backend round-trip on every visit even
  before you click anything.
