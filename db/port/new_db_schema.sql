--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: pc_builder_admin
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO pc_builder_admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: case_specs; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.case_specs (
    id integer NOT NULL,
    name text,
    price text,
    retailer_prices jsonb,
    manufacturer text,
    part_number text,
    type text,
    color text,
    power_supply text,
    side_panel text,
    power_supply_shroud boolean,
    front_panel_usb text,
    motherboard_form_factor text,
    maximum_video_card_length text,
    drive_bays text,
    expansion_slots text,
    dimensions text,
    volume text,
    url text,
    model text
);


ALTER TABLE public.case_specs OWNER TO pc_builder_admin;

--
-- Name: case_specs_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.case_specs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.case_specs_id_seq OWNER TO pc_builder_admin;

--
-- Name: case_specs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.case_specs_id_seq OWNED BY public.case_specs.id;


--
-- Name: cooler_specs; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.cooler_specs (
    id integer NOT NULL,
    name text,
    price text,
    retailer_prices jsonb,
    manufacturer text,
    part_number text,
    fan_rpm text,
    noise_level text,
    color text,
    radiator_size text,
    bearing_type text,
    height text,
    cpu_socket text,
    water_cooled boolean,
    fanless boolean,
    url text,
    model text
);


ALTER TABLE public.cooler_specs OWNER TO pc_builder_admin;

--
-- Name: cooler_specs_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.cooler_specs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cooler_specs_id_seq OWNER TO pc_builder_admin;

--
-- Name: cooler_specs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.cooler_specs_id_seq OWNED BY public.cooler_specs.id;


--
-- Name: cpu_specs; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.cpu_specs (
    id integer NOT NULL,
    name text,
    price text,
    retailer_prices jsonb,
    manufacturer text,
    part_number text,
    series text,
    microarchitecture text,
    core_family text,
    socket text,
    core_count integer,
    thread_count integer,
    performance_core_clock text,
    performance_core_boost_clock text,
    l2_cache text,
    l3_cache text,
    tdp text,
    integrated_graphics text,
    maximum_supported_memory text,
    ecc_support boolean,
    includes_cooler boolean,
    packaging text,
    lithography text,
    includes_cpu_cooler boolean,
    simultaneous_multithreading boolean,
    efficiency_core_clock text,
    efficiency_core_boost_clock text,
    model text,
    url text
);


ALTER TABLE public.cpu_specs OWNER TO pc_builder_admin;

--
-- Name: cpu_specs_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.cpu_specs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cpu_specs_id_seq OWNER TO pc_builder_admin;

--
-- Name: cpu_specs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.cpu_specs_id_seq OWNED BY public.cpu_specs.id;


--
-- Name: gpu_specs; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.gpu_specs (
    id integer NOT NULL,
    name text,
    price text,
    retailer_prices jsonb,
    manufacturer text,
    part_number text,
    chipset text,
    memory text,
    core_clock text,
    boost_clock text,
    effective_memory_clock text,
    interface text,
    color text,
    length text,
    tdp text,
    case_expansion_slot_width text,
    total_slot_width text,
    cooling text,
    external_power text,
    hdmi text,
    displayport text,
    dvi text,
    vga text,
    url text,
    model text
);


ALTER TABLE public.gpu_specs OWNER TO pc_builder_admin;

--
-- Name: gpu_specs_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.gpu_specs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gpu_specs_id_seq OWNER TO pc_builder_admin;

--
-- Name: gpu_specs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.gpu_specs_id_seq OWNED BY public.gpu_specs.id;


--
-- Name: memory_specs; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.memory_specs (
    id integer NOT NULL,
    name text,
    price text,
    retailer_prices jsonb,
    manufacturer text,
    part_number text,
    speed text,
    modules text,
    price_per_gb text,
    color text,
    first_word_latency text,
    cas_latency text,
    voltage text,
    timing text,
    ecc boolean,
    heat_spreader boolean,
    url text,
    model text
);


ALTER TABLE public.memory_specs OWNER TO pc_builder_admin;

--
-- Name: memory_specs_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.memory_specs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.memory_specs_id_seq OWNER TO pc_builder_admin;

--
-- Name: memory_specs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.memory_specs_id_seq OWNED BY public.memory_specs.id;


--
-- Name: motherboard_specs; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.motherboard_specs (
    id integer NOT NULL,
    name text,
    price text,
    retailer_prices jsonb,
    manufacturer text,
    part_number text,
    form_factor text,
    socket_cpu text,
    chipset text,
    memory_max text,
    memory_slots integer,
    memory_type text,
    memory_speed text,
    color text,
    sli_crossfire text,
    pci_slots text,
    onboard_video text,
    wireless_networking text,
    raid_support text,
    onboard_ethernet text,
    sata_ports text,
    m2_slots text,
    usb_headers text,
    ecc_support text,
    url text,
    model text
);


ALTER TABLE public.motherboard_specs OWNER TO pc_builder_admin;

--
-- Name: motherboard_specs_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.motherboard_specs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.motherboard_specs_id_seq OWNER TO pc_builder_admin;

--
-- Name: motherboard_specs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.motherboard_specs_id_seq OWNED BY public.motherboard_specs.id;


--
-- Name: psu_specs; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.psu_specs (
    id integer NOT NULL,
    name text,
    price text,
    retailer_prices jsonb,
    manufacturer text,
    part_number text,
    type text,
    efficiency_rating text,
    wattage integer,
    modular text,
    color text,
    fanless boolean,
    atx_connector text,
    eps_connector text,
    pcie_12v_connector text,
    pcie_8pin_connector text,
    pcie_6plus2pin_connector text,
    pcie_6pin_connector text,
    sata_connector text,
    molex_4pin_connector text,
    length text,
    url text,
    model text
);


ALTER TABLE public.psu_specs OWNER TO pc_builder_admin;

--
-- Name: psu_specs_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.psu_specs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.psu_specs_id_seq OWNER TO pc_builder_admin;

--
-- Name: psu_specs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.psu_specs_id_seq OWNED BY public.psu_specs.id;


--
-- Name: ssd_specs; Type: TABLE; Schema: public; Owner: pc_builder_admin
--

CREATE TABLE public.ssd_specs (
    id integer NOT NULL,
    name text,
    price numeric,
    capacity integer,
    price_per_gb numeric,
    type text,
    cache text,
    form_factor text,
    interface text
);


ALTER TABLE public.ssd_specs OWNER TO pc_builder_admin;

--
-- Name: ssd_specs_id_seq; Type: SEQUENCE; Schema: public; Owner: pc_builder_admin
--

CREATE SEQUENCE public.ssd_specs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ssd_specs_id_seq OWNER TO pc_builder_admin;

--
-- Name: ssd_specs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pc_builder_admin
--

ALTER SEQUENCE public.ssd_specs_id_seq OWNED BY public.ssd_specs.id;


--
-- Name: case_specs id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.case_specs ALTER COLUMN id SET DEFAULT nextval('public.case_specs_id_seq'::regclass);


--
-- Name: cooler_specs id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.cooler_specs ALTER COLUMN id SET DEFAULT nextval('public.cooler_specs_id_seq'::regclass);


--
-- Name: cpu_specs id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.cpu_specs ALTER COLUMN id SET DEFAULT nextval('public.cpu_specs_id_seq'::regclass);


--
-- Name: gpu_specs id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.gpu_specs ALTER COLUMN id SET DEFAULT nextval('public.gpu_specs_id_seq'::regclass);


--
-- Name: memory_specs id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.memory_specs ALTER COLUMN id SET DEFAULT nextval('public.memory_specs_id_seq'::regclass);


--
-- Name: motherboard_specs id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.motherboard_specs ALTER COLUMN id SET DEFAULT nextval('public.motherboard_specs_id_seq'::regclass);


--
-- Name: psu_specs id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.psu_specs ALTER COLUMN id SET DEFAULT nextval('public.psu_specs_id_seq'::regclass);


--
-- Name: ssd_specs id; Type: DEFAULT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.ssd_specs ALTER COLUMN id SET DEFAULT nextval('public.ssd_specs_id_seq'::regclass);


--
-- Name: case_specs case_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.case_specs
    ADD CONSTRAINT case_specs_pkey PRIMARY KEY (id);


--
-- Name: cooler_specs cooler_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.cooler_specs
    ADD CONSTRAINT cooler_specs_pkey PRIMARY KEY (id);


--
-- Name: cpu_specs cpu_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.cpu_specs
    ADD CONSTRAINT cpu_specs_pkey PRIMARY KEY (id);


--
-- Name: gpu_specs gpu_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.gpu_specs
    ADD CONSTRAINT gpu_specs_pkey PRIMARY KEY (id);


--
-- Name: memory_specs memory_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.memory_specs
    ADD CONSTRAINT memory_specs_pkey PRIMARY KEY (id);


--
-- Name: motherboard_specs motherboard_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.motherboard_specs
    ADD CONSTRAINT motherboard_specs_pkey PRIMARY KEY (id);


--
-- Name: psu_specs psu_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.psu_specs
    ADD CONSTRAINT psu_specs_pkey PRIMARY KEY (id);


--
-- Name: ssd_specs ssd_specs_pkey; Type: CONSTRAINT; Schema: public; Owner: pc_builder_admin
--

ALTER TABLE ONLY public.ssd_specs
    ADD CONSTRAINT ssd_specs_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

