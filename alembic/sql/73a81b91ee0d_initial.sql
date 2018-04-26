CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 73a81b91ee0d

CREATE TABLE follow (
    id INTEGER NOT NULL, 
    guild_id BIGINT, 
    sub_name VARCHAR(30), 
    follows VARCHAR(30) NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE updatechannel (
    guild_id BIGINT NOT NULL, 
    channel_id BIGINT NOT NULL, 
    PRIMARY KEY (guild_id, channel_id)
);

CREATE TABLE drmapping (
    discord_id BIGINT NOT NULL, 
    reddit_name VARCHAR(30) NOT NULL, 
    PRIMARY KEY (discord_id, reddit_name)
);

CREATE TABLE sidebartemplate (
    subreddit VARCHAR(30) NOT NULL, 
    template VARCHAR(10240) NOT NULL, 
    PRIMARY KEY (subreddit)
);

INSERT INTO alembic_version (version_num) VALUES ('73a81b91ee0d');

