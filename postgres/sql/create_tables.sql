-- number generator for id
CREATE SEQUENCE lqdty_id_seq;

CREATE TABLE public.lqdty_info
(
    id integer NOT NULL DEFAULT nextval('lqdty_id_seq'::regclass),
    pk character varying COLLATE pg_catalog."default",
    poolid character varying COLLATE pg_catalog."default" not null,
    liquidity       double precision NOT NULL,
    volume_usd      double precision NOT NULL,
    insert_ts timestamp without time zone not null,
    insert_timestamp_hour timestamp without time zone not null
)
TABLESPACE pg_default;


CREATE INDEX idx_lqdty_id
    ON public.lqdty_info USING hash
    (pk COLLATE pg_catalog."default")
    TABLESPACE pg_default;

CREATE INDEX idx_pool_id
    ON public.lqdty_info USING hash
    (poolid COLLATE pg_catalog."default")
    TABLESPACE pg_default;

CREATE INDEX idx_insert_hour ON public.lqdty_info ((insert_timestamp_hour::DATE));




CREATE OR REPLACE FUNCTION lqdty_info_function()
RETURNS TRIGGER AS $$
DECLARE
	partition_date TEXT;
	partition_name TEXT;
	start_of_hour TEXT;
	end_of_next_hour TEXT;
BEGIN
	partition_hour := to_char(NEW.insert_timestamp_hour,'YYYY_MM_DD_HH');
 	partition_name := 'lqdty_info_' || partition_hour;
	start_of_hour := to_char((NEW.insert_timestamp_hour),'YYYY_MM_DD_HH') || '-01';
	end_of_next_hour := to_char((NEW.insert_timestamp_hour + interval '1 hour'),'YYYY_MM_DD_HH') || '-01';
IF NOT EXISTS
	(SELECT 1
   	 FROM   information_schema.tables 
   	 WHERE  table_name = partition_name) 
THEN
	RAISE NOTICE 'A partition has been created %', partition_name;
	EXECUTE format(E'CREATE TABLE %I (CHECK ( date_trunc(\'hour\', insert_timestamp_hour) >= ''%s'' AND date_trunc(\'hour\', insert_timehour) < ''%s'')) INHERITS (public.lqdty_info)', partition_name, start_of_hour, end_of_next_hour);

END IF;
EXECUTE format('INSERT INTO %I (entry_id, pool_id, liquidity, volume_usd, insert_timestamp, insert_timehour) VALUES($1,$2,$3,$4,$5,$6)', partition_name) using NEW.emp_id, NEW.dep_id, NEW.emp_name, NEW.insert_timehour;
RETURN NULL;
END
$$
LANGUAGE plpgsql;

CREATE TRIGGER insert_lqdty_info_trigger
    BEFORE INSERT ON public.lqdty_info
    FOR EACH ROW EXECUTE PROCEDURE public.lqdty_info_function();


