CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD '1234';
SELECT 'CREATE DATABASE contacts'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'contacts');
CREATE TABLE emails(
email_id SERIAL PRIMARY KEY,
email VARCHAR(255)
);
CREATE TABLE phonenumbers(
phonenumber_id SERIAL PRIMARY KEY,
phonenumber VARCHAR(255)
);
INSERT INTO emails(email) VALUES ('sdad@gmail.com');

SELECT pg_create_physical_replication_slot('replication_slot');
CREATE TABLE hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 md5');
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();
