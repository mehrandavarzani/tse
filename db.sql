
CREATE TABLE public."group"
(
    id serial NOT NULL,
    code character(10) COLLATE pg_catalog."default",
    name character varying(120) COLLATE pg_catalog."default",
    parent integer,
    CONSTRAINT group_pkey PRIMARY KEY (id),
    CONSTRAINT group_code_key UNIQUE (code)
,
    CONSTRAINT group_name_key UNIQUE (name)
,
    CONSTRAINT group_parent_fkey FOREIGN KEY (parent)
        REFERENCES public."group" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."group"
    OWNER to root;


CREATE INDEX group_code_idx
    ON public."group" USING btree
    (code COLLATE pg_catalog."default")
    TABLESPACE pg_default;


CREATE INDEX group_id_idx
    ON public."group" USING btree
    (id)
    TABLESPACE pg_default;


CREATE TABLE public.company
(
    id serial NOT NULL,
    tse_id character(17) COLLATE pg_catalog."default" NOT NULL,
    symbol character varying COLLATE pg_catalog."default",
    name_fa character varying COLLATE pg_catalog."default",
    name_en character varying COLLATE pg_catalog."default",
    symbol_code_12 character(12) COLLATE pg_catalog."default",
    symbol_code_5 character(5) COLLATE pg_catalog."default",
    company_code_4 character(4) COLLATE pg_catalog."default",
    company_code_12 character(12) COLLATE pg_catalog."default",
    symbol_fa_30 character varying(30) COLLATE pg_catalog."default",
    market character varying COLLATE pg_catalog."default",
    group_id smallint,
    CONSTRAINT company_pkey PRIMARY KEY (id),
    CONSTRAINT company_symbol_key UNIQUE (symbol)
,
    CONSTRAINT company_tse_id_key UNIQUE (tse_id)
,
    CONSTRAINT company_group_id_fkey FOREIGN KEY (group_id)
        REFERENCES public."group" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.company
    OWNER to root;


CREATE INDEX company_id_idx
    ON public.company USING btree
    (id)
    TABLESPACE pg_default;


CREATE INDEX company_tse_id_idx
    ON public.company USING btree
    (tse_id COLLATE pg_catalog."default")
    TABLESPACE pg_default;
    


CREATE TABLE public.daily_data
(
    id bigserial NOT NULL,
    company_id bigint,
    last double precision,
    close double precision,
    first double precision,
    yesterday double precision,
    max double precision,
    min double precision,
    count integer,
    volume bigint,
    cost double precision,
    kharid_haghighi bigint,
    kharid_hoghoghi bigint,
    forosh_haghighi bigint,
    forosh_hoghoghi bigint,
    tedad_kharid_haghighi bigint,
    tedad_kharid_hoghoghi integer,
    tedad_forosh_haghighi integer,
    tedad_forosh_hoghoghi integer,
    date date,
    "time" time without time zone,
    min_week integer,
    max_week integer,
    min_year integer,
    max_year integer,
    min_gheimat_mojaz integer,
    max_gheimat_mojaz integer,
    tedad_saham bigint,
    hajm_mabna bigint,
    miangin_hajm_mah bigint,
    saham_shenavar double precision,
    pe_goroh double precision,
    eps double precision,
    pe double precision,
    CONSTRAINT daily_data_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.daily_data
    OWNER to root;
-- Table: public.queues

-- DROP TABLE public.queues;

CREATE TABLE public.queues
(
    id bigserial NOT NULL,
    tedad_kharid integer,
    hajm_kharid bigint,
    gheimat_kharid integer,
    tedad_forosh integer,
    hajm_forosh bigint,
    gheimat_forosh integer,
    price_id bigint,
    CONSTRAINT queues_pkey PRIMARY KEY (id),
    CONSTRAINT queues_price_id_fkey FOREIGN KEY (price_id)
        REFERENCES public.daily_data (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.queues
    OWNER to root;
