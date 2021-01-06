CREATE DATABASE IF NOT EXISTS `project_deity` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `project_deity`;

CREATE TABLE `db_versioning` (
  `version` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE `db_versioning`
  ADD PRIMARY KEY (`version`);

ALTER TABLE `db_versioning`
  MODIFY `version` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;