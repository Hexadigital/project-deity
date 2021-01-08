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