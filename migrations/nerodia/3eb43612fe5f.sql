CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 3eb43612fe5f

INSERT INTO alembic_version (version_num) VALUES ('3eb43612fe5f');

