# Restaurant Management System (RMS) – Azure Deployment & Documentation

## 1. Project Overview
This project is a **Restaurant Management System (RMS)** deployed on **Microsoft Azure**. It is composed of two main components:

- **POS (Point of Sale)**  
  Manages customer interactions such as orders, payments, and menu browsing. This is the staff-facing side of the system.

- **Management Portal**  
  Provides dashboards and reports for restaurant owners/managers. Enables tracking of sales, inventory, and overall business performance.

Both components are implemented as Python web applications (`app.py`) and run locally using:
```bash
python app.py
```

---

## 2. Folder Structure
```plaintext
project-root/
│
├── POS/                   # Point of Sale system (staff & customer-facing)
│   ├── app.py             # Main POS web application
│   ├── static/            # CSS, JS, images
│   ├── templates/         # HTML templates
│   └── ...                # POS-related modules (orders, customers)
│
└── management_portal/     # Owner/Manager dashboards
    ├── app.py             # Main dashboard web application
    ├── static/            # CSS, JS, images
    ├── templates/         # Dashboard HTML templates
    └── ...                # Modules for analytics, reports, charts
```

---

## 3. Azure Architecture

### Services Used
- **Azure SQL Database** → Stores structured data (customers, orders, inventory).
- **Azure App Service** → Hosts the POS and Management Portal apps.
- **Azure Key Vault** → Secures database connection strings and sensitive secrets.
- **Azure Data Factory** → ETL pipelines for analytics.
- **Azure Service Bus** → Event-driven communication between POS and backend systems.
- **Power BI** (planned integration) → Business intelligence dashboards.

---

## 4. Database Design (High-Level)

Entities currently modeled:
- `Users` → staff, owners, customers
- `Orders` & `Order_Items` → track customer orders
- `Menu_Items` → available products
- `Inventory` & `Inventory_Transactions` → stock levels and movements
- `Payments` → records of customer transactions

📌 An **ERD** (Entity Relationship Diagram) was generated to represent these entities and their relationships.

---

## 5. Security Considerations
- Passwords stored securely (hashed with **bcrypt/Argon2**).
- Secrets (DB connection strings, API keys) stored in **Azure Key Vault**.
- SQL Database encrypted at rest with **Transparent Data Encryption (TDE)**.
- Connections enforced over **TLS/SSL**.
- Authentication and authorization planned for both POS and Management Portal (future option: **Azure AD B2C**).

---

## 6. Infrastructure as Code (Terraform)

A Terraform configuration has been created to provision the required Azure resources:

- Resource Group
- Storage Account (for staging/logs)
- Key Vault (to store secrets)
- Azure SQL Server + Database (with firewall rules)
- App Service Plan + App Service (for web apps)
- Data Factory (for pipelines)
- Service Bus Namespace + Queue (for messaging)

### Key Features:
- DB connection string securely stored in **Key Vault**.
- Example firewall rule for developer IP.
- Outputs for resource names and endpoints after deployment.
- Recommendations included for production hardening (Managed Identity, monitoring, private endpoints).

📂 See Terraform file for implementation details.

---

## 7. Next Steps
- Containerize both apps (Docker) for deployment to App Service or AKS.
- Implement CI/CD pipeline (Azure DevOps or GitHub Actions).
- Add **Application Insights** for monitoring.
- Integrate **Power BI Embedded** into the management portal.
- Implement **Role-Based Access Control (RBAC)** for staff vs managers vs admin.

---

## 8. Notes
- Power BI provisioning is separate (handled via service principals or embedding APIs).
- For production: enable **purge protection** in Key Vault, use **private endpoints** for SQL and Storage.
- Sensitive variables should be stored in `terraform.tfvars` or pipeline secrets.
