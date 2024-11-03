--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2 (Debian 16.2-1.pgdg110+2)
-- Dumped by pg_dump version 16.2 (Debian 16.2-1.pgdg110+2)

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
-- Name: listing; Type: TABLE; Schema: public; Owner: air
--

CREATE TABLE public.listing (
    id character varying(255) NOT NULL,
    collect_date character varying(255) NOT NULL,
    sido character varying(255),
    collect_count integer,
    coordinate character varying(255),
    title character varying(255),
    rating double precision,
    review_count integer,
    option_list text,
    reserved_count integer
);


ALTER TABLE public.listing OWNER TO air;

--
-- Name: listing listing_pkey; Type: CONSTRAINT; Schema: public; Owner: air
--

ALTER TABLE ONLY public.listing
    ADD CONSTRAINT listing_pkey PRIMARY KEY (id, collect_date);


--
-- PostgreSQL database dump complete
--

