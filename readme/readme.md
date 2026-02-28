# SmartFactory OS — Complete Project Structure

## 📁 Root Directory Layout

```
SmartFactory_OS/
│
├── main_app.py                  # Entry point / Login screen / Module launcher
├── build_app.py                 # PyInstaller build script → SmartFactory_OS.exe
├── db_manager.py                # Centralized PostgreSQL connection pool & query helpers
├── press_config.json            # Runtime config: STD vs OVEN mode per press (auto-generated)
│
├── modules/
│   ├── __init__.py
│   ├── building.py              # PC1 — Green Tyre Building (Desktop)
│   ├── building_touch.py        # PC1 — Green Tyre Building (Touch/Tablet UI)
│   ├── curing.py                # PC2 — Curing Station Traceability
│   ├── qc.py                    # PC3 — Final Quality Control & Digital Passport
│   ├── despatch.py              # PC4 — Logistics & Despatch Manager
│   ├── lab.py                   # Raw Material Approval (Lab QC)
│   ├── crm.py                   # CRM & Sales Command Center
│   ├── admin_dashboard.py       # System Administration & Master Data
│   ├── global_dashboard.py      # Global Analytics & Full Traceability Grid
│   ├── production_log.py        # Shift-wise Production Log & PDF Export
│   └── order_parser.py          # Smart DOCX Order Importer (Fuzzy Matching)
│
└── reports/                     # Auto-generated PDF reports (created at runtime)
```

---

## 🗄️ Database: `tyre_factory_db` (PostgreSQL)

### Master / Config Tables

| Table | Purpose |
|-------|---------|
| `users` | Operators, Supervisors, Managers — login & role management |
| `press_master` | Factory presses with daylight slots & ACTIVE/MAINTENANCE status |
| `product_catalog` | SKU master — tyre size + core + brand + quality + baseline weight |
| `tyre_specs` | Rubber % breakdown per grade (core, mid, C+T, gum, tread, is_pob) |
| `bead_master` | Bead size, count & weight per tyre size |
| `pc1_mould_mapping` | Mould ID → tyre size + pattern mapping |
| `qc_defects_master` | Defect code library (DIRECT / INDIRECT types) |
| `raw_material_qc` | Batch approval/rejection log from Lab |

### CRM / Orders Tables

| Table | Purpose |
|-------|---------|
| `customer_master` | Customer directory (region, market type, default currency) |
| `currency_rates` | Exchange rates (INR, USD, EUR) for order valuation |
| `master_orders` | Master Order Book — PI numbers, quantities, deadlines, priority, value |
| `production_plan` | Daily press assignment board — press + daylight → tyre spec + target qty |

### Production / Traceability Tables

| Table | Purpose |
|-------|---------|
| `pc1_building` | Green tyre build records — materials, weights, batches, operator, status |
| `pc2_curing` | Curing records — press, mould, time, temp, pressure, unload, flash waste |
| `pc3_quality` | Final QC — grade, hardness, defects, inspector, despatch status |

---

## 🔄 Production Flow (End-to-End)

```
CRM (crm.py)
  └─► Master Orders created with PI number, customer, qty, deadline, price

Admin (admin_dashboard.py)
  └─► Production Plan assigned: Press + Daylight → Tyre Spec (from Master Order or MTS)

Lab (lab.py)
  └─► Raw material batches approved/rejected

PC1 Building (building.py / building_touch.py)
  └─► Green tyre built: press selected → plan loaded → batches scanned →
       weight entered → label printed (B-ID barcode) → status: COMPLETED

PC2 Curing (curing.py)
  └─► B-ID scanned → Serial No generated (F0xxxxx) → Press/Mould assigned →
       Curing started → Unloaded → QC weight & flash recorded → status: COOLING → DONE

PC3 QC (qc.py)
  └─► Serial scanned → Hardness tested → Defects logged → Grade assigned
       (A-GRADE / B-GRADE / SCRAP) → produced_qty on master_orders incremented →
       Digital Passport generated (HTML)

PC4 Despatch (despatch.py)
  └─► PI loaded → Serial barcodes scanned to fulfil order lines →
       Manifest exported (HTML / CSV) → despatched_at timestamp set

Global Dashboard (global_dashboard.py)
  └─► Full traceability grid: PC1 → PC2 → PC3 → PC4 in one view
      Double-click → Digital Passport popup
```

---

## 📦 Module Details

### `db_manager.py`
- Connection pool (min 1, max 10) via `psycopg2`
- `execute_query()` — INSERT / UPDATE / DELETE
- `fetch_data()` — SELECT with result return
- `search_global()` — Cross-table search (orders + customers)
- Auto-initializes on import

### `building.py` (PC1 — Desktop)
- Plan loading from `production_plan` by press + daylight
- Cascading material targets (core %, mid %, tread % etc.) from `tyre_specs`
- Multi-select listboxes for batch scanning (barcode-friendly)
- 15% weight tolerance guardrail with warning popup
- POB (Press-On-Band) mode: shows Gum + MS Rim Weight fields
- PARTIAL / COMPLETED save modes
- Balance tracker: remaining qty vs target for the day
- EPL barcode label printing (Linux `/dev/usb/lp4`)
- Visual material consumption dashboard (progress bars)

### `building_touch.py` (PC1 — Touchscreen)
- Multi-page wizard UI (Step 1: Machine → Step 2: Batches → Step 3: Finish)
- Large touch-friendly tile buttons for batch selection
- Numpad widget for weight entry
- Tread Update page for completing PARTIAL tyres
- Auto press maintenance check before selection

### `curing.py` (PC2)
- STD (Press) vs OVEN mode toggle per machine (saved to `press_config.json`)
- B-ID barcode scan → validates COMPLETED status from PC1
- Auto serial number generation: `F0XXXXX WWYY` format
- Auto mould lookup from `pc1_mould_mapping`
- Overcure detection with early-unload warning
- Pending Queue tab: Green tyres awaiting curing, colour-coded by age (0–8h / 8–24h / 24–72h / 72h+)
- Reprint label from pending queue

### `qc.py` (PC3)
- Serial scan → Full tyre history loaded (PC1 + PC2 data joined)
- Hardness testing: Core Min/Max + Tread Min/Max (Shore A)
- Defect library (DIRECT/INDIRECT) from `qc_defects_master`
- Grade submission: A-GRADE / B-GRADE / SCRAP
- A-GRADE increments `master_orders.produced_qty` via `order_id` chain
- Digital Passport: rich-text on-screen + HTML export
- Pending Tracker tab: tyres cured but awaiting QC (detailed + summary views)
- QC Report with date range filter + CSV export + label reprint

### `despatch.py` (PC4)
- Load order from PI number or build manually (cascading catalog dropdowns)
- Lock order → enable barcode scanning mode
- Smart match: checks both product quality and QC grade
- Duplicate scan protection + already-shipped detection
- HTML Manifest + CSV export

### `crm.py`
- Sales Dashboard with KPI cards (pending value in Lakhs, active orders, overdue)
- Priority Hot List (P1 = critical, colour-coded by deadline)
- Master Orders CRUD with INSERT/UPDATE smart save (ON CONFLICT by PI number)
- Customer Master directory with region + market + default currency
- Exchange rate management (USD → INR auto-converts order values)
- CSV bulk upload for orders

### `admin_dashboard.py`
- User management (CRUD with role assignment)
- Raw Material inventory upload (CSV)
- Production Plan board: MTO (from Master Order) or MTS (Make to Stock) modes
- Weight guardrail: 15% tolerance enforced at plan assignment
- Master Orders tab (manual entry + CSV upload)
- Product Catalog (SKU master + CSV upload/delete)
- Tyre Specs, Bead Master, Mould Master, Defects Master — all CSV-uploadable
- Press Master: press + daylight pairs with ACTIVE/MAINTENANCE status

### `global_dashboard.py`
- Date-range filter (curing date based)
- Executive Summary tab: PC1/PC2/PC3 counts + yield %
- Full Traceability Grid: 26-column joined view across all 3 production tables
- Live search/filter across all columns
- Double-click → Digital Passport popup
- CSV export of filtered view

### `production_log.py`
- Shift cycle: A (07-15), B (15-23), C (23-07)
- Grouped production summary per shift with sub-totals + grand total
- KPI cards per shift (qty + total weight)
- PDF export via `reportlab`

### `order_parser.py`
- DOCX table parser using `python-docx`
- Regex extraction of tyre sizes from raw text
- Fuzzy matching against live DB values (sizes + brands) via `difflib`
- Colour-coded confidence (green ≥80% / yellow ≥50% / red <50%)
- Manual verification & correction editor

---

## 🔧 Key Dependencies

```
psycopg2        — PostgreSQL driver
tkinter         — GUI framework (built-in)
python-docx     — DOCX parsing (order_parser)
reportlab       — PDF generation (production_log)
PyInstaller     — .exe bundling (build_app.py)
```

---

## 🖨️ Label Printing
- Protocol: **EPL2** (Zebra-compatible)
- Connection: Direct write to `/dev/usb/lp4` (Linux)
- Labels printed at: PC1 Build, PC2 Cure Start, PC3 QC Complete
- Reprint available at: PC1 Tab3, PC2 Pending Queue, PC3 Report tab

---

## 🔑 Key Design Patterns
- **Order Tracing Chain**: `master_orders.order_id` → `production_plan.order_id` → `pc1_building.order_id` → `pc3_quality` (A-GRADE increments `produced_qty`)
- **Weight Guardrails**: 15% tolerance enforced at both plan assignment (Admin) and build submission (PC1)
- **Partial Build Flow**: PARTIAL status allows curing station gatekeeper to reject incomplete tyres
- **Cascading Dropdowns**: Product Catalog drives Size → Core → Brand → Quality selections throughout
