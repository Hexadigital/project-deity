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