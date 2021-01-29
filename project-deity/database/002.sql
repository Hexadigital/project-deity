ALTER TABLE "project-deity".follower_classes
    ADD COLUMN tier smallint NOT NULL DEFAULT 0;

ALTER TABLE "project-deity".deities
    ADD COLUMN registered timestamp with time zone NOT NULL DEFAULT NOW();

CREATE TABLE "project-deity".lexicon
(
    id bigserial,
    term text NOT NULL,
    definition text NOT NULL,
    added timestamp with time zone NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id)
);
COMMENT ON TABLE "project-deity".lexicon
    IS 'This table holds lexicon entries.';

ALTER TABLE "project-deity".items
    ADD COLUMN description text;

ALTER TABLE "project-deity".player_items
    ADD COLUMN master_item_id bigint NOT NULL DEFAULT 0;

ALTER TABLE "project-deity".followers
    ADD COLUMN portrait text NOT NULL DEFAULT 'default.png';

ALTER TABLE "project-deity".followers
    ADD COLUMN title text;

CREATE TABLE "project-deity".deity_materials
(
    id bigserial,
    deity_id bigint NOT NULL,
    material_id bigint NOT NULL,
    quantity bigint NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
);

CREATE TABLE "project-deity".materials
(
    id bigserial,
    item_id bigint NOT NULL,
    category text NOT NULL,
    category_rank bigint NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE "project-deity".container_roulette
(
    id bigserial,
    container_id bigint NOT NULL,
    min_chance smallint NOT NULL,
    max_chance smallint NOT NULL,
    reward_id bigint NOT NULL,
    quantity int NOT NULL,
    PRIMARY KEY (id)
);

ALTER TABLE "project-deity".items DROP COLUMN value;

ALTER TABLE "project-deity".items DROP COLUMN weight;

ALTER TABLE "project-deity".player_items DROP COLUMN value;

ALTER TABLE "project-deity".player_items DROP COLUMN weight;

CREATE TABLE "project-deity".avatars
(
    id bigserial,
    name text NOT NULL,
    filename text NOT NULL,
    deity_exclusive bigint,
    PRIMARY KEY (id)
);

CREATE TABLE "project-deity".titles
(
    id bigserial,
    title text NOT NULL,
    description text NOT NULL,
    title_json text,
    PRIMARY KEY (id)
);