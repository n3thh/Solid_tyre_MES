# PROJECT MASTER PLAN

## 1. PROJECT OVERVIEW
Name: [PRODUCTION MES]
Goal: [Automate the Solid tyre Manufacturing process from Physical Digital and mainatain proper history of prodction as well as Tyre]
Target User: [for Easy auditing in QC and smoorth workflow for supervisor]

## 2. TECH STACK (Fixed)
* Language: [Python 3.13.7]
* Interface: [Tkinter for Desktop]
* Database: [PostgreSQL]
* External Libraries: []

## 3. DATABASE STRUCTURE (Data Models)
postgres=# \c tyre_factory_db
You are now connected to database "tyre_factory_db" as user "postgres".
tyre_factory_db=# \dt
               List of relations
 Schema |       Name        | Type  |  Owner   
--------+-------------------+-------+----------
 public | bead_master       | table | postgres
 public | pc1_building      | table | postgres
 public | pc1_mould_mapping | table | postgres
 public | pc2_curing        | table | postgres
 public | pc3_quality       | table | postgres
 public | production_plan   | table | postgres
 public | qc_defects_master | table | postgres
 public | raw_material_qc   | table | postgres
 public | tyre_specs        | table | postgres
 public | users             | table | postgres
(10 rows)

bead_master table structure
tyre_factory_db-# \d bead_master
                               Table "public.bead_master"
     Column      |         Type          | Collation | Nullable |        Default        
-----------------+-----------------------+-----------+----------+-----------------------
 tyre_size       | character varying(50) |           | not null | 
 mould_id        | character varying(50) |           | not null | ''::character varying
 bead_size       | character varying(50) |           |          | 
 bead_count      | integer               |           |          | 0
 weight_per_bead | numeric(10,3)         |           |          | 0.0
 core_size_ref   | character varying(50) |           |          | 
Indexes:
    "bead_master_pkey" PRIMARY KEY, btree (tyre_size, mould_id)

pc1_building table structure
tyre_factory_db-# \d pc1_building
                                       Table "public.pc1_building"
      Column       |            Type             | Collation | Nullable |            Default             
-------------------+-----------------------------+-----------+----------+--------------------------------
 b_id              | character varying(50)       |           | not null | 
 press_id          | character varying(50)       |           |          | 
 daylight          | character varying(50)       |           |          | 
 tyre_size         | character varying(50)       |           |          | 
 core_size         | character varying(50)       |           |          | 
 brand             | character varying(50)       |           |          | 
 pattern           | character varying(50)       |           |          | 
 quality           | character varying(50)       |           |          | 
 mould_id_marks    | character varying(100)      |           |          | 
 batch_mid         | text                        |           |          | 
 tread_type        | character varying(50)       |           |          | 
 green_tyre_weight | numeric(10,2)               |           |          | 
 operator_id       | character varying(50)       |           |          | 
 shift             | character varying(10)       |           |          | 
 created_at        | timestamp without time zone |           |          | CURRENT_TIMESTAMP
 status            | character varying(20)       |           |          | 'COMPLETED'::character varying
 ct_batch          | text                        |           |          | 
 is_pob            | boolean                     |           |          | false
 birth_time        | timestamp without time zone |           |          | 
 final_weight      | numeric(10,2)               |           |          | 
 updated_at        | timestamp without time zone |           |          | 
 batch_tread       | character varying(50)       |           |          | 
 batch_gum         | character varying(50)       |           |          | 
 batch_core        | character varying(50)       |           |          | 
Indexes:
    "pc1_building_pkey" PRIMARY KEY, btree (b_id)

pc2_curing table structure
tyre_factory_db-# \d pc2_curing
                                              Table "public.pc2_curing"
       Column        |            Type             | Collation | Nullable |                 Default                  
---------------------+-----------------------------+-----------+----------+------------------------------------------
 c_id                | integer                     |           | not null | nextval('pc1_curing_c_id_seq'::regclass)
 b_id                | character varying(20)       |           |          | 
 serial_no           | character varying(50)       |           |          | 
 process_type        | character varying(20)       |           |          | 'STANDARD'::character varying
 press_no            | character varying(50)       |           |          | 
 mould_no            | character varying(20)       |           |          | 
 operator_id         | character varying(50)       |           |          | 
 status              | character varying(50)       |           |          | 'CURING'::character varying
 green_weight        | numeric(5,2)                |           |          | 
 final_weight        | numeric(5,2)                |           |          | 
 flash_waste         | numeric(5,2)                |           |          | 
 start_time          | timestamp without time zone |           |          | now()
 press_finish_time   | timestamp without time zone |           |          | 
 oven_start_time     | timestamp without time zone |           |          | 
 oven_finish_time    | timestamp without time zone |           |          | 
 qc_grade            | character varying(10)       |           |          | 
 qc_remarks          | text                        |           |          | 
 temperature         | character varying(10)       |           |          | 
 pressure            | character varying(10)       |           |          | 
 is_oven             | boolean                     |           |          | false
 final_cured_weight  | numeric(5,2)                |           |          | 
 visual_qc_status    | character varying(20)       |           |          | 
 visual_qc_remarks   | text                        |           |          | 
 curing_time_minutes | integer                     |           |          | 
 end_time            | timestamp without time zone |           |          | 
 idle_time_minutes   | integer                     |           |          | 
 overcure_minutes    | integer                     |           |          | 0
 operator_name       | character varying(50)       |           |          | 
 supervisor_name     | character varying(50)       |           |          | 
 core_hardness_min   | character varying(10)       |           |          | 
 core_hardness_max   | character varying(10)       |           |          | 
 tread_hardness_min  | character varying(10)       |           |          | 
 tread_hardness_max  | character varying(10)       |           |          | 
 qc_defects          | text                        |           |          | 
 qc_engineer         | character varying(50)       |           |          | 
 qc_time             | timestamp without time zone |           |          | 
 shift               | character varying(5)        |           |          | 
 press_machine       | character varying(50)       |           |          | 
Indexes:
    "pc1_curing_pkey" PRIMARY KEY, btree (c_id)

tyre_factory_db-# \d pc3_quality
                                            Table "public.pc3_quality"
       Column       |            Type             | Collation | Nullable |                 Default                 
--------------------+-----------------------------+-----------+----------+-----------------------------------------
 id                 | integer                     |           | not null | nextval('pc3_quality_id_seq'::regclass)
 tyre_id            | character varying(50)       |           |          | 
 grade              | character varying(10)       |           | not null | 
 defect_codes       | character varying(100)      |           |          | 
 inspector_name     | character varying(50)       |           |          | 
 inspected_at       | timestamp without time zone |           |          | CURRENT_TIMESTAMP
 is_finalized       | boolean                     |           |          | false
 qc_remarks         | text                        |           |          | 
 hardness_core_min  | integer                     |           |          | 
 hardness_core_max  | integer                     |           |          | 
 hardness_tread_min | integer                     |           |          | 
 hardness_tread_max | integer                     |           |          | 
Indexes:
    "pc3_quality_pkey" PRIMARY KEY, btree (id)

production_plan table
tyre_factory_db-# \d production_plan
                                            Table "public.production_plan"
         Column         |          Type          | Collation | Nullable |                   Default                   
------------------------+------------------------+-----------+----------+---------------------------------------------
 id                     | integer                |           | not null | nextval('production_plan_id_seq'::regclass)
 press_id               | character varying(50)  |           |          | 
 daylight               | character varying(50)  |           |          | 
 tyre_size              | character varying(50)  |           |          | 
 core_size              | character varying(50)  |           |          | 
 brand                  | character varying(50)  |           |          | 
 pattern                | character varying(50)  |           |          | 
 quality                | character varying(50)  |           |          | 
 mould_id_marks         | character varying(100) |           |          | 
 type                   | character varying(50)  |           |          | 
 tyre_weight            | numeric(10,2)          |           |          | 
 production_requirement | integer                |           |          | 0
Indexes:
    "production_plan_pkey" PRIMARY KEY, btree (id)
    "production_plan_press_id_daylight_key" UNIQUE CONSTRAINT, btree (press_id, daylight)
table defect_master table structure
tyre_factory_db-# \d qc_defects_master
                                       Table "public.qc_defects_master"
    Column     |          Type          | Collation | Nullable |                    Default                    
---------------+------------------------+-----------+----------+-----------------------------------------------
 id            | integer                |           | not null | nextval('qc_defects_master_id_seq'::regclass)
 defect_code   | character varying(20)  |           | not null | 
 defect_name   | character varying(100) |           | not null | 
 defect_type   | character varying(20)  |           | not null | 
 defect_reason | character varying(255) |           |          | 
Indexes:
    "qc_defects_master_pkey" PRIMARY KEY, btree (id)
    "qc_defects_master_defect_code_key" UNIQUE CONSTRAINT, btree (defect_code)

Table raw_material_qc table structure
tyre_factory_db-# \d raw_material_qc
                                 Table "public.raw_material_qc"
    Column     |            Type             | Collation | Nullable |          Default          
---------------+-----------------------------+-----------+----------+---------------------------
 batch_no      | character varying(100)      |           | not null | 
 material_type | character varying(50)       |           |          | 
 status        | character varying(20)       |           |          | 'HOLD'::character varying
 updated_at    | timestamp without time zone |           |          | CURRENT_TIMESTAMP
Indexes:
    "raw_material_qc_pkey" PRIMARY KEY, btree (batch_no)

table tyre_specs table structure

tyre_factory_db-# \d tyre_specs
                      Table "public.tyre_specs"
   Column    |         Type          | Collation | Nullable | Default 
-------------+-----------------------+-----------+----------+---------
 grade       | character varying(50) |           | not null | 
 bead_weight | numeric(5,3)          |           |          | 
 core_pct    | numeric(5,2)          |           |          | 
 mid_pct     | numeric(5,2)          |           |          | 
 ct_pct      | numeric(5,2)          |           |          | 
 tread_pct   | numeric(5,2)          |           |          | 
 gum_pct     | numeric(5,2)          |           |          | 
 is_pob      | boolean               |           |          | false
Indexes:
    "tyre_specs_pkey" PRIMARY KEY, btree (grade)

users table structure
tyre_factory_db-# \d users
                                Table "public.users"
   Column   |            Type             | Collation | Nullable |      Default      
------------+-----------------------------+-----------+----------+-------------------
 user_id    | character varying(50)       |           | not null | 
 full_name  | character varying(100)      |           |          | 
 role       | character varying(50)       |           |          | 
 is_active  | boolean                     |           |          | true
 created_at | timestamp without time zone |           |          | CURRENT_TIMESTAMP
Indexes:
    "users_pkey" PRIMARY KEY, btree (user_id)


Progress made on:

🗄️ Database (PostgreSQL)

    pc1_building: Added ms_rim_weight (Numeric) and building_remarks (Text).

    pc3_quality: Added customer_name (VARCHAR) and despatched_at (TIMESTAMP).

    users: Added password (VARCHAR) with a default of '1234'.

🔐 main_app.py (Launcher & Login)

    Added a Password input field to the login UI.

    Updated the DB fetch logic to pull passwords and verify them upon login.

    Fixed the fallback local Admin profile to bypass DB connection errors.

    Added the menu button and launch function for PC4 (Despatch).

⚙️ admin_dashboard.py (Master Data)

    Added a Password text box to the Users tab to easily reset operator passwords.

    Added the "🤖 PARSE DOCX ORDER" trigger button to the Prod Plan tab (prepped for tomorrow).

🏗️ building.py (PC1)

    Added dynamic UI logic for POB Tyres (shows/hides the MS Rim Weight and Bonding Gum fields).

    Added the Building Remarks input field.

    Updated the mathematical validation to combine Target Rubber + MS Rim weight for the 15% tolerance check.

    Updated the SQL INSERT to save the new Rim Weight and Remarks.

🛡️ qc.py (PC3)

    Fixed a bug where "Mould ID" was showing up as "Building Remarks".

    Reformatted the Tyre History text and HTML Passport to cleanly separate Size, Core, Brand, and Quality into 4 distinct lines.

    Added a brand new "4. Logistics & Despatch" section to the History log and HTML card to track shipping status.

🚚 despatch.py (PC4) - NEW

    Built the full Shopping Cart order UI.

    Engineered the barcode scanner queue with strict validation (blocks scrap tyres, wrong sizes, and double-shipping).

    Added real-time database updates for customer_name and despatched_at.

    Added Export HTML and Export CSV manifest generation.

📄 order_parser.py (Smart DOCX Importer) - NEW / DRAFTED

    Created the UI and logic using python-docx, Regex, and difflib to extract tables from Word documents and fuzzy-match them against your database.
