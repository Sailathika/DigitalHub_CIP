# DigitalHub_CIP

### AI-Powered Multi-Vendor E-Commerce & Customer Intelligence Platform

DigitalHub_CIP is a full-stack **multi-vendor e-commerce and customer intelligence platform** designed to help administrators and vendors manage products, customers, orders, inventory, sales, and business insights through a centralized system.

The platform combines **e-commerce management, customer analytics, machine learning, vendor management, reporting, and AI-powered recommendations** into a single application.

---

## 🚀 Key Features

### 👨‍💼 Admin Portal

* Admin authentication and role-based access
* Business performance dashboard
* Revenue and sales analytics
* Customer growth analysis
* Product and inventory overview
* Vendor management
* Vendor approval, activation, and suspension
* Low-stock monitoring
* Dataset upload and processing
* Customer analytics
* Customer segmentation
* Churn prediction
* Product recommendations
* PDF report generation
* CSV data export

### 🏪 Vendor Portal

* Vendor authentication
* Vendor dashboard
* Vendor profile management
* Product management
* Add, edit, and delete products
* Product image upload
* Inventory information
* Vendor-specific product view
* Vendor business insights

### 📊 Customer Intelligence

DigitalHub processes customer and transaction data to generate useful business insights.

The platform supports:

* **RFM Analysis**

  * Recency
  * Frequency
  * Monetary value
* Customer segmentation
* Customer behavior analysis
* Churn prediction
* Product recommendation
* Sales trend analysis
* Customer growth analysis

### 🤖 Machine Learning

The platform integrates machine-learning components for business intelligence, including:

* **K-Means Clustering** for customer segmentation
* **Random Forest** for churn prediction
* Recommendation logic for personalized product suggestions
* Feature engineering using customer transaction data

### 📑 Reports & Data Export

* Automated business reports
* PDF report generation using ReportLab
* CSV data export
* Analytics-ready processed data

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      User/Admin     │
                    │       / Vendor      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React + Vite UI   │
                    │   Tailwind CSS      │
                    └──────────┬──────────┘
                               │
                         REST API
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    │ Authentication      │
                    │ Business Logic      │
                    │ API Routers         │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │ SQLAlchemy  │  │   Pandas    │  │ ML Models   │
       │ Database    │  │ ETL/Data    │  │ K-Means     │
       │             │  │ Processing  │  │ RandomForest│
       └──────┬──────┘  └─────────────┘  └─────────────┘
              │
              ▼
       ┌─────────────┐
       │ SQLite /    │
       │ PostgreSQL  │
       └─────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

* React.js
* Vite
* Tailwind CSS
* JavaScript
* Lucide Icons

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic

### Data & Machine Learning

* Pandas
* NumPy
* Scikit-learn
* RFM Analysis
* K-Means Clustering
* Random Forest

### Database

* SQLite for development
* PostgreSQL-ready architecture

### Reporting

* ReportLab
* CSV Export

### Development & Deployment

* Git
* GitHub
* Vercel
* Render

---

## 📂 Project Structure

```text
DigitalHub_CIP/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── assets/
│   │   └── App.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── database/
│
├── data/
│
├── reports/
│
├── .gitignore
├── README.md
└── runtime.txt
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/DigitalHub_CIP.git

cd DigitalHub_CIP
```

---

## 🔧 Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend will run on:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

---

## 💻 Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at the local URL shown by Vite.

---

## 🔐 Authentication

DigitalHub_CIP provides authenticated access for different types of users.

### Admin

Admins can:

* Monitor overall platform performance
* Manage vendors
* View business analytics
* Process datasets
* Generate reports
* Access customer intelligence

### Vendor

Vendors can:

* Manage their profile
* Manage products
* Upload product images
* Monitor their business information

---

## 🔄 Data Intelligence Pipeline

```text
Dataset Upload
      ↓
Data Validation
      ↓
Data Cleaning
      ↓
Data Storage
      ↓
Exploratory Data Analysis
      ↓
Feature Engineering
      ↓
RFM Analysis
      ↓
Machine Learning
      ↓
Customer Segmentation
      ↓
Churn Prediction
      ↓
Product Recommendations
      ↓
Business Reports
```

---

## 📈 Customer Segmentation

RFM-based customer features are generated from transaction data.

The three main metrics are:

| Metric    | Description                         |
| --------- | ----------------------------------- |
| Recency   | How recently the customer purchased |
| Frequency | How often the customer purchases    |
| Monetary  | How much the customer spends        |

K-Means clustering is then used to group customers with similar purchasing behavior.

---

## 🔮 Churn Prediction

The platform uses customer behavioral features to identify customers who may be likely to stop purchasing.

The prediction pipeline includes:

```text
Customer Data
      ↓
Feature Engineering
      ↓
Training Dataset
      ↓
Random Forest Model
      ↓
Churn Prediction
      ↓
Customer Risk Insights
```

---

## 🛍️ Product Recommendations

The recommendation module uses customer and product behavior to provide relevant product suggestions.

This can help vendors and administrators:

* Identify products relevant to customers
* Improve customer engagement
* Support personalized shopping experiences
* Increase potential cross-selling opportunities

---

## 📊 Dashboard

The admin dashboard provides a centralized overview of the platform, including:

* Revenue
* Orders
* Customers
* Products
* Vendors
* Low-stock products
* Sales trends
* Customer growth

---

## 📄 Reporting

DigitalHub_CIP can generate business reports containing processed analytics and key insights.

Supported exports include:

* PDF reports
* CSV datasets

---

## 🌐 Deployment

The application is designed for separate frontend and backend deployment.

```text
React Frontend
      ↓
   Vercel
      ↓
FastAPI Backend
      ↓
    Render
      ↓
Database
```

Environment variables should be configured separately for development and production.

---

## 🔮 Future Enhancements

* PostgreSQL production database
* Advanced inventory forecasting
* Vendor performance ranking
* Real-time order management
* Advanced recommendation engine
* MLflow model tracking
* Docker containerization
* GitHub Actions CI/CD
* Advanced BI dashboards
* Real-time notifications
* AI-powered business assistant

---

## 🎯 Project Objectives

DigitalHub_CIP aims to:

1. Centralize multi-vendor e-commerce management.
2. Provide administrators with actionable business intelligence.
3. Help vendors efficiently manage their products.
4. Apply machine learning to customer behavior.
5. Enable data-driven decision making.
6. Provide personalized product recommendations.
7. Automate reporting and analytics.

---

## 👥 User Roles

| Role   | Main Responsibilities                            |
| ------ | ------------------------------------------------ |
| Admin  | Platform management, analytics, vendors, reports |
| Vendor | Profile and product management                   |

---

## 🏆 Project Outcome

DigitalHub_CIP demonstrates how a traditional e-commerce platform can be extended with **customer intelligence and machine learning** to transform raw transaction data into actionable business insights.

The project combines:

**E-Commerce + Data Engineering + Machine Learning + Analytics + AI**

into a single full-stack platform.

---

## 📜 License

This project was developed for academic/project purposes.

