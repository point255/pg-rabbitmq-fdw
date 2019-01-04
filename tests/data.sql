-- Load extension
CREATE EXTENSION multicorn;

CREATE SERVER multicorn_rabbitmq FOREIGN DATA WRAPPER multicorn
OPTIONS (
  wrapper 'pg_rabbitmq.RabbitmqFDW'
);

-- Create test table
CREATE TABLE tag_rabbitmq (
    id bigint NOT NULL,
    label text,
    slug text,
    CONSTRAINT id_pkey PRIMARY KEY (id)
);

-- Create the the foreign table (with option for RabbitMQ)
CREATE FOREIGN TABLE rabbitmq (
    "id" bigint,
    "table" text,
    "action" text
)
SERVER multicorn_rabbitmq
OPTIONS (
    -- ip machine of the host from the Docker image
    host '172.17.0.1',
    port '5672',
    user 'test',
    password 'test',
    exchange 'indexing'
);

-- Create a function for each action
-- The only difference is the "action" value
CREATE OR REPLACE FUNCTION index_tag() RETURNS trigger AS $def$
    BEGIN
        INSERT INTO tag_rabbitmq ("id", "table", "action")
        VALUES (NEW.tag_id, 'tag', 'insert');
        RETURN NEW;
    END;
$def$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION reindex_tag() RETURNS trigger AS $def$
    BEGIN
        INSERT INTO tag_rabbitmq ("id", "table", "action")
        VALUES (NEW.tag_id, 'tag', 'update');
        RETURN NEW;
    END;
$def$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_tag() RETURNS trigger AS $def$
    BEGIN
        INSERT INTO tag_rabbitmq ("id", "table", "action")
        VALUES (OLD.tag_id, 'tag', 'delete');
        RETURN OLD;
    END;
$def$ LANGUAGE plpgsql;

-- Create triggers for each action
CREATE TRIGGER rabbitmq_insert_tag
    AFTER INSERT ON tag
    FOR EACH ROW EXECUTE PROCEDURE index_tag();

CREATE TRIGGER rabbitmq_update_tag
    AFTER UPDATE OF label, slug ON tag
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE PROCEDURE reindex_tag();

CREATE TRIGGER rabbitmq_delete_tag
    BEFORE DELETE ON tag
    FOR EACH ROW EXECUTE PROCEDURE delete_tag();
