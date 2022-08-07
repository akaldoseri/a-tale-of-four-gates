CREATE TABLE apps
(
    id              INT NOT NULL AUTO_INCREMENT,
    package_name    VARCHAR(255) UNIQUE,
    analysis_status ENUM ('full', 'background', 'sql', 'download_failed', 'failed'),
    PRIMARY KEY (id)
);

CREATE TABLE components
(
    id                      INT NOT NULL AUTO_INCREMENT,
    app_id                  INT,
    name                    VARCHAR(255),
    type                    ENUM ('activity', 'provider', 'service', 'receiver'),
    enabled                 BOOL,
    exported                BOOL,
    direct_boot_aware       BOOL,
    filter_matches          JSON,
    permission              VARCHAR(255),
    authorities             VARCHAR(255),
    grant_uri_permission    VARCHAR(255),
    write_permission        VARCHAR(255),
    read_permission         VARCHAR(255),
    has_sql                 BOOL,
    foreground_service_type VARCHAR(255),
    PRIMARY KEY (id),
    FOREIGN KEY (app_id) references apps (id)
);

CREATE TABLE sql_checks
(
    id               INT NOT NULL AUTO_INCREMENT,
    app_id           INT,
    provider_name    VARCHAR(255),
    method_name      VARCHAR(255),
    has_query_checks BOOL,
    has_uri_checks   BOOL,
    PRIMARY KEY (id),
    FOREIGN KEY (app_id) references apps (id)
)

