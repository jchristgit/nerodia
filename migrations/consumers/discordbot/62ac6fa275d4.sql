-- Running upgrade 3eb43612fe5f -> 62ac6fa275d4

CREATE TABLE discordbot_follow (
    id INTEGER NOT NULL, 
    guild_id BIGINT NOT NULL, 
    follows VARCHAR(30) NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE discordbot_updatechannel (
    guild_id BIGINT NOT NULL, 
    channel_id BIGINT NOT NULL, 
    PRIMARY KEY (guild_id, channel_id)
);

UPDATE alembic_version SET version_num='62ac6fa275d4' WHERE alembic_version.version_num = '3eb43612fe5f';
