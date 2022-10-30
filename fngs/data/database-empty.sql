--
-- PostgreSQL database dump
--

-- Dumped from database version 13.6 (Ubuntu 13.6-0ubuntu0.21.10.1)
-- Dumped by pg_dump version 13.6 (Ubuntu 13.6-0ubuntu0.21.10.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group (
    id bigint NOT NULL,
    name text
);


ALTER TABLE public.auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id bigint,
    permission_id bigint
);


ALTER TABLE public.auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_permission (
    id bigint NOT NULL,
    content_type_id bigint,
    codename text,
    name text
);


ALTER TABLE public.auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_user (
    id bigint NOT NULL,
    password text,
    last_login timestamp with time zone,
    is_superuser boolean,
    username text,
    first_name text,
    email text,
    is_staff boolean,
    is_active boolean,
    date_joined timestamp with time zone,
    last_name text
);


ALTER TABLE public.auth_user OWNER TO postgres;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_user_groups (
    id bigint NOT NULL,
    user_id bigint,
    group_id bigint
);


ALTER TABLE public.auth_user_groups OWNER TO postgres;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO postgres;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_user_groups_id_seq OWNED BY public.auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO postgres;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_user_id_seq OWNED BY public.auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id bigint,
    permission_id bigint
);


ALTER TABLE public.auth_user_user_permissions OWNER TO postgres;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO postgres;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_user_user_permissions_id_seq OWNED BY public.auth_user_user_permissions.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_admin_log (
    id bigint NOT NULL,
    action_time timestamp with time zone,
    object_id text,
    object_repr text,
    change_message text,
    content_type_id bigint,
    user_id bigint,
    action_flag smallint
);


ALTER TABLE public.django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_content_type (
    id bigint NOT NULL,
    app_label text,
    model text
);


ALTER TABLE public.django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app text,
    name text,
    applied timestamp with time zone
);


ALTER TABLE public.django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_session (
    session_key text NOT NULL,
    session_data text,
    expire_date timestamp with time zone
);


ALTER TABLE public.django_session OWNER TO postgres;

--
-- Name: ds_digestrecordlemma; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ds_digestrecordlemma (
    id integer NOT NULL,
    digest_record_id integer NOT NULL,
    lemma_id integer NOT NULL,
    count integer NOT NULL
);


ALTER TABLE public.ds_digestrecordlemma OWNER TO postgres;

--
-- Name: ds_digestrecordlemma_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ds_digestrecordlemma_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ds_digestrecordlemma_id_seq OWNER TO postgres;

--
-- Name: ds_digestrecordlemma_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ds_digestrecordlemma_id_seq OWNED BY public.ds_digestrecordlemma.id;


--
-- Name: ds_lemma; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ds_lemma (
    id integer NOT NULL,
    text character varying(2048) NOT NULL
);


ALTER TABLE public.ds_lemma OWNER TO postgres;

--
-- Name: ds_lemma_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ds_lemma_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ds_lemma_id_seq OWNER TO postgres;

--
-- Name: ds_lemma_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ds_lemma_id_seq OWNED BY public.ds_lemma.id;


--
-- Name: gatherer_digestgatheringiteration; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_digestgatheringiteration (
    id integer NOT NULL,
    dt timestamp with time zone NOT NULL,
    gathered_count integer NOT NULL,
    source_id integer,
    parser_error text,
    source_enabled boolean,
    source_error text,
    saved_count integer,
    overall_count integer
);


ALTER TABLE public.gatherer_digestgatheringiteration OWNER TO postgres;

--
-- Name: gatherer_digestgatheringiteration_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_digestgatheringiteration_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_digestgatheringiteration_id_seq OWNER TO postgres;

--
-- Name: gatherer_digestgatheringiteration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_digestgatheringiteration_id_seq OWNED BY public.gatherer_digestgatheringiteration.id;


--
-- Name: gatherer_digestissue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_digestissue (
    id bigint NOT NULL,
    number bigint,
    habr_url text,
    is_special boolean
);


ALTER TABLE public.gatherer_digestissue OWNER TO postgres;

--
-- Name: gatherer_digestissue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_digestissue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_digestissue_id_seq OWNER TO postgres;

--
-- Name: gatherer_digestissue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_digestissue_id_seq OWNED BY public.gatherer_digestissue.id;


--
-- Name: gatherer_digestrecord; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_digestrecord (
    id bigint NOT NULL,
    dt timestamp with time zone,
    title text,
    url text,
    content_type text,
    is_main boolean,
    content_category text,
    state text,
    gather_dt timestamp with time zone,
    keywords text,
    language text,
    description text,
    source_id bigint,
    digest_issue_id bigint,
    additional_url character varying(256),
    cleared_description text,
    text text
);


ALTER TABLE public.gatherer_digestrecord OWNER TO postgres;

--
-- Name: gatherer_digestrecord_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_digestrecord_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_digestrecord_id_seq OWNER TO postgres;

--
-- Name: gatherer_digestrecord_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_digestrecord_id_seq OWNED BY public.gatherer_digestrecord.id;


--
-- Name: gatherer_digestrecord_projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_digestrecord_projects (
    id bigint NOT NULL,
    digestrecord_id bigint,
    project_id bigint
);


ALTER TABLE public.gatherer_digestrecord_projects OWNER TO postgres;

--
-- Name: gatherer_digestrecord_projects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_digestrecord_projects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_digestrecord_projects_id_seq OWNER TO postgres;

--
-- Name: gatherer_digestrecord_projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_digestrecord_projects_id_seq OWNED BY public.gatherer_digestrecord_projects.id;


--
-- Name: gatherer_digestrecord_title_keywords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_digestrecord_title_keywords (
    id bigint NOT NULL,
    digestrecord_id bigint,
    keyword_id bigint
);


ALTER TABLE public.gatherer_digestrecord_title_keywords OWNER TO postgres;

--
-- Name: gatherer_digestrecord_title_keywords_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_digestrecord_title_keywords_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_digestrecord_title_keywords_id_seq OWNER TO postgres;

--
-- Name: gatherer_digestrecord_title_keywords_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_digestrecord_title_keywords_id_seq OWNED BY public.gatherer_digestrecord_title_keywords.id;


--
-- Name: gatherer_similardigestrecords_digest_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_similardigestrecords_digest_records (
    id bigint NOT NULL,
    similardigestrecords_id bigint,
    digestrecord_id bigint
);


ALTER TABLE public.gatherer_similardigestrecords_digest_records OWNER TO postgres;

--
-- Name: gatherer_digestrecordduplicate_digest_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_digestrecordduplicate_digest_records_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_digestrecordduplicate_digest_records_id_seq OWNER TO postgres;

--
-- Name: gatherer_digestrecordduplicate_digest_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_digestrecordduplicate_digest_records_id_seq OWNED BY public.gatherer_similardigestrecords_digest_records.id;


--
-- Name: gatherer_similardigestrecords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_similardigestrecords (
    id bigint NOT NULL,
    digest_issue_id bigint
);


ALTER TABLE public.gatherer_similardigestrecords OWNER TO postgres;

--
-- Name: gatherer_digestrecordduplicate_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_digestrecordduplicate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_digestrecordduplicate_id_seq OWNER TO postgres;

--
-- Name: gatherer_digestrecordduplicate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_digestrecordduplicate_id_seq OWNED BY public.gatherer_similardigestrecords.id;


--
-- Name: gatherer_digestrecordssource; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_digestrecordssource (
    id bigint NOT NULL,
    name text,
    enabled boolean,
    data_url character varying(512),
    language character varying(15),
    text_fetching_enabled boolean NOT NULL
);


ALTER TABLE public.gatherer_digestrecordssource OWNER TO postgres;

--
-- Name: gatherer_digestrecordssource_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_digestrecordssource_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_digestrecordssource_id_seq OWNER TO postgres;

--
-- Name: gatherer_digestrecordssource_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_digestrecordssource_id_seq OWNED BY public.gatherer_digestrecordssource.id;


--
-- Name: gatherer_digestrecordssource_projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_digestrecordssource_projects (
    id integer NOT NULL,
    digestrecordssource_id integer NOT NULL,
    project_id integer NOT NULL
);


ALTER TABLE public.gatherer_digestrecordssource_projects OWNER TO postgres;

--
-- Name: gatherer_digestrecordssource_projects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_digestrecordssource_projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_digestrecordssource_projects_id_seq OWNER TO postgres;

--
-- Name: gatherer_digestrecordssource_projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_digestrecordssource_projects_id_seq OWNED BY public.gatherer_digestrecordssource_projects.id;


--
-- Name: gatherer_keyword; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_keyword (
    id bigint NOT NULL,
    name text,
    content_category text,
    is_generic boolean,
    enabled boolean NOT NULL,
    proprietary boolean NOT NULL
);


ALTER TABLE public.gatherer_keyword OWNER TO postgres;

--
-- Name: gatherer_keyword_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_keyword_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_keyword_id_seq OWNER TO postgres;

--
-- Name: gatherer_keyword_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_keyword_id_seq OWNED BY public.gatherer_keyword.id;


--
-- Name: gatherer_project; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gatherer_project (
    id bigint NOT NULL,
    name text
);


ALTER TABLE public.gatherer_project OWNER TO postgres;

--
-- Name: gatherer_project_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gatherer_project_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gatherer_project_id_seq OWNER TO postgres;

--
-- Name: gatherer_project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gatherer_project_id_seq OWNED BY public.gatherer_project.id;


--
-- Name: tbot_telegrambotdigestrecordcategorizationattempt; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tbot_telegrambotdigestrecordcategorizationattempt (
    id bigint NOT NULL,
    dt timestamp with time zone,
    estimated_state text,
    estimated_is_main boolean,
    estimated_content_type text,
    estimated_content_category text,
    telegram_bot_user_id bigint,
    digest_record_id bigint
);


ALTER TABLE public.tbot_telegrambotdigestrecordcategorizationattempt OWNER TO postgres;

--
-- Name: tbot_telegrambotdigestrecordcategorizationattempt_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tbot_telegrambotdigestrecordcategorizationattempt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbot_telegrambotdigestrecordcategorizationattempt_id_seq OWNER TO postgres;

--
-- Name: tbot_telegrambotdigestrecordcategorizationattempt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tbot_telegrambotdigestrecordcategorizationattempt_id_seq OWNED BY public.tbot_telegrambotdigestrecordcategorizationattempt.id;


--
-- Name: tbot_telegrambotuser; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tbot_telegrambotuser (
    id bigint NOT NULL,
    username text,
    tid bigint
);


ALTER TABLE public.tbot_telegrambotuser OWNER TO postgres;

--
-- Name: tbot_telegrambotuser_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tbot_telegrambotuser_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbot_telegrambotuser_id_seq OWNER TO postgres;

--
-- Name: tbot_telegrambotuser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tbot_telegrambotuser_id_seq OWNED BY public.tbot_telegrambotuser.id;


--
-- Name: tbot_telegrambotusergroup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tbot_telegrambotusergroup (
    id integer NOT NULL,
    name character varying(256) NOT NULL
);


ALTER TABLE public.tbot_telegrambotusergroup OWNER TO postgres;

--
-- Name: tbot_telegrambotusergroup_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tbot_telegrambotusergroup_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbot_telegrambotusergroup_id_seq OWNER TO postgres;

--
-- Name: tbot_telegrambotusergroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tbot_telegrambotusergroup_id_seq OWNED BY public.tbot_telegrambotusergroup.id;


--
-- Name: tbot_telegrambotusergroup_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tbot_telegrambotusergroup_users (
    id integer NOT NULL,
    telegrambotusergroup_id integer NOT NULL,
    telegrambotuser_id integer NOT NULL
);


ALTER TABLE public.tbot_telegrambotusergroup_users OWNER TO postgres;

--
-- Name: tbot_telegrambotusergroup_users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tbot_telegrambotusergroup_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbot_telegrambotusergroup_users_id_seq OWNER TO postgres;

--
-- Name: tbot_telegrambotusergroup_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tbot_telegrambotusergroup_users_id_seq OWNED BY public.tbot_telegrambotusergroup_users.id;


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: auth_user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user ALTER COLUMN id SET DEFAULT nextval('public.auth_user_id_seq'::regclass);


--
-- Name: auth_user_groups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_groups ALTER COLUMN id SET DEFAULT nextval('public.auth_user_groups_id_seq'::regclass);


--
-- Name: auth_user_user_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_user_user_permissions_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Name: ds_digestrecordlemma id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ds_digestrecordlemma ALTER COLUMN id SET DEFAULT nextval('public.ds_digestrecordlemma_id_seq'::regclass);


--
-- Name: ds_lemma id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ds_lemma ALTER COLUMN id SET DEFAULT nextval('public.ds_lemma_id_seq'::regclass);


--
-- Name: gatherer_digestgatheringiteration id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestgatheringiteration ALTER COLUMN id SET DEFAULT nextval('public.gatherer_digestgatheringiteration_id_seq'::regclass);


--
-- Name: gatherer_digestissue id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestissue ALTER COLUMN id SET DEFAULT nextval('public.gatherer_digestissue_id_seq'::regclass);


--
-- Name: gatherer_digestrecord id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord ALTER COLUMN id SET DEFAULT nextval('public.gatherer_digestrecord_id_seq'::regclass);


--
-- Name: gatherer_digestrecord_projects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord_projects ALTER COLUMN id SET DEFAULT nextval('public.gatherer_digestrecord_projects_id_seq'::regclass);


--
-- Name: gatherer_digestrecord_title_keywords id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord_title_keywords ALTER COLUMN id SET DEFAULT nextval('public.gatherer_digestrecord_title_keywords_id_seq'::regclass);


--
-- Name: gatherer_digestrecordssource id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecordssource ALTER COLUMN id SET DEFAULT nextval('public.gatherer_digestrecordssource_id_seq'::regclass);


--
-- Name: gatherer_digestrecordssource_projects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecordssource_projects ALTER COLUMN id SET DEFAULT nextval('public.gatherer_digestrecordssource_projects_id_seq'::regclass);


--
-- Name: gatherer_keyword id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_keyword ALTER COLUMN id SET DEFAULT nextval('public.gatherer_keyword_id_seq'::regclass);


--
-- Name: gatherer_project id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_project ALTER COLUMN id SET DEFAULT nextval('public.gatherer_project_id_seq'::regclass);


--
-- Name: gatherer_similardigestrecords id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_similardigestrecords ALTER COLUMN id SET DEFAULT nextval('public.gatherer_digestrecordduplicate_id_seq'::regclass);


--
-- Name: gatherer_similardigestrecords_digest_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_similardigestrecords_digest_records ALTER COLUMN id SET DEFAULT nextval('public.gatherer_digestrecordduplicate_digest_records_id_seq'::regclass);


--
-- Name: tbot_telegrambotdigestrecordcategorizationattempt id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotdigestrecordcategorizationattempt ALTER COLUMN id SET DEFAULT nextval('public.tbot_telegrambotdigestrecordcategorizationattempt_id_seq'::regclass);


--
-- Name: tbot_telegrambotuser id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotuser ALTER COLUMN id SET DEFAULT nextval('public.tbot_telegrambotuser_id_seq'::regclass);


--
-- Name: tbot_telegrambotusergroup id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotusergroup ALTER COLUMN id SET DEFAULT nextval('public.tbot_telegrambotusergroup_id_seq'::regclass);


--
-- Name: tbot_telegrambotusergroup_users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotusergroup_users ALTER COLUMN id SET DEFAULT nextval('public.tbot_telegrambotusergroup_users_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_permission (id, content_type_id, codename, name) FROM stdin;
1	1	add_logentry	Can add log entry
2	1	change_logentry	Can change log entry
3	1	delete_logentry	Can delete log entry
4	1	view_logentry	Can view log entry
5	2	add_permission	Can add permission
6	2	change_permission	Can change permission
7	2	delete_permission	Can delete permission
8	2	view_permission	Can view permission
9	3	add_group	Can add group
10	3	change_group	Can change group
11	3	delete_group	Can delete group
12	3	view_group	Can view group
13	4	add_user	Can add user
14	4	change_user	Can change user
15	4	delete_user	Can delete user
16	4	view_user	Can view user
17	5	add_contenttype	Can add content type
18	5	change_contenttype	Can change content type
19	5	delete_contenttype	Can delete content type
20	5	view_contenttype	Can view content type
21	6	add_session	Can add session
22	6	change_session	Can change session
23	6	delete_session	Can delete session
24	6	view_session	Can view session
25	7	add_digestrecord	Can add Digest Record
26	7	change_digestrecord	Can change Digest Record
27	7	delete_digestrecord	Can delete Digest Record
28	7	view_digestrecord	Can view Digest Record
29	8	add_digestrecordduplicate	Can add digest record duplicate
30	8	change_digestrecordduplicate	Can change digest record duplicate
31	8	delete_digestrecordduplicate	Can delete digest record duplicate
32	8	view_digestrecordduplicate	Can view digest record duplicate
33	9	add_project	Can add Project
34	9	change_project	Can change Project
35	9	delete_project	Can delete Project
36	9	view_project	Can view Project
37	10	add_keyword	Can add Keyword
38	10	change_keyword	Can change Keyword
39	10	delete_keyword	Can delete Keyword
40	10	view_keyword	Can view Keyword
41	11	add_digestrecordssource	Can add Digest Records Source
42	11	change_digestrecordssource	Can change Digest Records Source
43	11	delete_digestrecordssource	Can delete Digest Records Source
44	11	view_digestrecordssource	Can view Digest Records Source
45	12	add_telegrambotuser	Can add Telegram Bot User
46	12	change_telegrambotuser	Can change Telegram Bot User
47	12	delete_telegrambotuser	Can delete Telegram Bot User
48	12	view_telegrambotuser	Can view Telegram Bot User
49	13	add_telegrambotdigestrecordcategorizationattempt	Can add Telegram Bot Digest Record Categorization Attempt
50	13	change_telegrambotdigestrecordcategorizationattempt	Can change Telegram Bot Digest Record Categorization Attempt
51	13	delete_telegrambotdigestrecordcategorizationattempt	Can delete Telegram Bot Digest Record Categorization Attempt
52	13	view_telegrambotdigestrecordcategorizationattempt	Can view Telegram Bot Digest Record Categorization Attempt
53	14	add_digestissue	Can add Digest Issue
54	14	change_digestissue	Can change Digest Issue
55	14	delete_digestissue	Can delete Digest Issue
56	14	view_digestissue	Can view Digest Issue
57	15	add_digestgatheringiteration	Can add Digest Gathering Iteration
58	15	change_digestgatheringiteration	Can change Digest Gathering Iteration
59	15	delete_digestgatheringiteration	Can delete Digest Gathering Iteration
60	15	view_digestgatheringiteration	Can view Digest Gathering Iteration
61	16	add_telegrambotusergroup	Can add Telegram Bot User Group
62	16	change_telegrambotusergroup	Can change Telegram Bot User Group
63	16	delete_telegrambotusergroup	Can delete Telegram Bot User Group
64	16	view_telegrambotusergroup	Can view Telegram Bot User Group
65	17	add_lemma	Can add lemma
66	17	change_lemma	Can change lemma
67	17	delete_lemma	Can delete lemma
68	17	view_lemma	Can view lemma
69	18	add_digestrecordlemma	Can add digest record lemma
70	18	change_digestrecordlemma	Can change digest record lemma
71	18	delete_digestrecordlemma	Can delete digest record lemma
72	18	view_digestrecordlemma	Can view digest record lemma
73	8	add_similardigestrecords	Can add Similar Digest Records
74	8	change_similardigestrecords	Can change Similar Digest Records
75	8	delete_similardigestrecords	Can delete Similar Digest Records
76	8	view_similardigestrecords	Can view Similar Digest Records
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, email, is_staff, is_active, date_joined, last_name) FROM stdin;
2	pbkdf2_sha256$150000$ieirjjGZM8x4$uKx54EXP8bX7hKX+F5HYQ3k7Xr3DsSn79F881jcNjGU=	\N	f	tbot			f	t	2021-08-21 12:56:41.67658+05	
1	pbkdf2_sha256$150000$zYslztJ6T5Dy$YOIoJ3PBMdTUNeim94r75a72UZpjDty9gaYApCNZK9g=	2022-10-29 14:49:13.891882+05	t	admin		gim6626@gmail.com	t	t	2020-11-01 16:59:08.1471+05	
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, change_message, content_type_id, user_id, action_flag) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	gatherer	digestrecord
9	gatherer	project
10	gatherer	keyword
11	gatherer	digestrecordssource
12	tbot	telegrambotuser
13	tbot	telegrambotdigestrecordcategorizationattempt
14	gatherer	digestissue
15	gatherer	digestgatheringiteration
16	tbot	telegrambotusergroup
17	ds	lemma
18	ds	digestrecordlemma
8	gatherer	similardigestrecords
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2020-11-01 16:53:17.360646+05
2	auth	0001_initial	2020-11-01 16:53:17.412358+05
3	admin	0001_initial	2020-11-01 16:53:17.465247+05
4	admin	0002_logentry_remove_auto_add	2020-11-01 16:53:17.511834+05
5	admin	0003_logentry_add_action_flag_choices	2020-11-01 16:53:17.554331+05
6	contenttypes	0002_remove_content_type_name	2020-11-01 16:53:17.624472+05
7	auth	0002_alter_permission_name_max_length	2020-11-01 16:53:17.661879+05
8	auth	0003_alter_user_email_max_length	2020-11-01 16:53:17.734311+05
9	auth	0004_alter_user_username_opts	2020-11-01 16:53:17.796444+05
10	auth	0005_alter_user_last_login_null	2020-11-01 16:53:17.860836+05
11	auth	0006_require_contenttypes_0002	2020-11-01 16:53:17.875419+05
12	auth	0007_alter_validators_add_error_messages	2020-11-01 16:53:17.924124+05
13	auth	0008_alter_user_username_max_length	2020-11-01 16:53:17.961936+05
14	auth	0009_alter_user_last_name_max_length	2020-11-01 16:53:18.003648+05
15	auth	0010_alter_group_name_max_length	2020-11-01 16:53:18.044792+05
16	auth	0011_update_proxy_permissions	2020-11-01 16:53:18.078994+05
17	sessions	0001_initial	2020-11-01 16:53:18.101981+05
18	gatherer	0001_create_digest_record	2020-11-01 17:47:27.639492+05
20	gatherer	0002_digest_record_new_fields	2020-11-05 10:37:43.334316+05
21	gatherer	0003_digest_record_new_field	2020-11-05 10:46:12.461338+05
22	gatherer	0004_add_digest_record_gather_dt	2020-11-05 13:30:48.905756+05
23	gatherer	0005_change_digest_record_gather_dt_name	2020-11-05 13:31:47.192092+05
24	gatherer	0006_more_subcategories	2020-11-15 15:34:26.289928+05
25	gatherer	0007_new_subcategory	2020-11-22 10:40:15.224728+05
26	gatherer	add_state_variant	2020-12-03 20:40:31.874156+05
27	gatherer	0008_add_state_variant	2020-12-03 21:07:06.650067+05
28	gatherer	0009_add_digest_record_subcategory	2020-12-03 21:07:06.670573+05
29	gatherer	0010_allow_digestrecord_dt_to_be_null	2021-01-16 19:04:58.734793+05
30	gatherer	0011_digestrecord_title_set_to_be_not_mandatory_unique	2021-01-16 19:04:58.755346+05
31	gatherer	0012_digestrecord_keywords	2021-02-22 19:02:54.434188+05
32	gatherer	0013_digestrecordduplicate	2021-04-15 09:16:45.196172+05
33	gatherer	0014_digestrecordduplicate_digest_number	2021-04-16 09:27:37.635144+05
34	gatherer	0015_new_category_sysadm	2021-06-18 02:56:01.241789+05
35	gatherer	0016_new_category_testing	2021-07-02 07:21:36.150442+05
36	gatherer	0017_add_project_model	2021-07-16 11:04:12.598996+05
37	gatherer	0018_fill_projects	2021-07-16 11:04:12.61161+05
38	gatherer	0019_set_project_field_to_be_optional	2021-07-16 11:04:12.627758+05
39	gatherer	0020_digestrecord_language	2021-07-16 11:04:23.516858+05
40	gatherer	0021_added_filtered_state	2021-07-16 11:04:23.608555+05
41	gatherer	0022_removed_redundant_null_parameter_for_MtM_field	2021-07-16 11:04:23.641177+05
42	gatherer	0023_fill_empty_projects_as_fn_project	2021-07-16 11:04:53.623099+05
43	gatherer	0024_fix_few_fields_length	2021-07-16 11:04:53.865246+05
44	gatherer	0025_fill_empty_languages	2021-07-16 11:05:01.250314+05
45	gatherer	0026_set_more_correct_org_subcategory_value	2021-07-16 11:05:02.401062+05
46	gatherer	0027_migrate_system_subcategory_to_sysadm	2021-07-21 06:55:07.816236+05
47	gatherer	0028_add_video_category	2021-07-21 07:34:51.663299+05
48	gatherer	0029_migrate_youtube_records_to_video_category	2021-07-21 07:34:52.448515+05
49	gatherer	0030_keyword	2021-07-23 09:23:42.708613+05
50	gatherer	0031_fixed_russian_name_for_project_name	2021-07-23 09:23:42.854324+05
51	gatherer	0032_fill_keywords	2021-07-23 09:23:43.333337+05
52	gatherer	0033_add_digestrecord_description	2021-08-15 23:15:40.429494+05
53	gatherer	0034_add_missed_meta_description_to_digest_records_duplicates_model	2021-08-22 09:18:37.208989+05
54	gatherer	0035_create_digestrecordssource	2021-08-22 09:18:37.38729+05
55	gatherer	0036_fill_digest_records_sources	2021-08-22 09:18:37.474601+05
56	gatherer	0037_add_missed_meta_description_to_digestrecordssource	2021-08-22 09:18:37.506698+05
57	gatherer	0038_add_youtube_channels_sources	2021-08-22 09:18:37.55152+05
58	gatherer	0039_add_digestrecord_source	2021-08-22 09:18:37.821452+05
59	tbot	0001_add_user_and_categorization_attempt_models	2021-08-22 09:18:37.883244+05
60	tbot	0002_set_telegram_username_not_required	2021-08-22 09:18:37.917485+05
61	tbot	0003_set_tid_unique	2021-08-22 09:18:37.951756+05
62	tbot	0004_add_missed_tbot_models_meta_descriptions	2021-08-22 09:18:37.991479+05
63	gatherer	0040_create_digestissue	2021-08-25 07:14:25.8088+05
64	gatherer	0041_fill_digest_issues	2021-08-25 07:14:25.862675+05
65	gatherer	0042_fix_meta_description_language	2021-08-25 07:14:25.898744+05
66	gatherer	0043_fix_descriptions_language	2021-08-25 07:14:25.939594+05
67	gatherer	0044_add_digestrecord_digest_issue	2021-08-25 07:14:26.229534+05
68	gatherer	0045_connect_digest_records_to_issues	2021-08-25 07:14:41.635475+05
69	gatherer	0046_add_digestrecord_title_keywords	2021-08-25 07:14:41.741514+05
70	gatherer	0047_fill_lf_keywords	2021-08-25 07:14:41.91326+05
71	gatherer	0048_fill_title_keywords	2021-08-25 07:15:34.330685+05
72	gatherer	0049_set_digest_issue_url_not_required	2021-08-25 07:15:34.427435+05
73	gatherer	0050_set_unique_together_for_keyword_name_and_category	2021-08-25 07:15:34.501271+05
74	gatherer	0051_add_digestrecordduplicate_digest_issue	2021-08-25 07:15:34.574567+05
75	gatherer	0052_fill_digest_issues_in_duplicates	2021-08-25 07:15:34.927747+05
76	tbot	0005_add_back_reference_to_digest_record_to_tbot_categorization	2021-08-28 15:37:00.855227+05
77	gatherer	0053_add_osm_source	2021-08-28 18:44:10.99693+05
78	gatherer	0054_digestgatheringiteration	2021-09-12 09:12:22.694612+05
79	gatherer	0055_add_more_fields_to_digestgatheringiteration	2021-09-12 09:12:22.732993+05
80	gatherer	0056_rename_digestgatheringiteration_count	2021-09-12 09:12:22.750275+05
81	gatherer	0057_digestgatheringiteration_saved_count	2021-09-12 09:12:22.762021+05
82	gatherer	0058_add_messengers_category	2021-09-12 11:34:49.038947+05
83	tbot	0006_add_messengers_category	2021-09-12 11:34:49.05131+05
84	gatherer	0059_add_more_source_fields	2021-09-13 10:51:29.184474+05
85	gatherer	0060_fill_sources_data	2021-09-13 10:51:30.585055+05
86	gatherer	0061_digestgatheringiteration_overall_count	2021-09-14 11:28:12.031082+05
87	gatherer	0062_digestissue_is_special	2021-09-16 07:40:56.822835+05
88	gatherer	0063_set_digestissue_is_special	2021-09-16 08:06:09.640015+05
89	gatherer	0064_add_unix_way_source	2021-09-18 14:56:50.655587+05
90	tbot	0007_telegrambotusergroup	2021-09-27 11:07:04.139654+05
91	tbot	0008_fill_users_groups	2021-09-27 11:07:04.606834+05
92	gatherer	0065_keyword_enabled	2021-09-27 14:06:13.524757+05
93	gatherer	0066_disable_some_keywords	2021-09-27 14:06:13.575741+05
94	tbot	0009_added_skipped_state	2021-09-27 14:09:28.876207+05
95	tbot	0010_marked_users_group_name_as_unique	2021-09-27 14:09:28.889978+05
96	gatherer	0067_added_skipped_state	2021-10-01 20:33:02.830615+05
97	gatherer	0068_digestrecord_additional_url	2021-10-01 20:38:16.796989+05
98	gatherer	0069_duplicate_state	2021-10-16 14:49:37.729262+05
99	tbot	0011_duplicate_state	2021-10-16 14:49:37.746653+05
100	gatherer	0070_rename_category_to_content_type	2021-10-23 11:49:05.187146+05
101	gatherer	0071_fix_content_type_verbose_name	2021-10-23 11:49:05.194678+05
102	gatherer	0072_rename_subcategory_to_content_category	2021-10-23 11:49:05.204074+05
103	gatherer	0073_fix_content_category_verbose_name	2021-10-23 11:49:05.211056+05
104	gatherer	0074_rename_keyword_category_to_content_type	2021-10-23 11:49:05.218021+05
105	gatherer	0075_fix_keyword_content_type_verbose_name	2021-10-23 11:49:05.222113+05
106	tbot	0012_rename_estimated_category_to_estimated_content_type	2021-10-23 11:49:05.231309+05
107	tbot	0013_fix_estimated_content_type_verbose_name	2021-10-23 11:49:05.239591+05
108	tbot	0014_rename_estimated_subcategory_to_estimated_content_category	2021-10-23 11:49:05.247268+05
109	tbot	0015_fix_estimated_content_category_verbose_name	2021-10-23 11:49:05.254616+05
110	gatherer	0076_keyword_proprietary	2021-10-23 15:18:08.792869+05
111	gatherer	0077_removed_useless_null_parameter	2021-10-24 11:57:59.700339+05
112	gatherer	0078_digestrecord_cleared_description	2021-10-24 11:57:59.708972+05
113	gatherer	0079_fill_cleared_descriptions	2021-10-24 11:58:33.894992+05
114	gatherer	0080_fixed_cleared_description_verbose_name	2021-10-24 11:58:33.906988+05
115	ds	0001_initial	2021-10-24 11:58:33.927936+05
116	ds	0002_set_unique	2021-10-24 11:58:33.942401+05
117	ds	0003_digestrecordlemma_count	2021-10-24 11:58:33.9505+05
118	ds	0004_increase_lemma_max_length	2021-10-24 11:58:33.955591+05
119	ds	0005_fill_lemmas_and_connections_to_digest_records	2021-10-24 12:37:58.276473+05
120	gatherer	0081_fix_wrongly_skipped_records	2021-10-29 07:42:37.392164+05
121	tbot	0016_add_editors_group	2021-10-29 07:42:37.397404+05
122	gatherer	0082_remove_jenkins_duplicate	2021-11-05 07:57:01.513296+05
123	gatherer	0083_rename_digestrecordduplicate_to_similardigestrecords	2021-11-06 19:13:05.435199+05
124	gatherer	0084_additional_renaming_after_recent_model_name_change	2021-11-06 19:13:05.705345+05
125	ds	0006_remove_russian_lemmas	2021-11-08 07:36:45.866968+05
126	gatherer	0085_removed_obsolete_news_content_category	2021-11-08 07:36:45.930604+05
127	gatherer	0086_remove_obsolete_digest_number_field	2021-11-08 07:36:45.967367+05
128	tbot	0017_removed_obsolete_news_content_category	2021-11-08 07:36:45.977063+05
129	tbot	0018_changed_default_estimated_is_main_to_none	2021-11-08 08:19:59.636986+05
130	gatherer	0087_added_none_default_value_for_record_is_main_field	2021-11-12 18:05:15.884596+05
131	gatherer	0088_digestrecord_text	2022-01-07 14:44:38.256494+05
132	gatherer	0089_digestrecordssource_text_fetching_enabled	2022-01-07 14:44:38.276378+05
133	gatherer	0090_enable_fetching_for_some_sources	2022-01-07 14:44:38.317758+05
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: ds_digestrecordlemma; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ds_digestrecordlemma (id, digest_record_id, lemma_id, count) FROM stdin;
\.


--
-- Data for Name: ds_lemma; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ds_lemma (id, text) FROM stdin;
\.


--
-- Data for Name: gatherer_digestgatheringiteration; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_digestgatheringiteration (id, dt, gathered_count, source_id, parser_error, source_enabled, source_error, saved_count, overall_count) FROM stdin;
\.


--
-- Data for Name: gatherer_digestissue; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_digestissue (id, number, habr_url, is_special) FROM stdin;
\.


--
-- Data for Name: gatherer_digestrecord; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_digestrecord (id, dt, title, url, content_type, is_main, content_category, state, gather_dt, keywords, language, description, source_id, digest_issue_id, additional_url, cleared_description, text) FROM stdin;
\.


--
-- Data for Name: gatherer_digestrecord_projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_digestrecord_projects (id, digestrecord_id, project_id) FROM stdin;
\.


--
-- Data for Name: gatherer_digestrecord_title_keywords; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_digestrecord_title_keywords (id, digestrecord_id, keyword_id) FROM stdin;
\.


--
-- Data for Name: gatherer_digestrecordssource; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_digestrecordssource (id, name, enabled, data_url, language, text_fetching_enabled) FROM stdin;
\.


--
-- Data for Name: gatherer_digestrecordssource_projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_digestrecordssource_projects (id, digestrecordssource_id, project_id) FROM stdin;
\.


--
-- Data for Name: gatherer_keyword; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_keyword (id, name, content_category, is_generic, enabled, proprietary) FROM stdin;
\.


--
-- Data for Name: gatherer_project; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_project (id, name) FROM stdin;
\.


--
-- Data for Name: gatherer_similardigestrecords; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_similardigestrecords (id, digest_issue_id) FROM stdin;
\.


--
-- Data for Name: gatherer_similardigestrecords_digest_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.gatherer_similardigestrecords_digest_records (id, similardigestrecords_id, digestrecord_id) FROM stdin;
\.


--
-- Data for Name: tbot_telegrambotdigestrecordcategorizationattempt; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tbot_telegrambotdigestrecordcategorizationattempt (id, dt, estimated_state, estimated_is_main, estimated_content_type, estimated_content_category, telegram_bot_user_id, digest_record_id) FROM stdin;
\.


--
-- Data for Name: tbot_telegrambotuser; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tbot_telegrambotuser (id, username, tid) FROM stdin;
\.


--
-- Data for Name: tbot_telegrambotusergroup; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tbot_telegrambotusergroup (id, name) FROM stdin;
\.


--
-- Data for Name: tbot_telegrambotusergroup_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tbot_telegrambotusergroup_users (id, telegrambotusergroup_id, telegrambotuser_id) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, true);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, true);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 76, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, true);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 2, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 9902, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 18, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 133, true);


--
-- Name: ds_digestrecordlemma_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ds_digestrecordlemma_id_seq', 3996042, true);


--
-- Name: ds_lemma_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ds_lemma_id_seq', 174318, true);


--
-- Name: gatherer_digestgatheringiteration_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_digestgatheringiteration_id_seq', 273500, true);


--
-- Name: gatherer_digestissue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_digestissue_id_seq', 104, true);


--
-- Name: gatherer_digestrecord_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_digestrecord_id_seq', 91172, true);


--
-- Name: gatherer_digestrecord_projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_digestrecord_projects_id_seq', 91159, true);


--
-- Name: gatherer_digestrecord_title_keywords_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_digestrecord_title_keywords_id_seq', 71844, true);


--
-- Name: gatherer_digestrecordduplicate_digest_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_digestrecordduplicate_digest_records_id_seq', 1636, true);


--
-- Name: gatherer_digestrecordduplicate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_digestrecordduplicate_id_seq', 581, true);


--
-- Name: gatherer_digestrecordssource_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_digestrecordssource_id_seq', 219, true);


--
-- Name: gatherer_digestrecordssource_projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_digestrecordssource_projects_id_seq', 221, true);


--
-- Name: gatherer_keyword_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_keyword_id_seq', 2397, true);


--
-- Name: gatherer_project_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.gatherer_project_id_seq', 2, true);


--
-- Name: tbot_telegrambotdigestrecordcategorizationattempt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tbot_telegrambotdigestrecordcategorizationattempt_id_seq', 6472, true);


--
-- Name: tbot_telegrambotuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tbot_telegrambotuser_id_seq', 98, true);


--
-- Name: tbot_telegrambotusergroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tbot_telegrambotusergroup_id_seq', 3, true);


--
-- Name: tbot_telegrambotusergroup_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tbot_telegrambotusergroup_users_id_seq', 77, true);


--
-- Name: ds_digestrecordlemma ds_digestrecordlemma_digest_record_id_lemma_id_f445097f_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ds_digestrecordlemma
    ADD CONSTRAINT ds_digestrecordlemma_digest_record_id_lemma_id_f445097f_uniq UNIQUE (digest_record_id, lemma_id);


--
-- Name: ds_digestrecordlemma ds_digestrecordlemma_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ds_digestrecordlemma
    ADD CONSTRAINT ds_digestrecordlemma_pkey PRIMARY KEY (id);


--
-- Name: ds_lemma ds_lemma_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ds_lemma
    ADD CONSTRAINT ds_lemma_pkey PRIMARY KEY (id);


--
-- Name: ds_lemma ds_lemma_text_28ee0f6f_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ds_lemma
    ADD CONSTRAINT ds_lemma_text_28ee0f6f_uniq UNIQUE (text);


--
-- Name: gatherer_digestgatheringiteration gatherer_digestgatheringiteration_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestgatheringiteration
    ADD CONSTRAINT gatherer_digestgatheringiteration_pkey PRIMARY KEY (id);


--
-- Name: gatherer_digestrecordssource_projects gatherer_digestrecordsso_digestrecordssource_id_p_5393c078_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecordssource_projects
    ADD CONSTRAINT gatherer_digestrecordsso_digestrecordssource_id_p_5393c078_uniq UNIQUE (digestrecordssource_id, project_id);


--
-- Name: gatherer_digestrecordssource gatherer_digestrecordssource_data_url_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecordssource
    ADD CONSTRAINT gatherer_digestrecordssource_data_url_key UNIQUE (data_url);


--
-- Name: gatherer_digestrecordssource_projects gatherer_digestrecordssource_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecordssource_projects
    ADD CONSTRAINT gatherer_digestrecordssource_projects_pkey PRIMARY KEY (id);


--
-- Name: django_migrations idx_16387_django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT idx_16387_django_migrations_pkey PRIMARY KEY (id);


--
-- Name: auth_group_permissions idx_16396_auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT idx_16396_auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups idx_16402_auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT idx_16402_auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions idx_16408_auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT idx_16408_auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log idx_16414_django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT idx_16414_django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type idx_16423_django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT idx_16423_django_content_type_pkey PRIMARY KEY (id);


--
-- Name: auth_permission idx_16432_auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT idx_16432_auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user idx_16441_auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT idx_16441_auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_group idx_16450_auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT idx_16450_auth_group_pkey PRIMARY KEY (id);


--
-- Name: django_session idx_16457_sqlite_autoindex_django_session_1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT idx_16457_sqlite_autoindex_django_session_1 PRIMARY KEY (session_key);


--
-- Name: gatherer_similardigestrecords_digest_records idx_16465_gatherer_digestrecordduplicate_digest_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_similardigestrecords_digest_records
    ADD CONSTRAINT idx_16465_gatherer_digestrecordduplicate_digest_records_pkey PRIMARY KEY (id);


--
-- Name: gatherer_digestrecord_projects idx_16471_gatherer_digestrecord_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord_projects
    ADD CONSTRAINT idx_16471_gatherer_digestrecord_projects_pkey PRIMARY KEY (id);


--
-- Name: gatherer_keyword idx_16477_gatherer_keyword_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_keyword
    ADD CONSTRAINT idx_16477_gatherer_keyword_pkey PRIMARY KEY (id);


--
-- Name: gatherer_project idx_16486_gatherer_project_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_project
    ADD CONSTRAINT idx_16486_gatherer_project_pkey PRIMARY KEY (id);


--
-- Name: gatherer_digestrecordssource idx_16495_gatherer_digestrecordssource_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecordssource
    ADD CONSTRAINT idx_16495_gatherer_digestrecordssource_pkey PRIMARY KEY (id);


--
-- Name: tbot_telegrambotuser idx_16504_tbot_telegrambotuser_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotuser
    ADD CONSTRAINT idx_16504_tbot_telegrambotuser_pkey PRIMARY KEY (id);


--
-- Name: gatherer_digestrecord idx_16513_gatherer_digestrecord_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord
    ADD CONSTRAINT idx_16513_gatherer_digestrecord_pkey PRIMARY KEY (id);


--
-- Name: gatherer_digestrecord_title_keywords idx_16522_gatherer_digestrecord_title_keywords_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord_title_keywords
    ADD CONSTRAINT idx_16522_gatherer_digestrecord_title_keywords_pkey PRIMARY KEY (id);


--
-- Name: gatherer_digestissue idx_16528_gatherer_digestissue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestissue
    ADD CONSTRAINT idx_16528_gatherer_digestissue_pkey PRIMARY KEY (id);


--
-- Name: gatherer_similardigestrecords idx_16537_gatherer_digestrecordduplicate_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_similardigestrecords
    ADD CONSTRAINT idx_16537_gatherer_digestrecordduplicate_pkey PRIMARY KEY (id);


--
-- Name: tbot_telegrambotdigestrecordcategorizationattempt idx_16543_tbot_telegrambotdigestrecordcategorizationattempt_pke; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotdigestrecordcategorizationattempt
    ADD CONSTRAINT idx_16543_tbot_telegrambotdigestrecordcategorizationattempt_pke PRIMARY KEY (id);


--
-- Name: tbot_telegrambotusergroup_users tbot_telegrambotusergrou_telegrambotusergroup_id__1b4a3ed0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotusergroup_users
    ADD CONSTRAINT tbot_telegrambotusergrou_telegrambotusergroup_id__1b4a3ed0_uniq UNIQUE (telegrambotusergroup_id, telegrambotuser_id);


--
-- Name: tbot_telegrambotusergroup tbot_telegrambotusergroup_name_a54732b7_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotusergroup
    ADD CONSTRAINT tbot_telegrambotusergroup_name_a54732b7_uniq UNIQUE (name);


--
-- Name: tbot_telegrambotusergroup tbot_telegrambotusergroup_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotusergroup
    ADD CONSTRAINT tbot_telegrambotusergroup_pkey PRIMARY KEY (id);


--
-- Name: tbot_telegrambotusergroup_users tbot_telegrambotusergroup_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotusergroup_users
    ADD CONSTRAINT tbot_telegrambotusergroup_users_pkey PRIMARY KEY (id);


--
-- Name: ds_digestrecordlemma_digest_record_id_a29c24ae; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ds_digestrecordlemma_digest_record_id_a29c24ae ON public.ds_digestrecordlemma USING btree (digest_record_id);


--
-- Name: ds_digestrecordlemma_lemma_id_f774cd48; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ds_digestrecordlemma_lemma_id_f774cd48 ON public.ds_digestrecordlemma USING btree (lemma_id);


--
-- Name: ds_lemma_text_28ee0f6f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ds_lemma_text_28ee0f6f_like ON public.ds_lemma USING btree (text varchar_pattern_ops);


--
-- Name: gatherer_digestgatheringiteration_source_id_679e811c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX gatherer_digestgatheringiteration_source_id_679e811c ON public.gatherer_digestgatheringiteration USING btree (source_id);


--
-- Name: gatherer_digestrecordssour_digestrecordssource_id_ff373133; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX gatherer_digestrecordssour_digestrecordssource_id_ff373133 ON public.gatherer_digestrecordssource_projects USING btree (digestrecordssource_id);


--
-- Name: gatherer_digestrecordssource_data_url_49229957_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX gatherer_digestrecordssource_data_url_49229957_like ON public.gatherer_digestrecordssource USING btree (data_url varchar_pattern_ops);


--
-- Name: gatherer_digestrecordssource_projects_project_id_bf8ba894; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX gatherer_digestrecordssource_projects_project_id_bf8ba894 ON public.gatherer_digestrecordssource_projects USING btree (project_id);


--
-- Name: idx_16396_auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16396_auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: idx_16396_auth_group_permissions_group_id_permission_id_0cd325b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16396_auth_group_permissions_group_id_permission_id_0cd325b ON public.auth_group_permissions USING btree (group_id, permission_id);


--
-- Name: idx_16396_auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16396_auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: idx_16402_auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16402_auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);


--
-- Name: idx_16402_auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16402_auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);


--
-- Name: idx_16402_auth_user_groups_user_id_group_id_94350c0c_uniq; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16402_auth_user_groups_user_id_group_id_94350c0c_uniq ON public.auth_user_groups USING btree (user_id, group_id);


--
-- Name: idx_16408_auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16408_auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);


--
-- Name: idx_16408_auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16408_auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);


--
-- Name: idx_16408_auth_user_user_permissions_user_id_permission_id_14a6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16408_auth_user_user_permissions_user_id_permission_id_14a6 ON public.auth_user_user_permissions USING btree (user_id, permission_id);


--
-- Name: idx_16414_django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16414_django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: idx_16414_django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16414_django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: idx_16423_django_content_type_app_label_model_76bd3d3b_uniq; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16423_django_content_type_app_label_model_76bd3d3b_uniq ON public.django_content_type USING btree (app_label, model);


--
-- Name: idx_16432_auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16432_auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: idx_16432_auth_permission_content_type_id_codename_01ab375a_uni; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16432_auth_permission_content_type_id_codename_01ab375a_uni ON public.auth_permission USING btree (content_type_id, codename);


--
-- Name: idx_16441_sqlite_autoindex_auth_user_1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16441_sqlite_autoindex_auth_user_1 ON public.auth_user USING btree (username);


--
-- Name: idx_16450_sqlite_autoindex_auth_group_1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16450_sqlite_autoindex_auth_group_1 ON public.auth_group USING btree (name);


--
-- Name: idx_16457_django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16457_django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: idx_16465_gatherer_digestrecordduplicate_digest_records_digestr; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16465_gatherer_digestrecordduplicate_digest_records_digestr ON public.gatherer_similardigestrecords_digest_records USING btree (digestrecord_id);


--
-- Name: idx_16471_gatherer_digestrecord_projects_digestrecord_id_aaa133; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16471_gatherer_digestrecord_projects_digestrecord_id_aaa133 ON public.gatherer_digestrecord_projects USING btree (digestrecord_id);


--
-- Name: idx_16471_gatherer_digestrecord_projects_digestrecord_id_projec; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16471_gatherer_digestrecord_projects_digestrecord_id_projec ON public.gatherer_digestrecord_projects USING btree (digestrecord_id, project_id);


--
-- Name: idx_16471_gatherer_digestrecord_projects_project_id_6abccce1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16471_gatherer_digestrecord_projects_project_id_6abccce1 ON public.gatherer_digestrecord_projects USING btree (project_id);


--
-- Name: idx_16477_gatherer_keyword_name_category_68ce703d_uniq; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16477_gatherer_keyword_name_category_68ce703d_uniq ON public.gatherer_keyword USING btree (name, content_category);


--
-- Name: idx_16495_sqlite_autoindex_gatherer_digestrecordssource_1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16495_sqlite_autoindex_gatherer_digestrecordssource_1 ON public.gatherer_digestrecordssource USING btree (name);


--
-- Name: idx_16504_sqlite_autoindex_tbot_telegrambotuser_1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16504_sqlite_autoindex_tbot_telegrambotuser_1 ON public.tbot_telegrambotuser USING btree (tid);


--
-- Name: idx_16513_gatherer_digestrecord_digest_issue_id_8f8aeee4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16513_gatherer_digestrecord_digest_issue_id_8f8aeee4 ON public.gatherer_digestrecord USING btree (digest_issue_id);


--
-- Name: idx_16513_gatherer_digestrecord_source_id_2c47c76b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16513_gatherer_digestrecord_source_id_2c47c76b ON public.gatherer_digestrecord USING btree (source_id);


--
-- Name: idx_16513_sqlite_autoindex_gatherer_digestrecord_1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16513_sqlite_autoindex_gatherer_digestrecord_1 ON public.gatherer_digestrecord USING btree (url);


--
-- Name: idx_16522_gatherer_digestrecord_title_keywords_digestrecord_id_; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16522_gatherer_digestrecord_title_keywords_digestrecord_id_ ON public.gatherer_digestrecord_title_keywords USING btree (digestrecord_id, keyword_id);


--
-- Name: idx_16522_gatherer_digestrecord_title_keywords_keyword_id_32e70; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16522_gatherer_digestrecord_title_keywords_keyword_id_32e70 ON public.gatherer_digestrecord_title_keywords USING btree (keyword_id);


--
-- Name: idx_16528_sqlite_autoindex_gatherer_digestissue_1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16528_sqlite_autoindex_gatherer_digestissue_1 ON public.gatherer_digestissue USING btree (number);


--
-- Name: idx_16528_sqlite_autoindex_gatherer_digestissue_2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_16528_sqlite_autoindex_gatherer_digestissue_2 ON public.gatherer_digestissue USING btree (habr_url);


--
-- Name: idx_16537_gatherer_digestrecordduplicate_digest_issue_id_7fe984; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16537_gatherer_digestrecordduplicate_digest_issue_id_7fe984 ON public.gatherer_similardigestrecords USING btree (digest_issue_id);


--
-- Name: idx_16543_tbot_telegrambotdigestrecordcategorizationattempt_dig; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16543_tbot_telegrambotdigestrecordcategorizationattempt_dig ON public.tbot_telegrambotdigestrecordcategorizationattempt USING btree (digest_record_id);


--
-- Name: idx_16543_tbot_telegrambotdigestrecordcategorizationattempt_tel; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_16543_tbot_telegrambotdigestrecordcategorizationattempt_tel ON public.tbot_telegrambotdigestrecordcategorizationattempt USING btree (telegram_bot_user_id);


--
-- Name: tbot_telegrambotusergroup__telegrambotusergroup_id_97d43ae0; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tbot_telegrambotusergroup__telegrambotusergroup_id_97d43ae0 ON public.tbot_telegrambotusergroup_users USING btree (telegrambotusergroup_id);


--
-- Name: tbot_telegrambotusergroup_name_a54732b7_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tbot_telegrambotusergroup_name_a54732b7_like ON public.tbot_telegrambotusergroup USING btree (name varchar_pattern_ops);


--
-- Name: tbot_telegrambotusergroup_users_telegrambotuser_id_6115c2ed; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tbot_telegrambotusergroup_users_telegrambotuser_id_6115c2ed ON public.tbot_telegrambotusergroup_users USING btree (telegrambotuser_id);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.auth_group(id);


--
-- Name: auth_group_permissions auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id);


--
-- Name: auth_permission auth_permission_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id);


--
-- Name: auth_user_groups auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.auth_group(id);


--
-- Name: auth_user_groups auth_user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.auth_user(id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.auth_user(id);


--
-- Name: django_admin_log django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id);


--
-- Name: django_admin_log django_admin_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.auth_user(id);


--
-- Name: ds_digestrecordlemma ds_digestrecordlemma_digest_record_id_a29c24ae_fk_gatherer_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ds_digestrecordlemma
    ADD CONSTRAINT ds_digestrecordlemma_digest_record_id_a29c24ae_fk_gatherer_ FOREIGN KEY (digest_record_id) REFERENCES public.gatherer_digestrecord(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ds_digestrecordlemma ds_digestrecordlemma_lemma_id_f774cd48_fk_ds_lemma_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ds_digestrecordlemma
    ADD CONSTRAINT ds_digestrecordlemma_lemma_id_f774cd48_fk_ds_lemma_id FOREIGN KEY (lemma_id) REFERENCES public.ds_lemma(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: gatherer_digestgatheringiteration gatherer_digestgathe_source_id_679e811c_fk_gatherer_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestgatheringiteration
    ADD CONSTRAINT gatherer_digestgathe_source_id_679e811c_fk_gatherer_ FOREIGN KEY (source_id) REFERENCES public.gatherer_digestrecordssource(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: gatherer_digestrecordssource_projects gatherer_digestrecor_digestrecordssource__ff373133_fk_gatherer_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecordssource_projects
    ADD CONSTRAINT gatherer_digestrecor_digestrecordssource__ff373133_fk_gatherer_ FOREIGN KEY (digestrecordssource_id) REFERENCES public.gatherer_digestrecordssource(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: gatherer_digestrecordssource_projects gatherer_digestrecor_project_id_bf8ba894_fk_gatherer_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecordssource_projects
    ADD CONSTRAINT gatherer_digestrecor_project_id_bf8ba894_fk_gatherer_ FOREIGN KEY (project_id) REFERENCES public.gatherer_project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: gatherer_digestrecord gatherer_digestrecord_digest_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord
    ADD CONSTRAINT gatherer_digestrecord_digest_issue_id_fkey FOREIGN KEY (digest_issue_id) REFERENCES public.gatherer_digestissue(id);


--
-- Name: gatherer_digestrecord_projects gatherer_digestrecord_projects_digestrecord_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord_projects
    ADD CONSTRAINT gatherer_digestrecord_projects_digestrecord_id_fkey FOREIGN KEY (digestrecord_id) REFERENCES public.gatherer_digestrecord(id);


--
-- Name: gatherer_digestrecord_projects gatherer_digestrecord_projects_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord_projects
    ADD CONSTRAINT gatherer_digestrecord_projects_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.gatherer_project(id);


--
-- Name: gatherer_digestrecord gatherer_digestrecord_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord
    ADD CONSTRAINT gatherer_digestrecord_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.gatherer_digestrecordssource(id);


--
-- Name: gatherer_digestrecord_title_keywords gatherer_digestrecord_title_keywords_digestrecord_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord_title_keywords
    ADD CONSTRAINT gatherer_digestrecord_title_keywords_digestrecord_id_fkey FOREIGN KEY (digestrecord_id) REFERENCES public.gatherer_digestrecord(id);


--
-- Name: gatherer_digestrecord_title_keywords gatherer_digestrecord_title_keywords_keyword_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_digestrecord_title_keywords
    ADD CONSTRAINT gatherer_digestrecord_title_keywords_keyword_id_fkey FOREIGN KEY (keyword_id) REFERENCES public.gatherer_keyword(id);


--
-- Name: gatherer_similardigestrecords gatherer_digestrecordduplicate_digest_issue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_similardigestrecords
    ADD CONSTRAINT gatherer_digestrecordduplicate_digest_issue_id_fkey FOREIGN KEY (digest_issue_id) REFERENCES public.gatherer_digestissue(id);


--
-- Name: gatherer_similardigestrecords_digest_records gatherer_similardige_digestrecord_id_aa2dc2cf_fk_gatherer_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_similardigestrecords_digest_records
    ADD CONSTRAINT gatherer_similardige_digestrecord_id_aa2dc2cf_fk_gatherer_ FOREIGN KEY (digestrecord_id) REFERENCES public.gatherer_digestrecord(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: gatherer_similardigestrecords_digest_records gatherer_similardige_similardigestrecords_b6cac2b3_fk_gatherer_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gatherer_similardigestrecords_digest_records
    ADD CONSTRAINT gatherer_similardige_similardigestrecords_b6cac2b3_fk_gatherer_ FOREIGN KEY (similardigestrecords_id) REFERENCES public.gatherer_similardigestrecords(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tbot_telegrambotdigestrecordcategorizationattempt tbot_telegrambotdigestrecordcategoriz_telegram_bot_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotdigestrecordcategorizationattempt
    ADD CONSTRAINT tbot_telegrambotdigestrecordcategoriz_telegram_bot_user_id_fkey FOREIGN KEY (telegram_bot_user_id) REFERENCES public.tbot_telegrambotuser(id);


--
-- Name: tbot_telegrambotdigestrecordcategorizationattempt tbot_telegrambotdigestrecordcategorizatio_digest_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotdigestrecordcategorizationattempt
    ADD CONSTRAINT tbot_telegrambotdigestrecordcategorizatio_digest_record_id_fkey FOREIGN KEY (digest_record_id) REFERENCES public.gatherer_digestrecord(id);


--
-- Name: tbot_telegrambotusergroup_users tbot_telegrambotuser_telegrambotuser_id_6115c2ed_fk_tbot_tele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotusergroup_users
    ADD CONSTRAINT tbot_telegrambotuser_telegrambotuser_id_6115c2ed_fk_tbot_tele FOREIGN KEY (telegrambotuser_id) REFERENCES public.tbot_telegrambotuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tbot_telegrambotusergroup_users tbot_telegrambotuser_telegrambotusergroup_97d43ae0_fk_tbot_tele; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tbot_telegrambotusergroup_users
    ADD CONSTRAINT tbot_telegrambotuser_telegrambotusergroup_97d43ae0_fk_tbot_tele FOREIGN KEY (telegrambotusergroup_id) REFERENCES public.tbot_telegrambotusergroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

