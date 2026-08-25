CREATE TABLE users (
    id BIGINT NOT NULL AUTO_INCREMENT,
    email VARCHAR(190) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT chk_users_role CHECK (role IN ('USER', 'ADMIN'))
);

CREATE TABLE analysis_results (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    analysis_type VARCHAR(20) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    candidate_name VARCHAR(160) NULL,
    candidate_email VARCHAR(190) NULL,
    predicted_field VARCHAR(60) NULL,
    resume_score INT NULL,
    match_score INT NULL,
    target_role VARCHAR(160) NULL,
    result_json JSON NOT NULL,
    ai_provider VARCHAR(40) NOT NULL,
    ai_model VARCHAR(80) NOT NULL,
    used_fallback BOOLEAN NOT NULL DEFAULT FALSE,
    processing_ms BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_analysis_results_user FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT chk_analysis_type CHECK (analysis_type IN ('RESUME', 'MATCH')),
    CONSTRAINT chk_resume_score CHECK (resume_score IS NULL OR resume_score BETWEEN 0 AND 100),
    CONSTRAINT chk_match_score CHECK (match_score IS NULL OR match_score BETWEEN 0 AND 100),
    CONSTRAINT chk_processing_ms CHECK (processing_ms >= 0)
);

CREATE INDEX idx_analysis_results_user_created
    ON analysis_results (user_id, created_at);

CREATE INDEX idx_analysis_results_type_created
    ON analysis_results (analysis_type, created_at);

CREATE INDEX idx_analysis_results_provider_fallback_created
    ON analysis_results (ai_provider, used_fallback, created_at);