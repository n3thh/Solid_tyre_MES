--
-- PostgreSQL database dump
--

\restrict o1FtGDJY5KF7LGpZPYO4bcWAFek0oUNPbhOqe9lYq1gVyiNLyTjrtcNzo4nDMWT

-- Dumped from database version 17.7 (Ubuntu 17.7-0ubuntu0.25.10.1)
-- Dumped by pg_dump version 17.7 (Ubuntu 17.7-0ubuntu0.25.10.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bead_master; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bead_master (
    tyre_size character varying(50) NOT NULL,
    mould_id character varying(50) DEFAULT ''::character varying NOT NULL,
    bead_size character varying(50),
    bead_count integer DEFAULT 0,
    weight_per_bead numeric(10,3) DEFAULT 0.0,
    core_size_ref character varying(50)
);


ALTER TABLE public.bead_master OWNER TO postgres;

--
-- Name: currency_rates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.currency_rates (
    currency_code character varying(10) NOT NULL,
    rate_to_inr numeric(10,2) DEFAULT 1.00,
    last_updated timestamp without time zone DEFAULT now()
);


ALTER TABLE public.currency_rates OWNER TO postgres;

--
-- Name: customer_master; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_master (
    customer_id character varying(50) NOT NULL,
    customer_name character varying(100) NOT NULL,
    region character varying(50),
    market_type character varying(20),
    default_currency character varying(10) DEFAULT 'INR'::character varying
);


ALTER TABLE public.customer_master OWNER TO postgres;

--
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    cust_id integer NOT NULL,
    company_name character varying(100) NOT NULL,
    city character varying(50)
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- Name: customers_cust_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_cust_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customers_cust_id_seq OWNER TO postgres;

--
-- Name: customers_cust_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customers_cust_id_seq OWNED BY public.customers.cust_id;


--
-- Name: master_orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.master_orders (
    order_id integer NOT NULL,
    pi_number character varying(50) NOT NULL,
    customer_name character varying(100) NOT NULL,
    tyre_size character varying(50) NOT NULL,
    core_size character varying(50) NOT NULL,
    brand character varying(50) NOT NULL,
    quality character varying(50),
    req_qty integer NOT NULL,
    produced_qty integer DEFAULT 0,
    despatched_qty integer DEFAULT 0,
    status character varying(20) DEFAULT 'OPEN'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    priority_level integer DEFAULT 3,
    committed_date date,
    unit_price_foreign numeric(10,2) DEFAULT 0.00,
    currency character varying(10) DEFAULT 'INR'::character varying,
    unit_price_inr numeric(10,2) DEFAULT 0.00,
    tyre_type character varying(50),
    pattern character varying(50),
    min_hardness numeric DEFAULT 65
);


ALTER TABLE public.master_orders OWNER TO postgres;

--
-- Name: master_orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.master_orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.master_orders_order_id_seq OWNER TO postgres;

--
-- Name: master_orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.master_orders_order_id_seq OWNED BY public.master_orders.order_id;


--
-- Name: pc1_building; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pc1_building (
    b_id character varying(50) NOT NULL,
    press_id character varying(50),
    daylight character varying(50),
    tyre_size character varying(50),
    core_size character varying(50),
    brand character varying(50),
    pattern character varying(50),
    quality character varying(50),
    mould_id_marks character varying(100),
    batch_mid text,
    tread_type character varying(50),
    green_tyre_weight numeric(10,2),
    operator_id character varying(50),
    shift character varying(10),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(20) DEFAULT 'COMPLETED'::character varying,
    ct_batch text,
    is_pob boolean DEFAULT false,
    birth_time timestamp without time zone,
    final_weight numeric(10,2),
    updated_at timestamp without time zone,
    batch_tread character varying(50),
    batch_gum character varying(50),
    batch_core character varying(50),
    ms_rim_weight numeric(10,2) DEFAULT 0.0,
    building_remarks text,
    pi_number character varying(100),
    target_weight numeric(10,2),
    core_batch_list text,
    middle_batch_list text,
    build_status character varying(20) DEFAULT 'COMPLETE'::character varying,
    daylight_id character varying(10)
);


ALTER TABLE public.pc1_building OWNER TO postgres;

--
-- Name: pc2_curing; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pc2_curing (
    c_id integer NOT NULL,
    b_id character varying(20),
    serial_no character varying(50),
    process_type character varying(20) DEFAULT 'STANDARD'::character varying,
    press_no character varying(50),
    mould_no character varying(20),
    operator_id character varying(50),
    status character varying(50) DEFAULT 'CURING'::character varying,
    green_weight numeric(5,2),
    final_weight numeric(5,2),
    flash_waste numeric(5,2),
    start_time timestamp without time zone DEFAULT now(),
    press_finish_time timestamp without time zone,
    oven_start_time timestamp without time zone,
    oven_finish_time timestamp without time zone,
    qc_grade character varying(10),
    qc_remarks text,
    temperature character varying(10),
    pressure character varying(10),
    is_oven boolean DEFAULT false,
    final_cured_weight numeric(5,2),
    visual_qc_status character varying(20),
    visual_qc_remarks text,
    curing_time_minutes integer,
    end_time timestamp without time zone,
    idle_time_minutes integer,
    overcure_minutes integer DEFAULT 0,
    operator_name character varying(50),
    supervisor_name character varying(50),
    core_hardness_min character varying(10),
    core_hardness_max character varying(10),
    tread_hardness_min character varying(10),
    tread_hardness_max character varying(10),
    qc_defects text,
    qc_engineer character varying(50),
    qc_time timestamp without time zone,
    shift character varying(5),
    press_machine character varying(50)
);


ALTER TABLE public.pc2_curing OWNER TO postgres;

--
-- Name: pc1_curing_c_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pc1_curing_c_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pc1_curing_c_id_seq OWNER TO postgres;

--
-- Name: pc1_curing_c_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pc1_curing_c_id_seq OWNED BY public.pc2_curing.c_id;


--
-- Name: pc1_mould_mapping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pc1_mould_mapping (
    id integer NOT NULL,
    tyre_size character varying(50),
    mould_id character varying(50),
    pattern character varying(50)
);


ALTER TABLE public.pc1_mould_mapping OWNER TO postgres;

--
-- Name: pc1_mould_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pc1_mould_mapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pc1_mould_mapping_id_seq OWNER TO postgres;

--
-- Name: pc1_mould_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pc1_mould_mapping_id_seq OWNED BY public.pc1_mould_mapping.id;


--
-- Name: pc3_quality; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pc3_quality (
    id integer NOT NULL,
    tyre_id character varying(50),
    grade character varying(10) NOT NULL,
    defect_codes character varying(100),
    inspector_name character varying(50),
    inspected_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_finalized boolean DEFAULT false,
    qc_remarks text,
    hardness_core_min integer,
    hardness_core_max integer,
    hardness_tread_min integer,
    hardness_tread_max integer,
    customer_name character varying(100),
    despatched_at timestamp without time zone
);


ALTER TABLE public.pc3_quality OWNER TO postgres;

--
-- Name: pc3_quality_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pc3_quality_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pc3_quality_id_seq OWNER TO postgres;

--
-- Name: pc3_quality_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pc3_quality_id_seq OWNED BY public.pc3_quality.id;


--
-- Name: press_master; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.press_master (
    press_id character varying(50) NOT NULL,
    daylight character varying(50) NOT NULL,
    status character varying(50) DEFAULT 'ACTIVE'::character varying,
    remarks text
);


ALTER TABLE public.press_master OWNER TO postgres;

--
-- Name: product_catalog; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_catalog (
    sku_id integer NOT NULL,
    tyre_size character varying(50) NOT NULL,
    core_size character varying(50) NOT NULL,
    brand character varying(50) NOT NULL,
    quality character varying(50) NOT NULL,
    baseline_weight numeric(5,2) NOT NULL,
    is_active boolean DEFAULT true
);


ALTER TABLE public.product_catalog OWNER TO postgres;

--
-- Name: product_catalog_sku_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_catalog_sku_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_catalog_sku_id_seq OWNER TO postgres;

--
-- Name: product_catalog_sku_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_catalog_sku_id_seq OWNED BY public.product_catalog.sku_id;


--
-- Name: production_plan; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.production_plan (
    id integer NOT NULL,
    press_id character varying(50),
    daylight character varying(50),
    tyre_size character varying(50),
    core_size character varying(50),
    brand character varying(50),
    pattern character varying(50),
    quality character varying(50),
    mould_id_marks character varying(100),
    type character varying(50),
    tyre_weight numeric(10,2),
    production_requirement integer DEFAULT 0,
    pi_number character varying(100),
    tyre_type character varying(50)
);


ALTER TABLE public.production_plan OWNER TO postgres;

--
-- Name: production_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.production_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.production_plan_id_seq OWNER TO postgres;

--
-- Name: production_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.production_plan_id_seq OWNED BY public.production_plan.id;


--
-- Name: qc_approval_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.qc_approval_logs (
    qc_id integer NOT NULL,
    batch_number character varying(50) NOT NULL,
    compound_type character varying(50),
    test_result character varying(20),
    lab_operator character varying(50),
    properties_json jsonb,
    approved_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.qc_approval_logs OWNER TO postgres;

--
-- Name: qc_approval_logs_qc_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.qc_approval_logs_qc_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.qc_approval_logs_qc_id_seq OWNER TO postgres;

--
-- Name: qc_approval_logs_qc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.qc_approval_logs_qc_id_seq OWNED BY public.qc_approval_logs.qc_id;


--
-- Name: qc_defects_master; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.qc_defects_master (
    id integer NOT NULL,
    defect_code character varying(20) NOT NULL,
    defect_name character varying(100) NOT NULL,
    defect_type character varying(20) NOT NULL,
    defect_reason character varying(255)
);


ALTER TABLE public.qc_defects_master OWNER TO postgres;

--
-- Name: qc_defects_master_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.qc_defects_master_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.qc_defects_master_id_seq OWNER TO postgres;

--
-- Name: qc_defects_master_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.qc_defects_master_id_seq OWNED BY public.qc_defects_master.id;


--
-- Name: raw_material_qc; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.raw_material_qc (
    batch_no character varying(100) NOT NULL,
    material_type character varying(50),
    status character varying(20) DEFAULT 'HOLD'::character varying,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_active boolean DEFAULT true
);


ALTER TABLE public.raw_material_qc OWNER TO postgres;

--
-- Name: ref_remarks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ref_remarks (
    remark_id integer NOT NULL,
    remark_text character varying(100) NOT NULL,
    is_active boolean DEFAULT true
);


ALTER TABLE public.ref_remarks OWNER TO postgres;

--
-- Name: ref_remarks_remark_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ref_remarks_remark_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ref_remarks_remark_id_seq OWNER TO postgres;

--
-- Name: ref_remarks_remark_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ref_remarks_remark_id_seq OWNED BY public.ref_remarks.remark_id;


--
-- Name: tyre_specs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tyre_specs (
    grade character varying(50) NOT NULL,
    bead_weight numeric(5,3),
    core_pct numeric(5,2),
    mid_pct numeric(5,2),
    ct_pct numeric(5,2),
    tread_pct numeric(5,2),
    gum_pct numeric(5,2),
    is_pob boolean DEFAULT false,
    tolerance_plus numeric(5,2) DEFAULT 0.50,
    tolerance_minus numeric(5,2) DEFAULT 0.50
);


ALTER TABLE public.tyre_specs OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id character varying(50) NOT NULL,
    full_name character varying(100),
    role character varying(50),
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    password character varying(100) DEFAULT '1234'::character varying
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: customers cust_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers ALTER COLUMN cust_id SET DEFAULT nextval('public.customers_cust_id_seq'::regclass);


--
-- Name: master_orders order_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.master_orders ALTER COLUMN order_id SET DEFAULT nextval('public.master_orders_order_id_seq'::regclass);


--
-- Name: pc1_mould_mapping id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pc1_mould_mapping ALTER COLUMN id SET DEFAULT nextval('public.pc1_mould_mapping_id_seq'::regclass);


--
-- Name: pc2_curing c_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pc2_curing ALTER COLUMN c_id SET DEFAULT nextval('public.pc1_curing_c_id_seq'::regclass);


--
-- Name: pc3_quality id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pc3_quality ALTER COLUMN id SET DEFAULT nextval('public.pc3_quality_id_seq'::regclass);


--
-- Name: product_catalog sku_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_catalog ALTER COLUMN sku_id SET DEFAULT nextval('public.product_catalog_sku_id_seq'::regclass);


--
-- Name: production_plan id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.production_plan ALTER COLUMN id SET DEFAULT nextval('public.production_plan_id_seq'::regclass);


--
-- Name: qc_approval_logs qc_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qc_approval_logs ALTER COLUMN qc_id SET DEFAULT nextval('public.qc_approval_logs_qc_id_seq'::regclass);


--
-- Name: qc_defects_master id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qc_defects_master ALTER COLUMN id SET DEFAULT nextval('public.qc_defects_master_id_seq'::regclass);


--
-- Name: ref_remarks remark_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ref_remarks ALTER COLUMN remark_id SET DEFAULT nextval('public.ref_remarks_remark_id_seq'::regclass);


--
-- Data for Name: bead_master; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bead_master (tyre_size, mould_id, bead_size, bead_count, weight_per_bead, core_size_ref) FROM stdin;
6.50-10	6.50-10 F	10" DRUM SIZE	3	0.205	5.00"
23X9.00-10	23X9.00-10 B	10" DRUM SIZE	3	0.205	6.50"
6.50-10	6.50-10 A	10" DRUM SIZE	3	0.205	5.00"
23X10-12	23X10-12	12" DRUM SIZE	3	0.250	8.00"
6.50-10	6.50-10 D	10" DRUM SIZE	3	0.205	5.00"
29X7.00-15	29X7.00-15 B	15" DRUM SIZE	3	0.320	6.00"
29X7.50-15	29X7.50-15 C	15" DRUM SIZE	3	0.320	5.50"
10.00-20	10.00-20	20" DRUM SIZE	4	0.420	7.50"
40X11.00-20	40X11.00-20	20" DRUM SIZE	4	0.420	7.50"
12.00-20	12.00-20	20" DRUM SIZE	4	0.420	8.00"
29X250-15	29X250-15	16" DRUM SIZE	3	0.340	7.00"
12X4.00-4	12X4.00-4	nan	0	NaN	2.50"
15X4.5-8	15X4.5-8	8" DRUM SIZE	2	0.180	3.00"
140X55-9	140X55-9	9" DRUM SIZE	2	0.195	4.00"
140X55-9	140X55-9 RIB	9" DRUM SIZE	2	0.195	4.00"
4.00-8	4.00-8 A	8" DRUM SIZE	2	0.180	3.00"
4.00-8	4.00-8 B	8" DRUM SIZE	2	0.180	3.00"
16X6.00-8	16X6.00-8	8" DRUM SIZE	2	0.180	4.33"
5.00-8	5.00-8 A	8" DRUM SIZE	2	0.180	3.00"
5.00-8	5.00-8 B	8" DRUM SIZE	2	0.180	3.00"
5.00-8	5.00-8 C	8" DRUM SIZE	2	0.180	3.00"
180X60-10	180X60-10	10" DRUM SIZE	2	0.205	5.00"
200X50-10	200X50-10	10" DRUM SIZE	2	0.205	6.50"
18X7.00-8	18X7.00-8 A	8" DRUM SIZE	2	0.180	4.33"
18X7.00-8	18X7.00-8 B	8" DRUM SIZE	2	0.180	4.33"
18X7.00-8	18X7.00-8 C	8" DRUM SIZE	2	0.180	4.33"
18X7.00-8	18X7.00-8 D	8" DRUM SIZE	2	0.180	4.33"
6.00-9	6.00-9 A	9" DRUM SIZE	2	0.195	4.00"
6.00-9	6.00-9 B	9" DRUM SIZE	2	0.195	4.00"
6.00-9	6.00-9 C	9" DRUM SIZE	2	0.195	4.00"
6.00-9	6.00-9 D	9" DRUM SIZE	2	0.195	4.00"
21X8.00-9	21X8.00-9	9" DRUM SIZE	2	0.195	6.00"
6.50-10	6.50-10 B	10" DRUM SIZE	3	0.205	5.00"
6.50-10	6.50-10 E	10" DRUM SIZE	3	0.205	5.00"
23X9.00-10	23X9.00-10 A	10" DRUM SIZE	3	0.205	6.50"
6.50-10	6.50-10 C	10" DRUM SIZE	3	0.205	5.00"
28X9.00-16	28X9.00-16	16" DRUM SIZE	3	0.340	6.00"
7.00-12	7.00-12 A	12" DRUM SIZE	3	0.250	5.00"
7.00-12	7.00-12 B	12" DRUM SIZE	3	0.250	5.00"
7.00-12	7.00-12 C	12" DRUM SIZE	3	0.250	5.00"
7.00-12	7.00-12 D	12" DRUM SIZE	3	0.250	5.00"
7.00-12	7.00-12 E	12" DRUM SIZE	3	0.250	5.00"
27X10.00-12	27X10.00-12	12" DRUM SIZE	3	0.250	8.00"
8.15-15	8.15-15 A	15" DRUM SIZE	3	0.320	6.50"
8.15-15	8.15-15 B	15" DRUM SIZE	3	0.320	6.50"
8.15-15	8.15-15 C	15" DRUM SIZE	3	0.320	6.50"
8.15-15	8.15-15 D	15" DRUM SIZE	3	0.320	6.50"
28X9.00-15	28X9.00-15 A	15" DRUM SIZE	3	0.320	7.00"
28X9.00-15	28X9.00-15 B	15" DRUM SIZE	3	0.320	7.00"
28X9.00-15	28X9.00-15 C	15" DRUM SIZE	3	0.320	7.00"
28X9.00-15	28X9.00-15 D	15" DRUM SIZE	3	0.320	7.00"
28X12.50-15	28X12.50-15	15" DRUM SIZE	3	0.320	9.75"
28X9.00-15	28X9.00-15 E	15" DRUM SIZE	3	0.320	7.00"
29X7.00-15	29X7.00-15 A	15" DRUM SIZE	3	0.320	6.00"
29X7.00-15	29X7.00-15 C	15" DRUM SIZE	3	0.320	6.00"
29X7.00-15	29X7.00-15 D	15" DRUM SIZE	3	0.320	5.50"
29X7.50-15	29X7.50-15 A	15" DRUM SIZE	3	0.320	5.50"
29X7.50-15	29X7.50-15 B	15" DRUM SIZE	3	0.320	5.50"
7.50-16	7.50-16 A	16" DRUM SIZE	3	0.340	6.00"
7.50-16	7.50-16 B	16" DRUM SIZE	3	0.340	6.00"
8.25-15	8.25-15 A	16" DRUM SIZE	3	0.340	6.50"
8.25-15	8.25-15 B	16" DRUM SIZE	3	0.340	6.50"
8.25-15	8.25-15 C	16" DRUM SIZE	3	0.340	6.50"
32X8.25-16	32X8.25-16 A	16" DRUM SIZE	3	0.340	6.00"
32X8.25-16	32X8.25-16 C	16" DRUM SIZE	3	0.340	6.00"
32X300-15	32X300-15	16" DRUM SIZE	3	0.340	8.00"
32X12.00-20	32X12.00-20	20" DRUM SIZE	3	0.420	7.50"
355X45-15	355X45-15	16" DRUM SIZE	3	0.340	9.75"
355X55-15	355X55-15	16" DRUM SIZE	3	0.340	9.75"
355X65-15	355X65-15	16" DRUM SIZE	3	0.340	9.75"
39X9.00-20	39X9.00-20	20" DRUM SIZE	4	0.420	7.00"
355X50-15	355X50-15	16" DRUM SIZE	3	0.340	9.75"
28X8.15[9.00]- 15	28X8.15[9.00]- 15	15" DRUM SIZE	3	0.320	7.00"
18X8 -12-1/8	18X8 -12-1/8	POB	0	NaN	POB
15X5X11 1/4	15X5X11 1/4	POB	0	NaN	POB
16X7X10-1/2	16X7X10-1/2	POB	0	NaN	POB
10X5X6-1/4	10X5X6-1/4	POB	0	NaN	POB
10X6X6-1/4	10X6X6-1/4	POB	0	NaN	POB
16X5X10-1/2	16X5X10-1/2	POB	0	NaN	POB
16X6X10-1/2	16X6X10-1/2 A	POB	0	NaN	POB
16X6X10-1/2	16X6X10-1/2 B	POB	0	NaN	POB
16-1/4X5X11-1/4	16-1/4X5X11-1/4	POB	0	NaN	POB
16-1/4X6X11-1/4	16-1/4X6X11-1/4 A	POB	0	NaN	POB
16-1/4X6X11-1/4	16-1/4X6X11-1/4 B	POB	0	NaN	POB
16-1/4X7X11-1/4	16-1/4X7X11-1/4 A	POB	0	NaN	POB
16-1/4X7X11-1/4	16-1/4X7X11-1/4 B	POB	0	NaN	POB
17-1/4X5X11-1/4	17-1/4X5X11-1/4	POB	0	NaN	POB
17-1/4X6X11-1/4	17-1/4X6X11-1/4	POB	0	NaN	POB
18X5X12-1/8	18X5X12-1/8	POB	0	NaN	POB
18X6X12-1/8	18X6X12-1/8	POB	0	NaN	POB
400X100X310	400X100X310	nan	0	NaN	3.00"
3.50-4	3.50-4	nan	0	NaN	2.50"
28X9.00-15	28X9.00-15 D 	15" DRUM SIZE	3	0.320	7.00"
18X7X12-1/8	18X7X12-1/8	POB	0	NaN	POB
18X8X12-1/8	18X8X12-1/8	POB	0	NaN	POB
18X9X12-1/8	18X9X12-1/8	POB	0	NaN	POB
21X5.00X15	21X5.00X15	POB	0	NaN	POB
21X6.00X15	21X6.00X15	POB	0	NaN	POB
21X7.00X15	21X7.00X15 A	POB	0	NaN	POB
21X7.00X15	21X7.00X15 B	POB	0	NaN	POB
21X8.00- 15	21X8.00- 15 A	POB	0	NaN	POB
21X8.00- 15	21X8.00- 15 B	POB	0	NaN	POB
21X9.00X15	21X9.00X15 C	POB	0	NaN	POB
22X6.00X16	22X6.00X16	POB	0	NaN	POB
22X6.00X17-3/4	22X6.00X17-3/4	POB	0	NaN	POB
22X7.00X17-3/4	22X7.00X17-3/4	POB	0	NaN	POB
15X5	15X5	POB	0	NaN	POB
16X6- 11 1/2	16X6- 11 1/2	POB	0	NaN	POB
22X9.00- 16	22X9.00- 16	POB	0	NaN	POB
22X10.00- 16	22X10.00- 16	POB	0	NaN	POB
31X10.00- 16	31X10.00- 16	16" DRUM SIZE	3	0.340	6.00"
23X12.00-12	23X12.00-12	12" DRUM SIZE	3	0.250	10.00"
22X8.00- 16	22X8.00- 16	POB	0	NaN	POB
22X12.00- 16	22X12.00- 16	POB	0	NaN	POB
31X10.00-20	31X10.00-20	20" DRUM SIZE	4	0.420	7.50"
\.


--
-- Data for Name: currency_rates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.currency_rates (currency_code, rate_to_inr, last_updated) FROM stdin;
INR	1.00	2026-02-24 22:37:33.307192
USD	90.00	2026-02-25 08:33:48.388461
\.


--
-- Data for Name: customer_master; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_master (customer_id, customer_name, region, market_type, default_currency) FROM stdin;
CEX0001	PARAGON STARS	MIDDLE EAST	EXPORT	USD
CD0001	SARKAR INFOTECH	DOMESTIC	LOCAL	INR
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customers (cust_id, company_name, city) FROM stdin;
\.


--
-- Data for Name: master_orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.master_orders (order_id, pi_number, customer_name, tyre_size, core_size, brand, quality, req_qty, produced_qty, despatched_qty, status, created_at, priority_level, committed_date, unit_price_foreign, currency, unit_price_inr, tyre_type, pattern, min_hardness) FROM stdin;
7	20	PARAGON STARS	7.00-12	5.00"	PAREX	V3H03	50	1	0	OPEN	2026-02-25 10:21:17.687079	1	2026-03-27	88.82	USD	7993.80	Standard Black	VXT-02	65
8	VTPL-PI21	SARKAR INFOTECH	21X7.00X15	POB	VELOX	POB-STD	10	0	0	OPEN	2026-02-27 23:28:52.664878	2	2026-03-29	6200.00	INR	6200.00	PRESS-ON-BAND(POB)	VXT-02	65
9	VTPL-PI22	PARAGON STARS	6.50-10	5.00"	PAREX	V3H03	10	0	0	URGENT	2026-03-01 22:08:36.360346	3	2026-03-31	76.00	USD	6840.00	CUSHION	VXT-02	65
\.


--
-- Data for Name: pc1_building; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pc1_building (b_id, press_id, daylight, tyre_size, core_size, brand, pattern, quality, mould_id_marks, batch_mid, tread_type, green_tyre_weight, operator_id, shift, created_at, status, ct_batch, is_pob, birth_time, final_weight, updated_at, batch_tread, batch_gum, batch_core, ms_rim_weight, building_remarks, pi_number, target_weight, core_batch_list, middle_batch_list, build_status, daylight_id) FROM stdin;
B-1001	P-01	SINGLE	18x7-8	4.33"	BOSON	LUG	Premium	M-101-L	S0007, S0008	VT001	20.20	Test Pilot	C	2026-02-14 00:05:27.028711	COMPLETED	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-1002	P-01	SINGLE	18x7-8	4.33"	BOSON	LUG	Premium	M-101-L	S0006	VT001	20.20	AJI MOHAN	C	2026-02-14 00:14:51.919785	COMPLETED	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-1003	P-01	SINGLE	18x7-8	4.33"	BOSON	LUG	Premium	M-101-L	S0006	VT001	20.20	AJI MOHAN	C	2026-02-14 00:15:02.870536	COMPLETED	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-1004	P-02	SINGLE	6.00-9	4.00"	TVS	RIB	Standard	M-205-R	S0006	VT001	24.50	AJI MOHAN	C	2026-02-14 00:15:18.085514	COMPLETED	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-1005	P-03	BOT	18x7-8	4.33"	CHALLENGER	LUG	Premium	M-102-B1	S0006	VT001	20.80	AJI MOHAN	C	2026-02-14 00:15:31.532213	COMPLETED	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-1006	P-03	TOP	18x7-8	4.33"	VELOX	LUG	Premium	M-102-T	S0006	VT001	20.60	AJI MOHAN	C	2026-02-14 00:15:45.61709	COMPLETED	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-1007	P-04	BOT	140X55-9	4.00"	TVS	LUG	VPR02	M-102-B3	S0006	VT001	10.80	AJI MOHAN	C	2026-02-14 00:15:55.399466	COMPLETED	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-1008	P-04	TOP	15X4.50-8	3.00"	BOSON	LUG	VPR02	M-102-B2	S0006	VT001	11.20	AJI MOHAN	C	2026-02-14 00:16:03.082454	COMPLETED	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010940	P-01	SINGLE	18x7-8	\N	BOSON	LUG	Premium	M-101-L		VT001	\N	AJI MOHAN	C	2026-02-14 01:09:40.783095	COMPLETED		f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010947	P-01	SINGLE	18x7-8	\N	BOSON	LUG	Premium	M-101-L		VT001	\N	AJI MOHAN	C	2026-02-14 01:09:47.599566	COMPLETED		f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010950	P-01	SINGLE	18x7-8	\N	BOSON	LUG	Premium	M-101-L		VT001	\N	AJI MOHAN	C	2026-02-14 01:09:50.595514	COMPLETED		f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010957	P-01	SINGLE	18x7-8	\N	BOSON	LUG	Premium	M-101-L		VT001	\N	AJI MOHAN	C	2026-02-14 01:09:57.707285	COMPLETED		f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010958	P-01	SINGLE	18x7-8	\N	BOSON	LUG	V3P02	M-101-L	S0006, S0007		\N	AJI MOHAN	C	2026-02-14 01:18:14.12222	PARTIAL	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010959	P-01	SINGLE	18x7-8	\N	BOSON	LUG	V3P02	M-101-L	S0006, S0007		\N	AJI MOHAN	C	2026-02-14 01:18:17.666267	PARTIAL	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010960	P-08	TOP	10.00-20	\N	TVS	LUG	V3H03	10.00-20	S0005, S0006, S0007	VT001	163.00	AJI MOHAN	A	2026-02-14 15:12:47.507796	COMPLETED	\N	f	2026-02-14 15:12:47.507648	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010961	P-08	BOT	12.00-20	\N	APT	LUG	V3H03	12.00-20	S0005, S0006, S0007	VT001	\N	AJI MOHAN	A	2026-02-14 15:13:10.154042	PARTIAL	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010962	P-08	BOT	12.00-20	\N	APT	LUG	V3H03	12.00-20	S0005, S0006, S0007	VT001	\N	AJI MOHAN	A	2026-02-14 15:13:18.414144	PARTIAL	\N	f	\N	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010963	P-08	TOP	10.00-20	\N	TVS	LUG	V3H03	10.00-20	S0006	VT001	163.00	AJI MOHAN	B	2026-02-14 20:55:31.255133	COMPLETED	\N	f	2026-02-14 20:55:31.255001	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010964	P-03	TOP	18X7.00-8	\N	VELOX	PATTERN	V3P02	18X7.00-8 B	S0007	VT001	20.60	AJI MOHAN	C	2026-02-14 23:13:42.796416	COMPLETED	\N	f	2026-02-14 23:13:42.796326	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010965	P-03	BOT	18X7.00-8	\N	CHALLENGER	LUG	V3P02	18X7.00-8 C	S0007	VT001	20.50	AJI MOHAN	C	2026-02-14 23:39:10.454825	COMPLETED	\N	f	2026-02-14 23:39:10.45472	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010966	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0006	VT001	24.50	AJI MOHAN	C	2026-02-14 23:41:54.614245	COMPLETED	\N	f	2026-02-14 23:41:54.614169	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010967	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0006	VT001	24.50	AJI MOHAN	C	2026-02-14 23:42:28.362599	COMPLETED	\N	f	2026-02-14 23:42:28.362507	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010968	P-04	BOT	140X55-9	\N	TVS	LUG	VPR02	140X55-9	S0007	VT001	10.20	AJI MOHAN	C	2026-02-15 00:09:33.436228	COMPLETED	\N	f	2026-02-15 00:09:33.436146	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010969	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT001	20.20	AJI MOHAN	C	2026-02-15 00:33:49.151349	COMPLETED	\N	f	2026-02-15 00:33:49.151259	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010970	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0005	VT001	20.20	AJI MOHAN	A	2026-02-15 10:20:34.940497	COMPLETED	\N	f	2026-02-15 10:20:34.940399	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010971	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0005	VT001	24.50	AJI MOHAN	A	2026-02-15 10:21:39.349634	COMPLETED	\N	f	2026-02-15 10:32:14.049803	\N	2026-02-15 10:32:14.049803	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010986	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0007	VT001	20.20	AJI MOHAN	B	2026-02-15 22:43:45.477302	COMPLETED	\N	f	2026-02-15 22:43:45.477224	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010972	P-08	TOP	10.00-20	\N	TVS	LUG	V3H03	10.00-20	S0006	VT001	162.80	AJI MOHAN	A	2026-02-15 10:42:25.044868	COMPLETED	\N	f	2026-02-15 10:43:23.483697	\N	2026-02-15 10:43:23.483697	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010987	P-03	TOP	18X7.00-8	\N	VELOX	PATTERN	V3P02	18X7.00-8 B	S0007, S0005	VT001	20.60	AJI MOHAN	B	2026-02-15 22:45:35.849248	COMPLETED	\N	f	2026-02-15 22:45:35.849163	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010973	P-04	BOT	140X55-9	\N	TVS	LUG	VPR02	140X55-9		VT001	10.10	AJI MOHAN	A	2026-02-15 11:41:50.203324	COMPLETED	\N	f	2026-02-15 11:43:04.801924	\N	2026-02-15 11:43:04.801924	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010974	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0007	VT001	24.40	AJI MOHAN	A	2026-02-15 11:47:05.617914	COMPLETED	\N	f	2026-02-15 11:47:30.608473	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010975	P-08	BOT	12.00-20	\N	APT	LUG	V3H03	12.00-20	S0006	VT001	193.50	AJI MOHAN	A	2026-02-15 13:54:03.641993	COMPLETED	\N	f	2026-02-15 13:54:03.64191	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010976	P-08	TOP	10.00-20	\N	TVS	LUG	V3H03	10.00-20	S0007	VT001	163.00	AJI MOHAN	A	2026-02-15 13:56:55.019383	COMPLETED	\N	f	2026-02-15 13:56:55.019306	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010977	P-06	TOP	4.00-8	\N	TVS	LUG	V3P02	4.00-8 A	S0006	VT001	10.20	AJI MOHAN	A	2026-02-15 14:14:10.654676	COMPLETED	\N	f	2026-02-15 14:14:10.654576	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010978	P-08	TOP	10.00-20	\N	TVS	LUG	V3H03	10.00-20		VT001	163.00	AJI MOHAN	B	2026-02-15 17:17:44.172591	COMPLETED	\N	f	2026-02-15 17:17:44.172495	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010979	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT001	20.20	AJI MOHAN	B	2026-02-15 18:11:22.260897	COMPLETED	\N	f	2026-02-15 18:11:22.260807	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010980	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0008	VT001	24.40	AJI MOHAN	B	2026-02-15 21:10:57.605478	COMPLETED	\N	f	2026-02-15 21:10:57.605401	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010981	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0005	VT001	24.50	AJI MOHAN	B	2026-02-15 21:54:55.953489	COMPLETED	\N	f	2026-02-15 21:54:55.95341	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010982	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0007	VT001	24.40	AJI MOHAN	B	2026-02-15 22:21:16.529245	COMPLETED	\N	f	2026-02-15 22:21:16.529158	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010983	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0007	VT001	24.50	AJI MOHAN	B	2026-02-15 22:29:39.255073	COMPLETED	\N	f	2026-02-15 22:29:39.254984	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010984	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0008	VT001	24.50	AJI MOHAN	B	2026-02-15 22:34:10.011518	COMPLETED	\N	f	2026-02-15 22:34:10.011426	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010985	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0007	VT001	24.50	AJI MOHAN	B	2026-02-15 22:38:39.18035	COMPLETED	\N	f	2026-02-15 22:38:39.180278	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010988	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0007	VT001	24.50	AJI MOHAN	B	2026-02-15 22:51:14.861203	COMPLETED	\N	f	2026-02-15 22:51:14.861125	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010989	P-03	TOP	18X7.00-8	\N	VELOX	PATTERN	V3P02	18X7.00-8 B	S0007	VT001	20.60	AJI MOHAN	B	2026-02-15 22:51:39.957077	COMPLETED	\N	f	2026-02-15 22:51:39.956983	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010990	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0007	VT001	20.20	AJI MOHAN	B	2026-02-15 22:59:24.85545	COMPLETED	\N	f	2026-02-15 22:59:24.855371	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010991	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0007	VT001	24.50	AJI MOHAN	B	2026-02-15 22:59:46.348124	COMPLETED	\N	f	2026-02-15 22:59:46.34805	\N	\N	\N	\N	\N	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010992	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0008	VT001	20.20	AJI	C	2026-02-16 02:07:08.898296	COMPLETED	\N	f	2026-02-16 02:07:08.898181	\N	\N	A1235		S0029	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010995	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0007	VT001	24.50	HANIFF	C	2026-02-16 02:10:52.462086	COMPLETED	\N	f	2026-02-16 02:10:52.462	\N	\N	A1234		S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010993	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0008	VT001	24.50	HANIFF	C	2026-02-16 02:07:47.704358	COMPLETED	\N	f	2026-02-16 02:36:34.433813	\N	\N			S0029	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010996	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0007	VT001	24.40	AJI	C	2026-02-16 02:23:11.902563	COMPLETED	\N	f	2026-02-16 02:35:04.367167	\N	\N	A1235		S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010994	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0007	VT001	24.30	HANIFF	C	2026-02-16 02:10:01.722721	COMPLETED	\N	f	2026-02-16 02:36:16.071225	\N	\N			S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010997	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT001	20.20	AJI	A	2026-02-16 09:15:05.22977	COMPLETED	\N	f	2026-02-16 09:15:05.229668	\N	\N	A1234		S0029	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010998	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0006	VT001	24.50	AJI	A	2026-02-16 09:16:05.576079	COMPLETED	\N	f	2026-02-16 09:16:05.575957	\N	\N	A1234		S0029	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-010999	P-03	TOP	18X7.00-8	\N	VELOX	PATTERN	V3P02	18X7.00-8 B	S0006	VT001	20.60	AJI	A	2026-02-16 09:16:44.333763	COMPLETED	\N	f	2026-02-16 09:16:44.333675	\N	\N	A1234		S0029, S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011000	P-04	BOT	140X55-9	\N	TVS	LUG	VPR02	140X55-9	S0008	VT001	10.20	HANIFF	A	2026-02-16 09:40:09.209466	COMPLETED	\N	f	2026-02-16 09:40:09.209379	\N	\N	A1234		S0031	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011001	P-04	BOT	140X55-9	\N	TVS	LUG	VPR02	140X55-9		VT001	10.20	AJI	A	2026-02-16 10:39:30.65048	COMPLETED	\N	f	2026-02-16 10:40:25.897157	\N	\N	A1236		S0029	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011002	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT001	20.20	HANIFF	A	2026-02-16 10:42:15.371312	COMPLETED	\N	f	2026-02-16 10:42:15.371241	\N	\N	A1235		S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011003	P-05	BOT	16X6-10-1/2	\N	BOSON	LUG	POB-PRM	16X6-10-1/2		VT002	10.80	HANIFF	A	2026-02-16 11:29:45.088759	COMPLETED	\N	t	2026-02-16 11:29:45.088646	\N	\N		BATCH-G001		0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011004	P-05	TOP	21X7.00-15	\N	APT	PATTERN	POB-PRM	21X7.00-15 A		VT002	16.90	HANIFF	A	2026-02-16 11:35:53.156646	COMPLETED	\N	t	2026-02-16 11:35:53.15654	\N	\N		BATCH-G001		0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011005	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT001	20.20	HANIFF	A	2026-02-16 11:56:59.488628	COMPLETED	\N	f	2026-02-16 11:56:59.488528	\N	\N			S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011006	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0007	VT002	20.20	HANIFF	A	2026-02-16 12:20:51.515665	COMPLETED	\N	f	2026-02-16 12:20:51.515559	\N	\N	BATCH-T009		S0031	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011007	P-05	TOP	21X7.00-15	\N	APT	PATTERN	POB-PRM	21X7.00-15 A	S0007	VT002	16.90	HANIFF	A	2026-02-16 12:21:25.138762	COMPLETED	\N	t	2026-02-16 12:21:25.13864	\N	\N	BATCH-T009	BATCH-G001	S0031	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011008	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT002	20.20	HANIFF	A	2026-02-16 12:35:17.178347	COMPLETED	\N	f	2026-02-16 12:35:17.178263	\N	\N	BATCH-T009		S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011009	P-05	BOT	16X6-10-1/2	\N	BOSON	LUG	POB-PRM	16X6-10-1/2		VT002	10.80	HANIFF	A	2026-02-16 12:35:53.707552	COMPLETED	\N	t	2026-02-16 12:35:53.707449	\N	\N		BATCH-G001		0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011010	P-05	TOP	21X7.00-15	\N	APT	PATTERN	POB-PRM	21X7.00-15 A		VT001	16.90	RAJENDRA	A	2026-02-16 12:40:43.700747	COMPLETED	\N	t	2026-02-16 12:40:43.700664	\N	\N	A1235	BATCH-G001		0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011011	P-04	TOP	15X4.50-8	\N	BOSON	LUG	VPR02	15X4.50-8		VT001	10.80	RAJENDRA	A	2026-02-16 12:46:34.021367	COMPLETED	\N	f	2026-02-16 12:46:34.021262	\N	\N				0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011012	P-08	TOP	10.00-20	\N	TVS	LUG	V3H03	10.00-20	S0006	VT002	163.00	HANIFF	A	2026-02-16 12:51:05.529766	COMPLETED	\N	f	2026-02-16 12:51:05.52966	\N	\N			S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011013	P-08	BOT	12.00-20	\N	APT	LUG	V3H03	12.00-20	S0007	VT002	194.00	RAJENDRA	A	2026-02-16 12:52:50.663158	COMPLETED	\N	f	2026-02-16 12:52:50.663065	\N	\N	BATCH-T009		S0031	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011014	P-03	TOP	18X7.00-8	\N	VELOX	PATTERN	V3P02	18X7.00-8 B	S0008	VT002	20.60	HANIFF	A	2026-02-16 14:22:28.442528	COMPLETED	\N	f	2026-02-16 14:22:28.442419	\N	\N	BATCH-T009		S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011015	P-04	TOP	15X4.50-8	\N	BOSON	LUG	VPR02	15X4.50-8		VT001	10.80	HANIFF	A	2026-02-16 14:24:42.497488	COMPLETED	\N	f	2026-02-16 14:24:42.497414	\N	\N				0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011016	P-05	TOP	21X7.00-15	\N	APT	PATTERN	POB-PRM	21X7.00-15 A		VT001	16.90	HANIFF	B	2026-02-16 20:54:34.482281	COMPLETED	\N	t	2026-02-16 20:54:34.482187	\N	\N	A1235	BATCH-G001		0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011017	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0005	VT001	20.20	HANIFF	B	2026-02-17 18:02:29.729627	COMPLETED	\N	f	2026-02-17 18:02:29.729505	\N	\N	A1235		S0029, S0032	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011018	P-04	BOT	140X55-9	\N	TVS	LUG	VPR02	140X55-9	S0006	VT001	10.20	RAJENDRA	B	2026-02-17 18:25:47.375191	COMPLETED	\N	f	2026-02-17 18:25:47.375097	\N	\N			S0029	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011019	P-02	SINGLE	6.00-9	\N	TVS	LUG	V3P02	6.00-9 B	S0008	VT001	24.50	RAJENDRA	B	2026-02-17 18:59:14.526897	COMPLETED	\N	f	2026-02-17 18:59:14.526793	\N	\N	A1235		S0031	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011020	P-04	BOT	140X55-9	\N	TVS	LUG	VPR02	140X55-9		VT002	10.20	HANIFF	B	2026-02-17 19:08:55.775943	COMPLETED	\N	f	2026-02-17 19:08:55.775839	\N	\N	BATCH-T002			0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011021	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT002	20.20	RAJENDRA	B	2026-02-17 20:34:20.949863	COMPLETED	\N	f	2026-02-17 20:34:20.949779	\N	\N	BATCH-T009		S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011022	P-04	BOT	140X55-9	\N	TVS	LUG	VPR02	140X55-9	S0006	VT001	11.00	RAJENDRA	B	2026-02-17 21:00:08.829257	COMPLETED	\N	f	2026-02-17 21:00:08.829145	\N	\N			S0029	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011023	P-04	BOT	140X55-9	\N	TVS	LUG	VPR02	140X55-9	S0007	VT001	11.00	RAJENDRA	B	2026-02-17 21:05:54.966752	COMPLETED	\N	f	2026-02-17 21:05:54.966667	\N	\N			S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011024	P-04	BOT	140X55-9	\N	TVS	LUG	VPR02	140X55-9		VT001	11.00	HANIFF	B	2026-02-17 21:06:40.714415	COMPLETED	\N	f	2026-02-17 21:06:40.714337	\N	\N	A1235			0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011025	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT001	30.00	HANIFF	B	2026-02-17 21:08:34.178217	COMPLETED	\N	f	2026-02-17 21:08:34.1781	\N	\N	A1234		S0029	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011026	P-08	TOP	10.00-20	\N	TVS	LUG	V3H03	10.00-20	S0006	VT002	164.00	LAKSHMI	B	2026-02-17 21:37:26.529359	COMPLETED	\N	f	2026-02-17 21:37:26.529267	\N	\N	BATCH-T009		S0031	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011027	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0007	VT002	20.20	HANIFF	C	2026-02-18 01:20:04.490624	COMPLETED	\N	f	2026-02-18 01:20:04.490465	\N	\N			S0030	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011028	P-03	TOP	18X7.00-8	\N	VELOX	PATTERN	V3P02	18X7.00-8 B	S0006	VT001	20.60	HANIFF	A	2026-02-18 09:20:45.54534	COMPLETED	\N	f	2026-02-18 09:20:45.545232	\N	\N	A1235		S0029	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011029	P-05	TOP	21X7.00-15	\N	APT	PATTERN	POB-PRM	21X7.00-15 A		VT001	16.90	HANIFF	A	2026-02-18 09:23:04.769367	COMPLETED	\N	t	2026-02-18 09:23:04.769272	\N	\N		BATCH-G001		0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011030	P-03	TOP	18X7.00-8	\N	VELOX	PATTERN	V3P02	18X7.00-8 B	S0006	VT001	20.60	HANIFF	A	2026-02-18 09:35:23.384038	COMPLETED	\N	f	2026-02-18 09:35:23.38394	\N	\N	A1235		S0031	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011031	P-05	BOT	16X6-10-1/2	\N	BOSON	LUG	POB-PRM	16X6-10-1/2		VT001	23.30	HANIFF	B	2026-02-19 21:55:39.623693	COMPLETED	\N	t	2026-02-19 21:55:39.623593	\N	\N	A1235	BATCH-G001		12.50	\N	\N	\N	\N	\N	COMPLETE	\N
B-011032	P-05	BOT	16X6-10-1/2	\N	BOSON	LUG	POB-PRM	16X6-10-1/2		VT001	22.00	HANIFF	B	2026-02-19 22:28:39.15243	COMPLETED	\N	t	2026-02-19 22:28:39.152342	\N	\N	A1236	BATCH-G001		11.20	Rim Bulging	\N	\N	\N	\N	COMPLETE	\N
B-011033	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT002	20.20	HANIFF	B	2026-02-19 22:29:24.925264	COMPLETED	\N	f	2026-02-19 22:29:48.460838	\N	\N	BATCH-T010		S0030	0.00		\N	\N	\N	\N	COMPLETE	\N
B-011034	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT002	20.40	HANIFF	A	2026-02-20 09:09:59.593861	COMPLETED	\N	f	2026-02-20 09:10:50.041435	\N	\N	BATCH-T010		S0029	0.00		\N	\N	\N	\N	COMPLETE	\N
B-011035	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A	S0006	VT001	20.40	HANIFF	A	2026-02-22 10:33:44.147215	COMPLETED	\N	f	2026-02-22 10:34:28.381302	\N	\N	A1235		S0030	0.00		\N	\N	\N	\N	COMPLETE	\N
B-011036	P-07	SINGLE	6.50-10	\N	VELOX	—	VPR01	—	S0007	VT002	34.80	HANIFF	A	2026-02-22 11:23:35.920483	COMPLETED	\N	f	2026-02-22 11:23:35.920388	\N	\N	BATCH-T009		S0030	0.00	FIRST TYRE	5	\N	\N	\N	COMPLETE	\N
B-011037	P-07	SINGLE	6.50-10	\N	VELOX	—	VPR01	—		VT002	34.80	RAJENDRA	A	2026-02-22 11:27:10.341759	COMPLETED	\N	f	2026-02-22 11:27:10.341676	\N	\N	BATCH-T009			0.00		5	\N	\N	\N	COMPLETE	\N
B-011038	P-07	SINGLE	6.50-10	\N	VELOX	—	VPR01	—		VT001	34.80	HANIFF	A	2026-02-22 11:32:01.931837	COMPLETED	\N	f	2026-02-22 11:32:01.931729	\N	\N	A1235		S0031	0.00		5	\N	\N	\N	COMPLETE	\N
B-011039	P-01	SINGLE	18X7.00-8	\N	BOSON	LUG	V3P02	18X7.00-8 A		VT002	20.20	HANIFF	B	2026-02-23 20:42:35.004061	COMPLETED	\N	f	2026-02-23 20:42:35.003972	\N	\N	BATCH-T002			0.00		\N	\N	\N	\N	COMPLETE	\N
B-011040	P-01	SINGLE	16X6-8	\N	BOSON	—	PREMIUM	—		VT001	14.50	HANIFF	A	2026-02-24 08:40:35.486964	COMPLETED	\N	f	2026-02-24 08:40:35.486851	\N	\N	A1235		S0030	0.00		1	\N	\N	\N	COMPLETE	\N
B-011041	P-04	TOP	15X4.5-8	\N	BOSON	LUG	VPR02	15X4.50-8		VT001	10.80	RAJENDRA	A	2026-02-24 08:41:53.406418	COMPLETED	\N	f	2026-02-24 08:41:53.406313	\N	\N	A1236		S0030	0.00		\N	\N	\N	\N	COMPLETE	\N
B-011042	P-01	SINGLE	7.00-12	\N	PAREX	—	V3H03	—	S0006	VT001	45.00	HANIFF	B	2026-02-26 22:42:27.518972	COMPLETED	\N	f	2026-02-26 22:42:27.51888	\N	\N	A1235		S0030	0.00		7	\N	\N	\N	COMPLETE	\N
B-011043	P-01	SINGLE	7.00-12	\N	PAREX	—	V3H03	—	S0006	VT002	45.00	HANIFF	B	2026-02-26 22:44:11.12501	COMPLETED	\N	f	2026-02-26 22:44:11.124904	\N	\N	BATCH-T009		S0030	0.00		7	\N	\N	\N	COMPLETE	\N
B-011044	P-01	SINGLE	7.00-12	\N	PAREX	—	V3H03	—	S0007	VT002	45.00	HANIFF	B	2026-02-26 22:44:33.926648	COMPLETED	\N	f	2026-02-26 23:02:12.180364	\N	\N	BATCH-T009		S0031	0.00		7	\N	\N	\N	COMPLETE	\N
B-011045	P-01	SINGLE	7.00-12	\N	PAREX	—	V3H03	—	S0007	VT002	\N	HANIFF	C	2026-02-26 23:02:43.363598	PARTIAL	\N	f	\N	\N	\N			S0031	0.00		7	\N	\N	\N	COMPLETE	\N
B-011046	P-01	SINGLE	7.00-12	\N	PAREX	—	V3H03	—	S0007	VT001	\N	HANIFF	C	2026-02-26 23:03:12.084878	COMPLETED	\N	f	2026-02-26 23:03:12.084782	\N	\N			S0030	0.00		7	\N	\N	\N	COMPLETE	\N
B-011047	P1	SINGLE	7.00-12	\N	PAREX	\N	V3H03	\N	M1100	VT001	45.00	Aji Mohan	\N	2026-02-27 16:10:04.543034	COMPLETED	\N	f	\N	\N	\N	\N	\N	A11, A12	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011048	P4	TOP	15X4.5-8	\N	BOSON	\N	VPR02	\N	M1100	VT001	10.80	Aji Mohan	\N	2026-02-27 16:10:49.871152	COMPLETED	\N	f	\N	\N	\N	\N	\N	A11	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011049	P1	SINGLE	7.00-12	\N	PAREX	\N	V3H03	\N	M1100	VT001	45.00	Aji Mohan	\N	2026-02-27 16:11:32.110682	COMPLETED	\N	f	\N	\N	\N	\N	\N	A11	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011050	P1	SINGLE	7.00-12	\N	PAREX	\N	V3H03	\N	M1100	VT001	45.00	Aji Mohan	\N	2026-02-27 16:13:09.234643	COMPLETED	\N	f	\N	\N	\N	\N	\N	A11	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011051	P2	SINGLE	6.00-9	\N	TVS	\N	V3P02	\N	M1106	VT001	24.50	Aji Mohan	\N	2026-02-27 16:13:37.848483	COMPLETED	\N	f	\N	\N	\N	\N	\N	A11	0.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011053	P-01	SINGLE	7.00-12	\N	PAREX	\N	V3H03	\N	M1100	VT001	0.00	Aji Mohan	\N	2026-02-27 16:36:41.294646	PARTIAL	\N	f	\N	\N	\N	\N	\N	A11	0.00	\N	7	\N	\N	\N	COMPLETE	\N
B-011055	P-01	SINGLE	7.00-12	\N	PAREX	\N	V3H03	\N	M1100	VT001	45.00	Aji Mohan	\N	2026-02-27 16:49:37.907153	COMPLETED	\N	f	\N	\N	\N	\N	\N	A11	0.00	\N	7	\N	\N	\N	COMPLETE	\N
B-011056	P-01	SINGLE	7.00-12	\N	PAREX	\N	V3H03	\N	M1105	VT001	45.00	Aji Mohan	\N	2026-02-27 17:07:22.34745	COMPLETED	\N	f	2026-02-27 17:38:34.961178	\N	\N	V1129	\N	A11	0.00	\N	7	\N	\N	\N	COMPLETE	\N
B-011054	P-01	SINGLE	7.00-12	\N	PAREX	\N	V3H03	\N	M1100	VT001	45.00	Aji Mohan	\N	2026-02-27 16:45:01.462104	COMPLETED	\N	f	2026-02-27 17:41:52.786624	\N	\N	V1129	\N	A11	0.00	\N	7	\N	\N	\N	COMPLETE	\N
B-011057	P-01	SINGLE	7.00-12	5.00"	PAREX	\N	V3H03	\N	BATCH-M013	VT001	45.00	Aji Mohan	B	2026-02-27 18:22:39.568705	COMPLETED	\N	f	2026-02-27 18:22:39.568601	\N	\N	V1129		S0036	0.00	\N	7	\N	\N	\N	COMPLETE	\N
B-011052	P-01	SINGLE	7.00-12	\N	PAREX	\N	V3H03	\N	M1100	VT001	45.00	Aji Mohan	\N	2026-02-27 16:25:50.156775	COMPLETED	\N	f	2026-02-27 18:23:07.271637	\N	\N	V1129	\N	A11	0.00	\N	7	\N	\N	\N	COMPLETE	\N
B-011058	P-01	SINGLE	7.00-12	5.00"	PAREX	\N	V3H03	\N	BATCH-M013	VT001	45.00	Aji Mohan	B	2026-02-27 20:54:45.279078	COMPLETED	\N	f	2026-02-27 20:55:14.402452	\N	\N	V1129		S0036	0.00	\N	7	\N	\N	\N	COMPLETE	\N
B-011059	P-01	SINGLE	7.00-12	5.00"	PAREX	\N	V3H03	\N	BATCH-M013, BATCH-M012	VT002	45.00	Aji Mohan	B	2026-02-27 21:13:20.702944	COMPLETED	\N	f	2026-02-27 21:13:20.702817	\N	\N	VT25, VT24		S0035, S0034, BATCH-C024	0.00	\N	7	\N	\N	\N	COMPLETE	\N
B-011060	P-01	SINGLE	7.00-12	5.00"	PAREX	\N	V3H03	\N		VT001	\N	Aji Mohan	C	2026-02-27 23:03:29.93847	COMPLETED	\N	f	2026-02-27 23:03:29.938347	\N	\N	V1129, V1127		A19	0.00	\N	7	\N	\N	\N	COMPLETE	\N
B-011061	P-05	BOT	16X6-10-1/2	—	BOSON	LUG	POB-PRM	16X6-10-1/2		VT001	24.80	Aji Mohan	C	2026-02-28 01:53:21.847009	COMPLETED	\N	t	2026-02-28 01:53:21.846924	\N	\N	V1001	G001		14.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011062	P-05	BOT	16X6-10-1/2	—	BOSON	LUG	POB-PRM	16X6-10-1/2		VT001	24.80	Aji Mohan	C	2026-02-28 01:54:39.344435	COMPLETED	\N	t	2026-02-28 01:54:39.34434	\N	\N	V1001	G001		14.00	\N	\N	\N	\N	\N	COMPLETE	\N
B-011063	P-01	SINGLE	7.00-12	—	PAREX	—	V3H03	—		VT001	45.00	Aji Mohan	A	2026-02-28 09:13:53.832248	COMPLETED	\N	f	2026-02-28 09:13:53.832138	\N	\N	V1001		A14	\N	\N	7	\N	\N	\N	COMPLETE	\N
B-011064	P-05	BOT	16X6-10-1/2	—	BOSON	LUG	POB-PRM	16X6-10-1/2		VT001	28.00	Aji Mohan	A	2026-02-28 09:35:29.123349	COMPLETED	\N	t	2026-02-28 09:35:29.123267	\N	\N	V1001	G001		14.00	\N	\N	\N	\N	\N	COMPLETE	\N
\.


--
-- Data for Name: pc1_mould_mapping; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pc1_mould_mapping (id, tyre_size, mould_id, pattern) FROM stdin;
1	6.50-10	6.50-10 A	\N
2	6.50-10	6.50-10 B	\N
3	9.00-10	9.00-10 A	\N
4	9.00-10	9.00-10 B	\N
5	10.00-20	M-101	\N
6	10.00-20	M-102	\N
7	10.00-20	M-105	\N
8	400X100X310	400X100X310	\N
9	3.50-4	3.50-4	\N
10	12X4.00-4	12X4.00-4	\N
11	15X4.5-8	15X4.5-8	\N
12	140X55-9	140X55-9	\N
13	140X55-9	140X55-9 RIB	\N
14	4.00-8	4.00-8 A	\N
15	4.00-8	4.00-8 B	\N
16	16X6.00-8	16X6.00-8	\N
17	5.00-8	5.00-8 A	\N
18	5.00-8	5.00-8 B	\N
19	5.00-8	5.00-8 C	\N
20	180X60-10	180X60-10	\N
21	200X50-10	200X50-10	\N
22	18X7.00-8	18X7.00-8 A	\N
23	18X7.00-8	18X7.00-8 B	\N
24	18X7.00-8	18X7.00-8 C	\N
25	18X7.00-8	18X7.00-8 D	\N
26	6.00-9	6.00-9 A	\N
27	6.00-9	6.00-9 B	\N
28	6.00-9	6.00-9 C	\N
29	6.00-9	6.00-9 D	\N
30	21X8.00-9	21X8.00-9	\N
31	6.50-10	6.50-10 A	\N
32	6.50-10	6.50-10 B	\N
33	6.50-10	6.50-10 C	\N
34	6.50-10	6.50-10 D	\N
35	6.50-10	6.50-10 E	\N
36	6.50-10	6.50-10 F	\N
37	6.50-10	6.50-10 A	\N
38	6.50-10	6.50-10 B	\N
39	6.50-10	6.50-10 C	\N
40	6.50-10	6.50-10 E	\N
41	6.50-10	6.50-10 F	\N
42	23X9.00-10	23X9.00-10 A	\N
43	23X9.00-10	23X9.00-10 B	\N
44	23X10-12	23X10-12	\N
45	28X9.00-16	28X9.00-16	\N
46	7.00-12	7.00-12 A	\N
47	7.00-12	7.00-12 B	\N
48	7.00-12	7.00-12 C	\N
49	7.00-12	7.00-12 D	\N
50	7.00-12	7.00-12 E	\N
51	27X10.00-12	27X10.00-12	\N
52	8.15-15	8.15-15 A	\N
53	8.15-15	8.15-15 B	\N
54	8.15-15	8.15-15 C	\N
55	8.15-15	8.15-15 D	\N
56	28X9.00-15	28X9.00-15 A	\N
57	28X9.00-15	28X9.00-15 B	\N
58	28X9.00-15	28X9.00-15 C	\N
59	28X9.00-15	28X9.00-15 D	\N
60	28X9.00-15	28X9.00-15 E	\N
61	28X12.50-15	28X12.50-15	\N
62	29X7.00-15	29X7.00-15 A	\N
63	29X7.00-15	29X7.00-15 B	\N
64	29X7.00-15	29X7.00-15 B	\N
65	29X7.00-15	29X7.00-15 C	\N
66	29X7.00-15	29X7.00-15 D	\N
67	29X7.50-15	29X7.50-15 A	\N
68	29X7.50-15	29X7.50-15 B	\N
69	29X7.50-15	29X7.50-15 C	\N
70	29X7.50-15	29X7.50-15 C	\N
71	7.50-16	7.50-16 A	\N
72	7.50-16	7.50-16 B	\N
73	8.25-15	8.25-15 A	\N
74	8.25-15	8.25-15 B	\N
75	8.25-15	8.25-15 C	\N
76	32X8.25-16	32X8.25-16 A	\N
77	32X8.25-16	32X8.25-16 C	\N
78	32X300-15	32X300-15	\N
79	32X12.00-20	32X12.00-20	\N
80	355X45-15	355X45-15	\N
81	355X55-15	355X55-15	\N
82	355X65-15	355X65-15	\N
83	39X9.00-20	39X9.00-20	\N
84	10.00-20	10.00-20	\N
85	10.00-20	10.00-20	\N
86	40X11.00-20	40X11.00-20	\N
87	40X11.00-20	40X11.00-20	\N
88	12.00-20	12.00-20	\N
89	12.00-20	12.00-20	\N
90	355X50-15	355X50-15	\N
91	28X8.15[9.00]- 15	28X8.15[9.00]- 15	\N
92	18X8 -12-1/8	18X8 -12-1/8	\N
93	29X250-15	29X250-15	\N
94	29X250-15	29X250-15	\N
95	15X5X11 1/4	15X5X11 1/4	\N
96	16X7X10-1/2	16X7X10-1/2	\N
97	10X5X6-1/4	10X5X6-1/4	\N
98	10X6X6-1/4	10X6X6-1/4	\N
99	16X5X10-1/2	16X5X10-1/2	\N
100	16X6X10-1/2	16X6X10-1/2 A	\N
101	16X6X10-1/2	16X6X10-1/2 B	\N
102	16-1/4X5X11-1/4	16-1/4X5X11-1/4	\N
103	16-1/4X6X11-1/4	16-1/4X6X11-1/4 A	\N
104	16-1/4X6X11-1/4	16-1/4X6X11-1/4 B	\N
105	16-1/4X7X11-1/4	16-1/4X7X11-1/4 A	\N
106	16-1/4X7X11-1/4	16-1/4X7X11-1/4 B	\N
107	17-1/4X5X11-1/4	17-1/4X5X11-1/4	\N
108	17-1/4X6X11-1/4	17-1/4X6X11-1/4	\N
109	18X5X12-1/8	18X5X12-1/8	\N
110	18X6X12-1/8	18X6X12-1/8	\N
111	18X7X12-1/8	18X7X12-1/8	\N
112	18X8X12-1/8	18X8X12-1/8	\N
113	18X9X12-1/8	18X9X12-1/8	\N
114	21X5.00X15	21X5.00X15	\N
115	21X6.00X15	21X6.00X15	\N
116	21X7.00X15	21X7.00X15 A	\N
117	21X7.00X15	21X7.00X15 B	\N
118	21X8.00- 15	21X8.00- 15 A	\N
119	21X8.00- 15	21X8.00- 15 B	\N
120	21X9.00X15	21X9.00X15 C	\N
121	21X9.00X15	21X9.00X15 C	\N
122	22X6.00X16	22X6.00X16	\N
123	22X6.00X17-3/4	22X6.00X17-3/4	\N
124	22X7.00X17-3/4	22X7.00X17-3/4	\N
125	15X5	15X5	\N
126	16X6- 11 1/2	16X6- 11 1/2	\N
127	22X9.00- 16	22X9.00- 16	\N
128	22X10.00- 16	22X10.00- 16	\N
129	31X10.00- 16	31X10.00- 16	\N
130	23X12.00-12	23X12.00-12	\N
131	22X8.00- 16	22X8.00- 16	\N
132	22X12.00- 16	22X12.00- 16	\N
133	31X10.00-20	31X10.00-20	\N
\.


--
-- Data for Name: pc2_curing; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pc2_curing (c_id, b_id, serial_no, process_type, press_no, mould_no, operator_id, status, green_weight, final_weight, flash_waste, start_time, press_finish_time, oven_start_time, oven_finish_time, qc_grade, qc_remarks, temperature, pressure, is_oven, final_cured_weight, visual_qc_status, visual_qc_remarks, curing_time_minutes, end_time, idle_time_minutes, overcure_minutes, operator_name, supervisor_name, core_hardness_min, core_hardness_max, tread_hardness_min, tread_hardness_max, qc_defects, qc_engineer, qc_time, shift, press_machine) FROM stdin;
5	B-010973	F010002 0726	STANDARD	P-04	BOT	\N	DONE	\N	\N	0.30	2026-02-15 13:27:29.751848	\N	\N	\N	\N	\N	142	150	f	9.80	OK		150	2026-02-15 13:32:54.50987	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
6	B-010971	F010003 0726	STANDARD	P-02	SINGLE	\N	DONE	\N	\N	0.50	2026-02-15 13:33:39.509152	\N	\N	\N	\N	\N	160	150	f	24.00	OK		150	2026-02-15 13:34:16.394263	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
7	B-010970	F010004 0726	STANDARD	P-01	SINGLE	\N	DONE	\N	\N	1.30	2026-02-15 13:35:13.453538	\N	\N	\N	\N	\N	160	150	f	18.90	OK		180	2026-02-15 13:35:46.820766	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
16	B-010977	F010013 0726	STANDARD	P-06	TOP	\N	DONE	\N	\N	0.00	2026-02-15 14:15:08.906255	\N	\N	\N	\N	\N	160	150	f	10.20	REJECT		90	2026-02-15 14:15:55.827343	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
17	B-010978	F010014 0726	STANDARD	P-08	TOP	\N	DONE	\N	\N	0.90	2026-02-15 17:18:41.729082	\N	\N	\N	\N	\N	160	150	f	162.10	OK	unfill	320	2026-02-15 17:19:09.563103	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
15	B-0109769	F010012 0726	STANDARD	P-08	TOP	\N	DONE	\N	\N	3.00	2026-02-15 13:57:17.068204	\N	\N	\N	\N	\N	160	150	f	160.00	OK		320	2026-02-15 17:20:16.66845	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
14	B-010975	F010011 0726	STANDARD	P-08	BOT	\N	DONE	\N	\N	3.00	2026-02-15 13:54:41.24559	\N	\N	\N	\N	\N	160	150	f	160.00	OK		320	2026-02-15 17:20:46.508216	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
34	B-010996	F010031 0726	STANDARD	OVEN-1 (P-02-SINGLE)	6.00-9 A	\N	QC_OK	\N	\N	0.00	2026-02-16 02:38:25.559594	\N	\N	\N	\N	\N	160	N/A	t	24.40	OK		180	2026-02-16 02:38:48.066931	0	0	LAKSHMI	Bijoy	80	82	68	72	DD001 - UNDER CURE	Bijoy	2026-02-16 02:40:49.159031	\N	\N
43	B-011017	F010041 0726	STANDARD	P-01-SINGLE	18X7.00-8 A	\N	QC_OK	20.20	\N	0.20	2026-02-17 18:04:08.166384	\N	\N	\N	\N	\N	160	150	f	20.00	OK		180	2026-02-17 18:05:40.21762	1933	0	HANIFF	Bijoy	80	82	68	72	DD004 - SIZE/ GRADE PLATE CHANGES|DI014 - ONE SIDE WIDTH	Bijoy	2026-02-17 18:08:34.233537	\N	\N
2	B-010973	F010002 0126	STANDARD	P1-B		\N	DONE	10.10	\N	0.10	2026-02-15 12:57:44.075673	\N	\N	\N	\N	\N	\N	\N	f	10.00	OK		45	2026-02-16 20:34:03.822958	\N	1851	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
18	B-010979	F010015 0726	STANDARD	OVEN-1	18X7.00-8 A	\N	DONE	\N	\N	0.00	2026-02-15 19:01:59.816177	\N	\N	\N	\N	\N	160	200	t	20.20	OK		45	2026-02-15 20:37:46.142698	0	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
1	B-010974	F010001 0126	STANDARD	P1-B		\N	DONE	24.40	\N	0.20	2026-02-15 12:56:54.478572	\N	\N	\N	\N	\N	\N	\N	f	24.20	OK		45	2026-02-15 20:43:08.447895	\N	421	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
20	B-010981	F010017 0726	STANDARD	P-02-SINGLE	6.00-9 A	\N	DONE	\N	\N	0.50	2026-02-15 22:15:41.723704	\N	\N	\N	\N	\N	160	150	f	24.00	OK		45	2026-02-15 23:48:20.974658	0	47	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
21	B-010982	F010018 0726	STANDARD	P-02-SINGLE	6.00-9 A	\N	DONE	\N	\N	0.00	2026-02-15 22:23:04.53493	\N	\N	\N	\N	\N	160	150	f	0.00	REJECT		45	2026-02-15 23:48:46.642923	0	40	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
22	B-010983	F010019 0726	STANDARD	P-02-SINGLE	6.00-9 A	\N	DONE	\N	\N	0.00	2026-02-15 22:29:55.903696	\N	\N	\N	\N	\N	160	150	f	24.50	MILD		45	2026-02-15 23:49:07.248641	0	34	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
24	B-010985	F010021 0726	STANDARD	OVEN-1	6.00-9 A	\N	DONE	\N	\N	0.50	2026-02-15 22:42:22.381793	\N	\N	\N	\N	\N	160	N/A	t	24.00	OK		180	2026-02-15 23:49:51.648752	124	0	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
19	B-010980	F010016 0726	STANDARD	P2	6.00-9 C	\N	DONE	\N	\N	0.40	2026-02-15 21:12:44.538471	\N	\N	\N	\N	\N	160	400	t	24.00	OK		120	2026-02-16 09:30:57.975716	0	618	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
25	B-010986	F010022 0726	STANDARD	P-01	18X7.00-8 A	\N	QC_OK	\N	\N	0.20	2026-02-15 22:44:22.279402	\N	\N	\N	\N	\N	160	150	f	20.00	OK		45	2026-02-15 23:57:44.44628	548	28	\N	\N	80	82	68	72	DD008 - UNDER WEIGHT	AJIMOHAN	2026-02-16 00:35:45.541207	\N	\N
23	B-010984	F010020 0726	STANDARD	P-02-SINGLE	6.00-9 A	\N	QC_OK	\N	\N	0.50	2026-02-15 22:36:24.333316	\N	\N	\N	\N	\N	160	150	f	24.00	OK		45	2026-02-15 23:49:32.484672	0	28	\N	\N	80	82	68	72	DD005 - CORE SIZE CHANGE	AJIMOHAN	2026-02-16 01:16:08.717147	\N	\N
33	B-010994	F010030 0726	STANDARD	OVEN-1 (P-02-SINGLE)	6.00-9 A	\N	DONE	\N	\N	0.30	2026-02-16 02:37:47.630999	\N	\N	\N	\N	\N	160	N/A	t	24.00	OK		180	2026-02-16 09:32:10.17482	0	234	LAKSHMI	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
32	B-010993	F010029 0726	STANDARD	OVEN-1 (P-02-SINGLE)	6.00-9 A	\N	DONE	\N	\N	0.50	2026-02-16 02:12:20.36323	\N	\N	\N	\N	\N	160	N/A	t	24.00	OK		180	2026-02-16 09:33:01.517477	0	260	RAJENDRA	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
31	B-010992	F010028 0726	STANDARD	P-01-SINGLE	18X7.00-8 A	\N	DONE	\N	\N	0.20	2026-02-16 02:11:50.365382	\N	\N	\N	\N	\N	160	150	f	20.00	OK		45	2026-02-16 09:33:23.614423	0	396	RAJENDRA	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
30	B-010990	F010027 0726	STANDARD	P-01-SINGLE	18X7.00-8 A	\N	DONE	\N	\N	0.20	2026-02-15 23:39:16.248424	\N	\N	\N	\N	\N	160	150	f	20.00	OK		45	2026-02-16 09:50:10.797265	0	565	HANIFF	SUPERVISOR	\N	\N	\N	\N	\N	\N	\N	\N	\N
29	B-010991	F010026 0726	STANDARD	OVEN-1 (P-02-SINGLE)	6.00-9 A	\N	DONE	\N	\N	0.20	2026-02-15 23:38:54.520169	\N	\N	\N	\N	\N	160	N/A	t	24.30	OK		180	2026-02-16 12:25:26.028284	0	586	HANIFF	SUPERVISOR	\N	\N	\N	\N	\N	\N	\N	\N	\N
28	B-010989	F010025 0726	STANDARD	P-03-TOP	18X7.00-8 A	\N	DONE	\N	\N	0.20	2026-02-15 22:52:24.995275	\N	\N	\N	\N	\N	160	150	f	20.40	OK		45	2026-02-16 12:25:50.488417	0	768	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
27	B-010988	F010024 0726	STANDARD	OVEN-1 (P-02-SINGLE)	6.00-9 A	\N	DONE	\N	\N	0.20	2026-02-15 22:52:07.25085	\N	\N	\N	\N	\N	160	N/A	t	24.30	OK		180	2026-02-16 12:26:24.140448	0	634	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
26	B-010987	F010023 0726	STANDARD	P-03	18X7.00-8 A	\N	DONE	\N	\N	0.20	2026-02-15 22:46:11.967644	\N	\N	\N	\N	\N	160	150	f	20.40	OK		45	2026-02-16 12:26:49.790689	0	775	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
38	B-011007	F010035 0726	STANDARD	P-05-TOP	18X7.00-8 A	\N	DONE	\N	\N	0.10	2026-02-16 12:24:00.846409	\N	\N	\N	\N	\N	160	150	f	16.80	OK		45	2026-02-16 12:29:54.64135	0	0	LAKSHMI	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
13	B-010968	F010010 0726	STANDARD	P-04	BOT	\N	DONE	\N	\N	0.00	2026-02-15 13:46:54.658587	\N	\N	\N	\N	\N	160	150	f	10.20	OK		45	2026-02-16 20:22:57.413497	\N	1791	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
12	B-010968	F010009 0726	STANDARD	P-04	BOT	\N	DONE	\N	\N	0.00	2026-02-15 13:45:37.339761	\N	\N	\N	\N	\N	160	150	f	10.20	OK		45	2026-02-16 20:23:21.023748	\N	1792	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
11	B-010968	F010008 0726	STANDARD	P-04	BOT	\N	DONE	\N	\N	0.00	2026-02-15 13:37:31.017271	\N	\N	\N	\N	\N	160	150	f	10.20	OK		45	2026-02-16 20:23:46.600816	\N	1801	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
10	B-010968	F010007 0726	STANDARD	P-04	BOT	\N	DONE	\N	\N	0.20	2026-02-15 13:37:17.191246	\N	\N	\N	\N	\N	160	150	f	10.00	OK		45	2026-02-16 20:24:26.964003	\N	1802	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
9	B-010968	F010006 0726	STANDARD	P-04	BOT	\N	DONE	\N	\N	0.20	2026-02-15 13:37:02.568396	\N	\N	\N	\N	\N	160	150	f	10.00	OK		45	2026-02-16 20:24:52.557552	\N	1802	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
8	B-010968	F010005 0726	STANDARD	P-04	BOT	\N	DONE	\N	\N	0.20	2026-02-15 13:36:45.408267	\N	\N	\N	\N	\N	160	150	f	10.00	OK		45	2026-02-16 20:25:17.35873	\N	1803	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
4	B-010973	F010001 0626	STANDARD	P-04	BOT	\N	DONE	\N	\N	0.10	2026-02-15 13:18:25.158709	\N	\N	\N	\N	\N	160	150	f	10.00	OK		45	2026-02-16 20:33:06.908544	\N	1829	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3	B-010972	F010003 0126	STANDARD	P1-B		\N	DONE	162.80	\N	0.80	2026-02-15 12:58:15.470658	\N	\N	\N	\N	\N	\N	\N	f	162.00	OK		45	2026-02-16 20:33:38.766341	\N	1850	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
41	B-011015	F010038 0726	STANDARD	P-04-TOP		\N	DONE	10.80	\N	0.30	2026-02-16 14:55:24.559883	\N	\N	\N	\N	\N	160	150	f	10.50	OK		45	2026-02-16 20:34:58.342115	0	294	HANIFF	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
40	B-011012	F010037 0726	STANDARD	P-08-TOP	10.00-20	\N	DONE	\N	\N	0.30	2026-02-16 13:14:01.888592	\N	\N	\N	\N	\N	160	150	f	10.50	OK		45	2026-02-16 20:36:54.382022	0	397	HANIFF	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
42	B-011016	F010039 0726	STANDARD	P-05-TOP		\N	DONE	16.90	\N	0.10	2026-02-16 20:55:01.760089	\N	\N	\N	\N	\N	160	150	f	16.80	OK		120	2026-02-17 18:28:33.632219	505	1173	LAKSHMI	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
47	B-011022	F010045 0726	STANDARD	P-04-BOT	140X55-9	\N	COOLING	11.00	\N	\N	2026-02-17 21:00:54.731155	\N	\N	\N	\N	\N	160	150	f	\N	\N	\N	45	2026-02-17 21:56:40.793474	153	11	LAKSHMI	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
37	B-011006	F010034 0726	STANDARD	P-01-SINGLE	18X7.00-8 A	\N	DONE	\N	\N	0.20	2026-02-16 12:22:07.639193	\N	\N	\N	\N	\N	160	150	f	20.00	OK		45	2026-02-17 19:28:47.913051	151	1821	LAKSHMI	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
45	B-011019	F010043 0726	STANDARD	OVEN-1 (P-02-SINGLE)	6.00-9 C	\N	QC_OK	24.50	\N	0.50	2026-02-17 19:01:04.439825	\N	\N	\N	\N	\N	160	N/A	t	24.00	OK	mild unfill	180	2026-02-17 19:01:59.185939	1834	0	HANIFF	Bijoy	80	82	68	72	DD001 - UNDER CURE	Bijoy	2026-02-17 19:04:49.489344	\N	\N
36	B-011000	F010033 0726	STANDARD	P-04-BOT	140X55-9	\N	COOLING	\N	\N	\N	2026-02-16 09:44:39.700041	\N	\N	\N	\N	\N	160	150	f	\N	\N	\N	45	2026-02-17 20:32:22.83789	0	2043	HANIFF	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
46	B-011020	F010044 0726	STANDARD	P-04-BOT	140X55-9	\N	COOLING	10.20	\N	\N	2026-02-17 19:32:11.423282	\N	\N	\N	\N	\N	160	150	f	\N	\N	\N	45	2026-02-17 20:32:22.83789	64	15	HANIFF	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
35	B-010997	F010032 0726	STANDARD	P-01-SINGLE	18X7.00-8 A	\N	COOLING	\N	\N	\N	2026-02-16 09:18:17.362294	\N	\N	\N	\N	\N	160	150	f	\N	\N	\N	45	2026-02-17 20:32:34.703142	0	2069	HANIFF	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
44	B-011018	F010042 0726	STANDARD	P-04-BOT	140X55-9	\N	QC_COMPLETED	10.20	\N	0.20	2026-02-17 18:26:19.473462	\N	\N	\N	\N	\N	160	150	f	10.00	OK		45	2026-02-17 18:27:31.646963	0	0	LAKSHMI	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
39	B-011013	F010036 0726	STANDARD	P-08-BOT	12.00-20	\N	QC_COMPLETED	\N	\N	2.00	2026-02-16 12:55:15.493437	\N	\N	\N	\N	\N	160	150	f	192.00	OK		45	2026-02-17 18:29:04.222887	0	1728	HANIFF	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
48	B-011025	F010046 0726	STANDARD	P-01-SINGLE	18X7.00-8 A	\N	COOLING	30.00	\N	\N	2026-02-17 23:41:04.778465	\N	\N	\N	\N	\N	160	150	f	\N	\N	\N	45	2026-02-18 09:26:33.906408	252	540	HANIFF	Bijoy	\N	\N	\N	\N	\N	\N	\N	\N	\N
49	B-011033	F010047 0726	STANDARD	P-01	18X7.00-8 A	\N	QC_COMPLETED	20.20	\N	0.40	2026-02-19 22:37:11.611885	\N	\N	\N	\N	\N	160	150	f	19.80	OK		45	2026-02-19 22:37:32.590396	6301	-45	HANIFF	Bijoy	\N	\N	\N	\N	\N	\N	2026-02-19 22:37:55.164652	\N	\N
50	B-011034	F010048 0726	STANDARD	P-01	18X7.00-8 A	\N	COOLING	20.40	\N	\N	2026-02-20 09:11:05.962922	\N	\N	\N	\N	\N	160	150	f	\N	\N	\N	45	2026-02-20 09:38:39.852142	6935	-17	HANIFF	Aji Mohan	\N	\N	\N	\N	\N	\N	\N	\N	\N
51	B-1001	F010049 0726	STANDARD	P-01		\N	QC_COMPLETED	20.20	\N	0.20	2026-02-20 09:37:36.807838	\N	\N	\N	\N	\N	160	150	f	20.00	OK		45	2026-02-20 09:38:39.852142	6961	-44	HANIFF	Aji Mohan	\N	\N	\N	\N	\N	\N	2026-02-20 09:38:58.632418	\N	\N
53	B-1003	F010051 0726	STANDARD	P-01	140X55-9	\N	QC_COMPLETED	20.20	\N	10.20	2026-02-20 19:13:32.551038	\N	\N	\N	\N	\N	160	150	f	10.00	OK		45	2026-02-22 10:47:29.188697	7537	2329	LAKSHMI	Aji Mohan	\N	\N	\N	\N	\N	\N	2026-02-22 10:48:48.672001	\N	\N
54	B-011036	F010052 0826	STANDARD	OVEN-1 (P-07)	6.50-10 A	\N	DONE	34.80	\N	0.00	2026-02-22 11:24:01.560393	\N	\N	\N	\N	\N	160	N/A	t	34.50	OK		180	2026-02-22 11:24:14.897819	0	-180	LAKSHMI	Aji Mohan	\N	\N	\N	\N	\N	\N	2026-02-22 11:24:56.473767	\N	\N
55	B-011037	F010053 0826	STANDARD	OVEN-1 (P-07)	6.50-10 A	\N	QC_COMPLETED	34.80	\N	0.30	2026-02-22 11:28:52.538812	\N	\N	\N	\N	\N	160	N/A	t	34.50	OK		180	2026-02-22 11:29:02.796458	4	-180	HANIFF	Aji Mohan	\N	\N	\N	\N	\N	\N	2026-02-22 11:29:33.080388	\N	\N
56	B-011038	F010054 0826	STANDARD	OVEN-1 (P-07)	6.50-10 A	\N	QC_COMPLETED	34.80	\N	0.30	2026-02-22 11:32:27.963514	\N	\N	\N	\N	\N	160	N/A	t	34.50	OK		180	2026-02-22 11:32:36.703814	8	-180	HANIFF	Aji Mohan	\N	\N	\N	\N	\N	\N	2026-02-22 11:32:53.936348	\N	\N
52	B-1007	F010050 0726	STANDARD	P-04-BOT	140X55-9	\N	COOLING	10.80	\N	\N	2026-02-20 19:00:55.045912	\N	\N	\N	\N	\N	160	150	f	\N	\N	\N	45	2026-02-23 20:47:41.937691	0	4382	LAKSHMI	Aji Mohan	\N	\N	\N	\N	\N	\N	\N	\N	\N
57	B-1005	F010055 0826	STANDARD	P-03-BOT		\N	QC_COMPLETED	20.80	\N	0.80	2026-02-26 22:45:26.780267	\N	\N	\N	\N	\N	160	150	f	20.00	OK		45	2026-02-26 23:40:30.158317	0	10	HANIFF	Aji Mohan	\N	\N	\N	\N	\N	\N	2026-02-26 23:41:18.742738	\N	\N
58	B-011043	F010056 0826	STANDARD	OVEN-1 (P-01)	7.00-12 A	\N	COOLING	45.00	\N	\N	2026-02-26 22:45:42.712412	\N	\N	\N	\N	\N	160	N/A	t	\N	\N	\N	180	2026-02-27 21:15:51.857974	0	1170	HANIFF	Aji Mohan	\N	\N	\N	\N	\N	\N	\N	\N	\N
59	B-011059	F010057 0826	STANDARD	OVEN-1 (P-01)	7.00-12 A	\N	QC_COMPLETED	45.00	\N	0.50	2026-02-27 21:14:52.092872	\N	\N	\N	\N	\N	160	N/A	t	44.50	OK		180	2026-02-27 21:15:51.857974	0	-179	HANIFF	Aji Mohan	\N	\N	\N	\N	\N	\N	2026-02-27 21:16:26.629228	\N	\N
\.


--
-- Data for Name: pc3_quality; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pc3_quality (id, tyre_id, grade, defect_codes, inspector_name, inspected_at, is_finalized, qc_remarks, hardness_core_min, hardness_core_max, hardness_tread_min, hardness_tread_max, customer_name, despatched_at) FROM stdin;
3	F010047 0726	A-GRADE	DD003 - CURED FLASH|DD006 - SERIAL NUMBER MISSING	Bijoy	2026-02-19 22:38:45.871158	t	mild trobles	80	82	68	72	JK	2026-02-20 00:08:47.383927
2	F010036 0726	B-GRADE	DD006 - SERIAL NUMBER MISSING|DD009 - OVER WEIGHT|DI017 - TREAD CRACK	Bijoy	2026-02-17 23:00:18.609762	t		80	82	68	72	aruna	2026-02-20 00:20:28.933111
1	F010042 0726	A-GRADE	DD004 - SIZE/ GRADE PLATE CHANGES|DD002 - OVER CURE	Bijoy	2026-02-17 21:53:35.262696	t	placed as hold	\N	\N	\N	\N	AJI eng	2026-02-20 00:32:07.325208
4	F010049 0726	B-GRADE	DD001 - UNDER CURE	Aji Mohan	2026-02-20 09:39:40.865266	t	tread part is missing	80	82	68	72	\N	\N
5	F010051 0726	A-GRADE	DD001 - UNDER CURE	Aji Mohan	2026-02-22 10:49:21.302796	t		80	82	68	72	\N	\N
6	f010052 0826	A-GRADE		Aji Mohan	2026-02-22 11:25:59.483744	t	OKAY	80	82	68	72	\N	\N
7	F010053 0826	A-GRADE	DD001 - UNDER CURE	Aji Mohan	2026-02-22 11:30:42.245187	t		80	82	68	72	\N	\N
8	F010054 0826	A-GRADE	DD001 - UNDER CURE	Aji Mohan	2026-02-22 11:38:06.933834	t		80	82	68	71	\N	\N
9	f010052 0826	A-GRADE		Aji Mohan	2026-02-22 11:57:13.528068	t		80	82	68	72	\N	\N
10	F010055 0826	A-GRADE	DD001 - UNDER CURE	Aji Mohan	2026-02-26 23:46:32.695086	t		80	82	68	72	\N	\N
11	F010057 0826	A-GRADE	DD001 - UNDER CURE	Aji Mohan	2026-02-27 21:17:30.620193	t		80	82	68	72	\N	\N
\.


--
-- Data for Name: press_master; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.press_master (press_id, daylight, status, remarks) FROM stdin;
P-01	SINGLE	ACTIVE	STANDARD
P-02	SINGLE	MAINTENANCE	CYLINDER ISSUE
P-03	TOP	ACTIVE	STANDARD
P-04	TOP	ACTIVE	STANDARD
P-05	TOP	ACTIVE	STANDARD
P-06	TOP	ACTIVE	STANDARD
P-07	SINGLE	ACTIVE	STANDARD
P-08	TOP	ACTIVE	STANDARD
P-03	BOT	ACTIVE	Standard
P-04	BOT	ACTIVE	STANDARD
P-05	BOT	ACTIVE	STANDARD
P-06	BOT	ACTIVE	STANDARD
P-08	BOT	ACTIVE	STANDARD
\.


--
-- Data for Name: product_catalog; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_catalog (sku_id, tyre_size, core_size, brand, quality, baseline_weight, is_active) FROM stdin;
\.


--
-- Data for Name: production_plan; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.production_plan (id, press_id, daylight, tyre_size, core_size, brand, pattern, quality, mould_id_marks, type, tyre_weight, production_requirement, pi_number, tyre_type) FROM stdin;
100	P-02	SINGLE	6.00-9	4.00"	TVS	LUG	V3P02	6.00-9 B	CUSHION	24.50	12	\N	\N
102	P-03	TOP	18X7.00-8	4.33"	VELOX	PATTERN	V3P02	18X7.00-8 B	CUSHION	20.60	18	\N	\N
103	P-03	BOT	18X7.00-8	4.33"	CHALLENGER	LUG	V3P02	18X7.00-8 C	CUSHION	20.50	25	\N	\N
104	P-04	TOP	15X4.5-8	3.00"	BOSON	LUG	VPR02	15X4.50-8	CUSHION	10.80	23	\N	\N
105	P-04	BOT	140X55-9	4.00"	TVS	LUG	VPR02	140X55-9	CUSHION	10.20	21	\N	\N
107	P-05	BOT	16X6-10-1/2	POB	BOSON	LUG	POB-PRM	16X6-10-1/2	POB	10.80	9	\N	\N
108	P-06	TOP	4.00-8	3.00"	TVS	LUG	V3P02	4.00-8 A	CUSHION	10.20	6	\N	\N
109	P-06	BOT	4.00-8	3.00"	APT	LUG	V3H03	4.00-8 B	CUSHION	10.20	15	\N	\N
111	P-08	TOP	10.00-20	7.50"	TVS	LUG	V3H03	10.00-20	CUSHION	163.00	15	\N	\N
112	P-08	BOT	12.00-20	8.00"	APT	LUG	V3H03	12.00-20	CUSHION	194.00	15	\N	\N
114	P-05	TOP	6.50-10	5.00"	BOSON	\N	PREMIUM	\N	\N	\N	50	\N	\N
116	P-07	SINGLE	6.50-10	5.00"	VELOX	\N	VPR01	\N	\N	34.80	5	5	\N
119	P-01	SINGLE	7.00-12	5.00"	PAREX	\N	V3H03	\N	\N	45.00	50	7	\N
\.


--
-- Data for Name: qc_approval_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.qc_approval_logs (qc_id, batch_number, compound_type, test_result, lab_operator, properties_json, approved_at) FROM stdin;
\.


--
-- Data for Name: qc_defects_master; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.qc_defects_master (id, defect_code, defect_name, defect_type, defect_reason) FROM stdin;
1	DD001	UNDER CURE	DIRECT	LESS TEMPERATURE
2	DD002	OVER CURE	DIRECT	EXCESS TEMPERATURE
3	DD003	CURED FLASH	DIRECT	IMPROPER PRE MOULDING CHECKING
4	DD004	SIZE/ GRADE PLATE CHANGES	DIRECT	IMPROPER MOULD CHECKING BEFORE LOADING
5	DD005	CORE SIZE CHANGE	DIRECT	ERROR IN SPEC CALCULATION
6	DD006	SERIAL NUMBER MISSING	DIRECT	IMPROPER PRE MOULDING WEIGHT CHECKING
7	DD007	SPECIFICATION CHANGE	DIRECT	LESS CURING TIME
8	DD008	UNDER WEIGHT	DIRECT	EXCESS CURING TIME
9	DD009	OVER WEIGHT	DIRECT	WEIGHT NOT ADJUSTED
10	DD010	SMALL BULGING	DIRECT	IMPROPER PLACEMENT OF SERIAL NUMBER
11	DD011	BEAD WIRE OUT	DIRECT	IMPROPER BEAD WIRE PLACEMENT
12	DD012	OPEN MOULD	DIRECT	MOULD BOX NOT TIGHTENED PROPERLY
13	DD013	UNFILL	DIRECT	LESS WEIGHT
14	DI014	ONE SIDE WIDTH	INDIRECT	EXCESS WEIGHT
15	DI015	ONE SIDE WIDTH- CRACK	INDIRECT	INSUFFICIENT MOULD RELEASING AGENT
16	DI016	DIMENSION CHANGE	INDIRECT	IMPROPER MOULD CLEANING
17	DI017	TREAD CRACK	INDIRECT	EXCESS MOULD RELEASING AGENT
18	DI018	CORE CRACK	INDIRECT	DULL MOULD CAVITY
19	DI019	FLOW MARK	INDIRECT	BOILER COMPLAINT
20	DI020	DULL APPEARANCE	INDIRECT	PRESS COMPLAINT
21	DI021	INSUFFICIENT CHEMICAL	INDIRECT	FABRIC SPECIFIC GRAVITY VARIATION
22	DI022	EXCESS CHEMICAL	INDIRECT	IMPROPER CHEMICAL WEIGHING
23	DI023	UNDER CURE	INDIRECT	TEMPERATURE FAILURE
\.


--
-- Data for Name: raw_material_qc; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.raw_material_qc (batch_no, material_type, status, updated_at, is_active) FROM stdin;
A14	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A15	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A16	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A17	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A18	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A19	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A110	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A111	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A112	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A113	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A114	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A115	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A116	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A117	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A118	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A119	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A120	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A121	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A122	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A123	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A124	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A125	CORE	APPROVED	2026-02-27 14:48:07.260137	f
M1100	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1101	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1102	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1103	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1104	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1105	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1106	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1107	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1108	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1109	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1110	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1111	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1112	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1113	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1114	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1115	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1116	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1117	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1118	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1119	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
M1120	MIDDLE	APPROVED	2026-02-27 14:48:54.828628	f
V1120	VT001	APPROVED	2026-02-27 14:49:15.777016	f
V1121	VT001	APPROVED	2026-02-27 14:49:15.777016	f
V1122	VT001	APPROVED	2026-02-27 14:49:15.777016	f
V1123	VT001	APPROVED	2026-02-27 14:49:15.777016	f
V1125	VT001	APPROVED	2026-02-27 14:49:15.777016	f
V1126	VT001	APPROVED	2026-02-27 14:49:15.777016	f
V1127	VT001	APPROVED	2026-02-27 14:49:15.777016	f
V1128	VT001	APPROVED	2026-02-27 14:49:15.777016	f
V1129	VT001	APPROVED	2026-02-27 14:49:15.777016	f
VT10	VT002	APPROVED	2026-02-27 14:55:48.519179	f
VT11	VT002	APPROVED	2026-02-27 14:55:48.519179	f
VT12	VT002	APPROVED	2026-02-27 14:55:48.519179	f
VT13	VT002	APPROVED	2026-02-27 14:55:48.519179	f
VT14	VT002	APPROVED	2026-02-27 14:55:48.519179	f
VT15	VT002	APPROVED	2026-02-27 14:55:48.519179	f
VT16	VT002	APPROVED	2026-02-27 14:55:48.519179	f
VT17	VT002	APPROVED	2026-02-27 14:55:48.519179	f
VT18	VT002	APPROVED	2026-02-27 14:55:48.519179	f
VT19	VT002	APPROVED	2026-02-27 14:55:48.519179	f
S0005	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.258884	f
S0006	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.259853	f
A1234	VT001	APPROVED	2026-02-13 23:11:16.193479	f
A1235	VT001	APPROVED	2026-02-13 23:11:16.194825	f
A1236	VT001	APPROVED	2026-02-13 23:11:16.196087	f
A1237	VT001	APPROVED	2026-02-13 23:11:16.196817	f
A1238	VT001	APPROVED	2026-02-13 23:11:16.197534	f
A1239	VT001	APPROVED	2026-02-13 23:11:16.198236	f
A1240	VT001	APPROVED	2026-02-13 23:11:16.198978	f
A1241	VT001	APPROVED	2026-02-13 23:11:16.199705	f
A1242	VT001	APPROVED	2026-02-13 23:11:16.200399	f
A1243	VT001	APPROVED	2026-02-13 23:11:16.201127	f
A1244	VT001	APPROVED	2026-02-13 23:11:16.201893	f
A1245	VT001	APPROVED	2026-02-13 23:11:16.202609	f
A1246	VT001	APPROVED	2026-02-13 23:11:16.203332	f
A1247	VT001	APPROVED	2026-02-13 23:11:16.204022	f
A1248	VT001	APPROVED	2026-02-13 23:11:16.204792	f
A1249	VT001	APPROVED	2026-02-13 23:11:16.205471	f
A1250	VT001	APPROVED	2026-02-13 23:11:16.206208	f
A1251	VT001	APPROVED	2026-02-13 23:11:16.206935	f
A1252	VT001	APPROVED	2026-02-13 23:11:16.20767	f
VT20	VT002	APPROVED	2026-02-27 14:55:48.519179	f
VT22	VT002	APPROVED	2026-02-27 14:55:48.519179	f
V310001	VT003	APPROVED	2026-02-23 22:20:28.228338	f
V310002	VT003	APPROVED	2026-02-23 22:20:28.228338	f
V310003	VT003	APPROVED	2026-02-23 22:20:28.228338	f
V310004	VT003	APPROVED	2026-02-23 22:20:28.228338	f
V310005	VT003	APPROVED	2026-02-23 22:20:28.228338	f
V310006	VT003	APPROVED	2026-02-23 22:20:28.228338	f
V310007	VT003	APPROVED	2026-02-23 22:20:28.228338	f
V310008	VT003	APPROVED	2026-02-23 22:20:28.228338	f
V310009	VT003	APPROVED	2026-02-23 22:20:28.228338	f
V310010	VT003	APPROVED	2026-02-23 22:20:28.228338	f
A11	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A12	CORE	APPROVED	2026-02-27 14:48:07.260137	f
A13	CORE	APPROVED	2026-02-27 14:48:07.260137	f
G001	GUM	APPROVED	2026-02-28 00:21:06.475858	t
A1253	VT001	APPROVED	2026-02-13 23:11:16.208413	f
A1254	VT001	APPROVED	2026-02-13 23:11:16.209152	f
A1255	VT001	APPROVED	2026-02-13 23:11:16.209845	f
A1256	VT001	APPROVED	2026-02-13 23:11:16.210584	f
A1257	VT001	APPROVED	2026-02-13 23:12:04.255684	f
A1258	VT001	APPROVED	2026-02-13 23:12:04.256392	f
A1259	VT001	APPROVED	2026-02-13 23:12:04.257113	f
S0007	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.260577	f
S0008	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.261288	f
S0009	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.262033	f
S0010	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.263057	f
S0011	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.264398	f
S0012	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.265644	f
S0029	CORE	APPROVED	2026-02-13 23:47:29.754486	f
S0030	CORE	APPROVED	2026-02-13 23:47:29.755544	f
S0031	CORE	APPROVED	2026-02-13 23:47:29.756275	f
S0032	CORE	APPROVED	2026-02-13 23:47:29.756997	f
S0033	CORE	APPROVED	2026-02-13 23:47:29.757715	f
S0034	CORE	APPROVED	2026-02-13 23:47:29.758443	f
S0035	CORE	APPROVED	2026-02-13 23:47:29.759169	f
S0036	CORE	APPROVED	2026-02-13 23:47:29.759893	f
S0001	MIDDLE_LAYER	APPROVED	2026-02-13 23:11:16.190505	f
S0002	MIDDLE_LAYER	HOLD	2026-02-13 23:11:16.192085	f
S0003	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.256502	f
S0004	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.257584	f
S0013	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.266609	f
S0014	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.267334	f
S0015	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.268056	f
S0016	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.268811	f
S0017	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.2695	f
S0018	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.270218	f
S0019	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.270928	f
BATCH-C012	CORE	APPROVED	2026-02-16 11:28:50.704232	f
BATCH-C013	CORE	APPROVED	2026-02-16 11:28:50.705581	f
BATCH-C014	CORE	APPROVED	2026-02-16 11:28:50.706558	f
V1001	VT001	APPROVED	2026-03-01 23:40:22.033092	t
S0020	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.271646	f
S0021	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.27234	f
S0022	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.273068	f
S0023	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.273784	f
S0024	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.274497	f
S0025	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.275281	f
S0026	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.275961	f
S0027	MIDDLE_LAYER	APPROVED	2026-02-13 23:13:01.276669	f
S0028	MIDDLE_LAYER	APPROVED	2026-02-13 23:47:29.753514	f
BATCH-C001	CORE	APPROVED	2026-02-16 11:28:50.673178	f
BATCH-M001	MID	APPROVED	2026-02-16 11:28:50.674664	f
BATCH-G001	GUM	APPROVED	2026-02-16 11:28:50.675359	f
BATCH-T001	VT001	APPROVED	2026-02-16 11:28:50.676102	f
BATCH-T002	VT002	APPROVED	2026-02-16 11:28:50.676872	f
BATCH-T003	NMW	APPROVED	2026-02-16 11:28:50.67757	f
BATCH-T004	NMW	APPROVED	2026-02-16 11:28:50.678289	f
BATCH-T005	NMW	APPROVED	2026-02-16 11:28:50.679008	f
BATCH-T006	NMW	APPROVED	2026-02-16 11:28:50.679741	f
BATCH-T007	NMW	APPROVED	2026-02-16 11:28:50.680458	f
BATCH-T008	NMW	APPROVED	2026-02-16 11:28:50.681182	f
BATCH-T009	VT002	APPROVED	2026-02-16 11:28:50.683114	f
BATCH-T010	VT002	APPROVED	2026-02-16 11:28:50.683697	f
BATCH-T011	VT002	APPROVED	2026-02-16 11:28:50.684429	f
BATCH-T012	VT002	APPROVED	2026-02-16 11:28:50.685137	f
BATCH-T013	VT002	APPROVED	2026-02-16 11:28:50.685849	f
BATCH-T014	VT002	APPROVED	2026-02-16 11:28:50.686616	f
BATCH-T015	VT002	APPROVED	2026-02-16 11:28:50.687329	f
BATCH-M002	MID	APPROVED	2026-02-16 11:28:50.688037	f
BATCH-M003	MID	APPROVED	2026-02-16 11:28:50.688761	f
BATCH-M004	MID	APPROVED	2026-02-16 11:28:50.689478	f
BATCH-M005	MID	APPROVED	2026-02-16 11:28:50.690201	f
BATCH-M006	MID	APPROVED	2026-02-16 11:28:50.690925	f
BATCH-M007	MID	APPROVED	2026-02-16 11:28:50.691674	f
BATCH-M008	MID	APPROVED	2026-02-16 11:28:50.692391	f
BATCH-M009	MID	APPROVED	2026-02-16 11:28:50.693091	f
BATCH-M010	MID	APPROVED	2026-02-16 11:28:50.693815	f
BATCH-M011	MID	APPROVED	2026-02-16 11:28:50.694551	f
BATCH-M012	MID	APPROVED	2026-02-16 11:28:50.695262	f
BATCH-M013	MID	APPROVED	2026-02-16 11:28:50.695987	f
BATCH-C002	CORE	APPROVED	2026-02-16 11:28:50.696727	f
BATCH-C003	CORE	APPROVED	2026-02-16 11:28:50.697435	f
BATCH-C004	CORE	APPROVED	2026-02-16 11:28:50.698176	f
BATCH-C005	CORE	APPROVED	2026-02-16 11:28:50.698901	f
BATCH-C006	CORE	APPROVED	2026-02-16 11:28:50.699605	f
BATCH-C007	CORE	APPROVED	2026-02-16 11:28:50.700343	f
BATCH-C008	CORE	APPROVED	2026-02-16 11:28:50.701059	f
BATCH-C009	CORE	APPROVED	2026-02-16 11:28:50.701821	f
BATCH-C010	CORE	APPROVED	2026-02-16 11:28:50.702529	f
BATCH-C011	CORE	APPROVED	2026-02-16 11:28:50.703257	f
BATCH-C015	CORE	APPROVED	2026-02-16 11:28:50.70753	f
BATCH-C016	CORE	APPROVED	2026-02-16 11:28:50.708241	f
BATCH-C017	CORE	APPROVED	2026-02-16 11:28:50.708947	f
BATCH-C018	CORE	APPROVED	2026-02-16 11:28:50.709682	f
BATCH-C019	CORE	APPROVED	2026-02-16 11:28:50.710395	f
BATCH-C020	CORE	APPROVED	2026-02-16 11:28:50.711132	f
BATCH-C021	CORE	APPROVED	2026-02-16 11:28:50.711879	f
BATCH-C022	CORE	APPROVED	2026-02-16 11:28:50.7126	f
BATCH-C023	CORE	APPROVED	2026-02-16 11:28:50.713321	f
BATCH-C024	CORE	APPROVED	2026-02-16 11:28:50.71405	f
\.


--
-- Data for Name: ref_remarks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ref_remarks (remark_id, remark_text, is_active) FROM stdin;
\.


--
-- Data for Name: tyre_specs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tyre_specs (grade, bead_weight, core_pct, mid_pct, ct_pct, tread_pct, gum_pct, is_pob, tolerance_plus, tolerance_minus) FROM stdin;
POB-PRM	\N	0.00	0.00	40.00	57.00	3.00	t	0.50	0.50
VST01	\N	62.00	0.00	6.00	32.00	0.00	f	0.50	0.50
VPR01	\N	59.00	0.00	6.00	35.00	0.00	f	0.50	0.50
VPR02	\N	59.00	0.00	6.00	35.00	0.00	f	0.50	0.50
VPR03	\N	59.00	0.00	6.00	35.00	0.00	f	0.50	0.50
V3P01	\N	54.00	5.00	6.00	35.00	0.00	f	0.50	0.50
V3P02	\N	54.00	5.00	6.00	35.00	0.00	f	0.50	0.50
V3P03	\N	54.00	5.00	6.00	35.00	0.00	f	0.50	0.50
V3H02	\N	44.00	12.00	6.00	38.00	0.00	f	0.50	0.50
V3H03	\N	44.00	12.00	6.00	38.00	0.00	f	0.50	0.50
V3NMW	\N	34.00	10.00	6.00	50.00	0.00	f	0.50	0.50
APERTURE	\N	42.00	10.00	6.00	42.00	0.00	f	0.50	0.50
POB-STD	\N	0.00	0.00	40.00	57.00	3.00	t	0.50	0.50
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, full_name, role, is_active, created_at, password) FROM stdin;
OP-01	HANIFF	OPERATOR	t	2026-02-15 23:04:46.629903	1234
OP-02	RAJENDRA	OPERATOR	t	2026-02-15 23:05:16.429476	1234
OP-03	LAKSHMI	OPERATOR	t	2026-02-16 01:36:31.673165	1234
ADMIN	Bijoy	ADMIN	t	2026-02-16 00:20:41.353085	1234
SUP-01	AJI	SUPERVISOR	f	2026-02-15 23:03:50.823533	1234
ADMIN_AJI	Aji Mohan	ADMIN	t	2026-02-19 23:41:38.341602	aji123
\.


--
-- Name: customers_cust_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customers_cust_id_seq', 1, false);


--
-- Name: master_orders_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.master_orders_order_id_seq', 9, true);


--
-- Name: pc1_curing_c_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pc1_curing_c_id_seq', 59, true);


--
-- Name: pc1_mould_mapping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pc1_mould_mapping_id_seq', 133, true);


--
-- Name: pc3_quality_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pc3_quality_id_seq', 11, true);


--
-- Name: product_catalog_sku_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_catalog_sku_id_seq', 1, false);


--
-- Name: production_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.production_plan_id_seq', 120, true);


--
-- Name: qc_approval_logs_qc_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.qc_approval_logs_qc_id_seq', 1, false);


--
-- Name: qc_defects_master_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.qc_defects_master_id_seq', 23, true);


--
-- Name: ref_remarks_remark_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ref_remarks_remark_id_seq', 1, false);


--
-- Name: bead_master bead_master_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bead_master
    ADD CONSTRAINT bead_master_pkey PRIMARY KEY (tyre_size, mould_id);


--
-- Name: currency_rates currency_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.currency_rates
    ADD CONSTRAINT currency_rates_pkey PRIMARY KEY (currency_code);


--
-- Name: customer_master customer_master_customer_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_master
    ADD CONSTRAINT customer_master_customer_name_key UNIQUE (customer_name);


--
-- Name: customer_master customer_master_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_master
    ADD CONSTRAINT customer_master_pkey PRIMARY KEY (customer_id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (cust_id);


--
-- Name: master_orders master_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.master_orders
    ADD CONSTRAINT master_orders_pkey PRIMARY KEY (order_id);


--
-- Name: pc1_building pc1_building_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pc1_building
    ADD CONSTRAINT pc1_building_pkey PRIMARY KEY (b_id);


--
-- Name: pc2_curing pc1_curing_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pc2_curing
    ADD CONSTRAINT pc1_curing_pkey PRIMARY KEY (c_id);


--
-- Name: pc1_mould_mapping pc1_mould_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pc1_mould_mapping
    ADD CONSTRAINT pc1_mould_mapping_pkey PRIMARY KEY (id);


--
-- Name: pc3_quality pc3_quality_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pc3_quality
    ADD CONSTRAINT pc3_quality_pkey PRIMARY KEY (id);


--
-- Name: press_master press_master_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.press_master
    ADD CONSTRAINT press_master_pkey PRIMARY KEY (press_id, daylight);


--
-- Name: product_catalog product_catalog_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_catalog
    ADD CONSTRAINT product_catalog_pkey PRIMARY KEY (sku_id);


--
-- Name: product_catalog product_catalog_tyre_size_core_size_brand_quality_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_catalog
    ADD CONSTRAINT product_catalog_tyre_size_core_size_brand_quality_key UNIQUE (tyre_size, core_size, brand, quality);


--
-- Name: production_plan production_plan_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.production_plan
    ADD CONSTRAINT production_plan_pkey PRIMARY KEY (id);


--
-- Name: production_plan production_plan_press_id_daylight_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.production_plan
    ADD CONSTRAINT production_plan_press_id_daylight_key UNIQUE (press_id, daylight);


--
-- Name: qc_approval_logs qc_approval_logs_batch_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qc_approval_logs
    ADD CONSTRAINT qc_approval_logs_batch_number_key UNIQUE (batch_number);


--
-- Name: qc_approval_logs qc_approval_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qc_approval_logs
    ADD CONSTRAINT qc_approval_logs_pkey PRIMARY KEY (qc_id);


--
-- Name: qc_defects_master qc_defects_master_defect_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qc_defects_master
    ADD CONSTRAINT qc_defects_master_defect_code_key UNIQUE (defect_code);


--
-- Name: qc_defects_master qc_defects_master_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.qc_defects_master
    ADD CONSTRAINT qc_defects_master_pkey PRIMARY KEY (id);


--
-- Name: raw_material_qc raw_material_qc_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.raw_material_qc
    ADD CONSTRAINT raw_material_qc_pkey PRIMARY KEY (batch_no);


--
-- Name: ref_remarks ref_remarks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ref_remarks
    ADD CONSTRAINT ref_remarks_pkey PRIMARY KEY (remark_id);


--
-- Name: ref_remarks ref_remarks_remark_text_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ref_remarks
    ADD CONSTRAINT ref_remarks_remark_text_key UNIQUE (remark_text);


--
-- Name: tyre_specs tyre_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tyre_specs
    ADD CONSTRAINT tyre_specs_pkey PRIMARY KEY (grade);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: idx_mould_size; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mould_size ON public.pc1_mould_mapping USING btree (tyre_size);


--
-- PostgreSQL database dump complete
--

\unrestrict o1FtGDJY5KF7LGpZPYO4bcWAFek0oUNPbhOqe9lYq1gVyiNLyTjrtcNzo4nDMWT

