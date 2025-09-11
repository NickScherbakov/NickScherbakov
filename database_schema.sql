-- GitHub M&A Intelligence Database Schema
-- PostgreSQL database for storing historical repository and analysis data

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(500) NOT NULL UNIQUE,
    owner VARCHAR(255) NOT NULL,
    owner_type VARCHAR(50),
    description TEXT,
    language VARCHAR(100),
    stars INTEGER DEFAULT 0,
    forks INTEGER DEFAULT 0,
    watchers INTEGER DEFAULT 0,
    size INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    pushed_at TIMESTAMP WITH TIME ZONE,
    archived BOOLEAN DEFAULT FALSE,
    disabled BOOLEAN DEFAULT FALSE,
    visibility VARCHAR(20) DEFAULT 'public',
    topics TEXT[], -- Array of topic strings
    license_name VARCHAR(255),
    license_url VARCHAR(500),
    homepage VARCHAR(500),
    has_issues BOOLEAN DEFAULT TRUE,
    has_projects BOOLEAN DEFAULT TRUE,
    has_wiki BOOLEAN DEFAULT TRUE,
    has_pages BOOLEAN DEFAULT FALSE,
    has_downloads BOOLEAN DEFAULT TRUE,
    fork BOOLEAN DEFAULT FALSE,
    mirror_url VARCHAR(500),
    archived_at TIMESTAMP WITH TIME ZONE,
    created_at_db TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at_db TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Repository snapshots for historical tracking
CREATE TABLE IF NOT EXISTS repository_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id BIGINT REFERENCES repositories(id) ON DELETE CASCADE,
    snapshot_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    stars INTEGER,
    forks INTEGER,
    watchers INTEGER,
    open_issues INTEGER,
    network_count INTEGER,
    subscribers_count INTEGER,
    size INTEGER,
    commit_count INTEGER,
    branch_count INTEGER,
    release_count INTEGER,
    contributor_count INTEGER,
    language_distribution JSONB, -- Store language breakdown
    topic_changes TEXT[], -- Track topic additions/removals
    metadata JSONB -- Additional metadata
);

-- Contributors table
CREATE TABLE IF NOT EXISTS contributors (
    id BIGINT PRIMARY KEY,
    login VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    company VARCHAR(255),
    location VARCHAR(500),
    email VARCHAR(500),
    bio TEXT,
    blog VARCHAR(500),
    twitter_username VARCHAR(100),
    public_repos INTEGER DEFAULT 0,
    public_gists INTEGER DEFAULT 0,
    followers INTEGER DEFAULT 0,
    following INTEGER DEFAULT 0,
    hireable BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    suspended_at TIMESTAMP WITH TIME ZONE,
    created_at_db TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at_db TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Repository contributors junction table
CREATE TABLE IF NOT EXISTS repository_contributors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id BIGINT REFERENCES repositories(id) ON DELETE CASCADE,
    contributor_id BIGINT REFERENCES contributors(id) ON DELETE CASCADE,
    contributions INTEGER DEFAULT 0,
    first_contribution TIMESTAMP WITH TIME ZONE,
    last_contribution TIMESTAMP WITH TIME ZONE,
    is_owner BOOLEAN DEFAULT FALSE,
    permission VARCHAR(20), -- admin, write, read, none
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(repository_id, contributor_id)
);

-- Commits table
CREATE TABLE IF NOT EXISTS commits (
    sha VARCHAR(40) PRIMARY KEY,
    repository_id BIGINT REFERENCES repositories(id) ON DELETE CASCADE,
    author_id BIGINT REFERENCES contributors(id) ON DELETE SET NULL,
    committer_id BIGINT REFERENCES contributors(id) ON DELETE SET NULL,
    message TEXT,
    tree_sha VARCHAR(40),
    parent_shas TEXT[], -- Array of parent commit SHAs
    authored_at TIMESTAMP WITH TIME ZONE,
    committed_at TIMESTAMP WITH TIME ZONE,
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    changed_files INTEGER DEFAULT 0,
    verified BOOLEAN DEFAULT FALSE,
    created_at_db TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transfer events table
CREATE TABLE IF NOT EXISTS transfer_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id BIGINT REFERENCES repositories(id) ON DELETE CASCADE,
    old_owner VARCHAR(255),
    new_owner VARCHAR(255),
    transfer_date TIMESTAMP WITH TIME ZONE,
    transfer_type VARCHAR(100), -- acquisition, spin-off, rebrand, etc.
    confidence_score DECIMAL(3,2) DEFAULT 0.0,
    evidence JSONB, -- Supporting evidence for the transfer
    announced BOOLEAN DEFAULT FALSE,
    announcement_date TIMESTAMP WITH TIME ZONE,
    deal_value DECIMAL(15,2), -- Estimated deal value
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Organization activities table
CREATE TABLE IF NOT EXISTS organization_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- PushEvent, CreateEvent, etc.
    event_id VARCHAR(100) UNIQUE,
    actor VARCHAR(255),
    repository VARCHAR(500),
    payload JSONB,
    public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ML Analysis results table
CREATE TABLE IF NOT EXISTS ml_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_type VARCHAR(50) NOT NULL, -- anomaly_detection, acquisition_prediction, etc.
    repository_id BIGINT REFERENCES repositories(id) ON DELETE CASCADE,
    model_version VARCHAR(50),
    features JSONB, -- Input features used
    predictions JSONB, -- Model predictions
    confidence_score DECIMAL(5,4),
    risk_level VARCHAR(20), -- LOW, MEDIUM, HIGH, CRITICAL
    anomaly_score DECIMAL(5,4),
    acquisition_probability DECIMAL(5,4),
    predicted_acquirer VARCHAR(255),
    timeline_estimate VARCHAR(100),
    key_signals TEXT[],
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Acquisition predictions table
CREATE TABLE IF NOT EXISTS acquisition_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company VARCHAR(255) NOT NULL,
    repository_id BIGINT REFERENCES repositories(id) ON DELETE CASCADE,
    acquisition_probability DECIMAL(5,4) NOT NULL,
    confidence_score DECIMAL(5,4),
    predicted_acquirer VARCHAR(255),
    timeline_estimate VARCHAR(100),
    key_signals TEXT[],
    model_version VARCHAR(50),
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active', -- active, completed, cancelled
    actual_acquisition_date TIMESTAMP WITH TIME ZONE,
    actual_acquirer VARCHAR(255),
    actual_deal_value DECIMAL(15,2),
    notes TEXT
);

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(20),
    category VARCHAR(50), -- api, ml, data_collection, etc.
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API request logs table
CREATE TABLE IF NOT EXISTS api_request_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    endpoint VARCHAR(500),
    method VARCHAR(10),
    user_agent TEXT,
    ip_address INET,
    response_status INTEGER,
    response_time_ms INTEGER,
    user_id VARCHAR(255), -- If authenticated
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    error_message TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_repositories_stars ON repositories(stars DESC);
CREATE INDEX IF NOT EXISTS idx_repositories_language ON repositories(language);
CREATE INDEX IF NOT EXISTS idx_repositories_owner ON repositories(owner);
CREATE INDEX IF NOT EXISTS idx_repositories_updated_at ON repositories(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_repository_snapshots_repo_date ON repository_snapshots(repository_id, snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_repository_snapshots_date ON repository_snapshots(snapshot_date DESC);

CREATE INDEX IF NOT EXISTS idx_contributors_company ON contributors(company);
CREATE INDEX IF NOT EXISTS idx_contributors_location ON contributors(location);

CREATE INDEX IF NOT EXISTS idx_repository_contributors_repo ON repository_contributors(repository_id);
CREATE INDEX IF NOT EXISTS idx_repository_contributors_contrib ON repository_contributors(contributor_id);

CREATE INDEX IF NOT EXISTS idx_commits_repository ON commits(repository_id);
CREATE INDEX IF NOT EXISTS idx_commits_author ON commits(author_id);
CREATE INDEX IF NOT EXISTS idx_commits_committed_at ON commits(committed_at DESC);

CREATE INDEX IF NOT EXISTS idx_transfer_events_repo ON transfer_events(repository_id);
CREATE INDEX IF NOT EXISTS idx_transfer_events_date ON transfer_events(transfer_date DESC);
CREATE INDEX IF NOT EXISTS idx_transfer_events_confidence ON transfer_events(confidence_score DESC);

CREATE INDEX IF NOT EXISTS idx_organization_activities_org ON organization_activities(organization);
CREATE INDEX IF NOT EXISTS idx_organization_activities_created ON organization_activities(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ml_analysis_results_repo ON ml_analysis_results(repository_id);
CREATE INDEX IF NOT EXISTS idx_ml_analysis_results_date ON ml_analysis_results(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_ml_analysis_results_risk ON ml_analysis_results(risk_level);

CREATE INDEX IF NOT EXISTS idx_acquisition_predictions_company ON acquisition_predictions(company);
CREATE INDEX IF NOT EXISTS idx_acquisition_predictions_prob ON acquisition_predictions(acquisition_probability DESC);
CREATE INDEX IF NOT EXISTS idx_acquisition_predictions_date ON acquisition_predictions(prediction_date DESC);

CREATE INDEX IF NOT EXISTS idx_system_metrics_name_date ON system_metrics(metric_name, metric_date DESC);
CREATE INDEX IF NOT EXISTS idx_system_metrics_category ON system_metrics(category);

CREATE INDEX IF NOT EXISTS idx_api_request_logs_timestamp ON api_request_logs(request_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_request_logs_endpoint ON api_request_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_request_logs_status ON api_request_logs(response_status);

-- Create views for common queries
CREATE OR REPLACE VIEW repository_stats AS
SELECT
    r.id,
    r.full_name,
    r.stars,
    r.forks,
    r.language,
    COUNT(DISTINCT rc.contributor_id) as contributor_count,
    MAX(rs.snapshot_date) as last_snapshot,
    AVG(rs.stars) as avg_stars_last_30d,
    AVG(rs.forks) as avg_forks_last_30d
FROM repositories r
LEFT JOIN repository_contributors rc ON r.id = rc.repository_id
LEFT JOIN repository_snapshots rs ON r.id = rs.repository_id
    AND rs.snapshot_date >= NOW() - INTERVAL '30 days'
GROUP BY r.id, r.full_name, r.stars, r.forks, r.language;

CREATE OR REPLACE VIEW acquisition_targets AS
SELECT
    ap.company,
    ap.acquisition_probability,
    ap.predicted_acquirer,
    ap.timeline_estimate,
    r.stars,
    r.language,
    ap.prediction_date,
    ap.key_signals
FROM acquisition_predictions ap
JOIN repositories r ON ap.repository_id = r.id
WHERE ap.status = 'active'
ORDER BY ap.acquisition_probability DESC;

CREATE OR REPLACE VIEW anomaly_summary AS
SELECT
    mar.repository_id,
    r.full_name,
    mar.risk_level,
    mar.anomaly_score,
    mar.analysis_date,
    mar.key_signals
FROM ml_analysis_results mar
JOIN repositories r ON mar.repository_id = r.id
WHERE mar.analysis_type = 'anomaly_detection'
ORDER BY mar.anomaly_score DESC;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at_db = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update timestamps
CREATE TRIGGER update_repositories_updated_at BEFORE UPDATE ON repositories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contributors_updated_at BEFORE UPDATE ON contributors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_repository_contributors_updated_at BEFORE UPDATE ON repository_contributors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_acquisition_predictions_updated_at BEFORE UPDATE ON acquisition_predictions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate repository growth metrics
CREATE OR REPLACE FUNCTION calculate_repository_growth(repo_id BIGINT)
RETURNS TABLE (
    period VARCHAR(20),
    stars_growth DECIMAL(10,2),
    forks_growth DECIMAL(10,2),
    contributor_growth DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        '7d'::VARCHAR(20),
        COALESCE(
            (MAX(CASE WHEN snapshot_date >= NOW() - INTERVAL '7 days' THEN stars END) -
             MIN(CASE WHEN snapshot_date >= NOW() - INTERVAL '7 days' THEN stars END))::DECIMAL(10,2) /
            NULLIF(MIN(CASE WHEN snapshot_date >= NOW() - INTERVAL '7 days' THEN stars END), 0) * 100, 0
        ),
        COALESCE(
            (MAX(CASE WHEN snapshot_date >= NOW() - INTERVAL '7 days' THEN forks END) -
             MIN(CASE WHEN snapshot_date >= NOW() - INTERVAL '7 days' THEN forks END))::DECIMAL(10,2) /
            NULLIF(MIN(CASE WHEN snapshot_date >= NOW() - INTERVAL '7 days' THEN forks END), 0) * 100, 0
        ),
        0::DECIMAL(10,2) -- Contributor growth calculation would require more complex logic
    FROM repository_snapshots
    WHERE repository_id = repo_id;

    RETURN QUERY
    SELECT
        '30d'::VARCHAR(20),
        COALESCE(
            (MAX(CASE WHEN snapshot_date >= NOW() - INTERVAL '30 days' THEN stars END) -
             MIN(CASE WHEN snapshot_date >= NOW() - INTERVAL '30 days' THEN stars END))::DECIMAL(10,2) /
            NULLIF(MIN(CASE WHEN snapshot_date >= NOW() - INTERVAL '30 days' THEN stars END), 0) * 100, 0
        ),
        COALESCE(
            (MAX(CASE WHEN snapshot_date >= NOW() - INTERVAL '30 days' THEN forks END) -
             MIN(CASE WHEN snapshot_date >= NOW() - INTERVAL '30 days' THEN forks END))::DECIMAL(10,2) /
            NULLIF(MIN(CASE WHEN snapshot_date >= NOW() - INTERVAL '30 days' THEN forks END), 0) * 100, 0
        ),
        0::DECIMAL(10,2)
    FROM repository_snapshots
    WHERE repository_id = repo_id;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE repositories IS 'Core repository information from GitHub API';
COMMENT ON TABLE repository_snapshots IS 'Historical snapshots of repository metrics';
COMMENT ON TABLE contributors IS 'GitHub user information for contributors';
COMMENT ON TABLE repository_contributors IS 'Junction table linking repositories and contributors';
COMMENT ON TABLE commits IS 'Commit information from repositories';
COMMENT ON TABLE transfer_events IS 'Detected repository ownership transfers';
COMMENT ON TABLE organization_activities IS 'GitHub organization activity events';
COMMENT ON TABLE ml_analysis_results IS 'Machine learning analysis results';
COMMENT ON TABLE acquisition_predictions IS 'Acquisition probability predictions';
COMMENT ON TABLE system_metrics IS 'System performance and health metrics';
COMMENT ON TABLE api_request_logs IS 'API request logging for analytics';

COMMENT ON VIEW repository_stats IS 'Aggregated repository statistics with recent activity';
COMMENT ON VIEW acquisition_targets IS 'Current acquisition prediction targets';
COMMENT ON VIEW anomaly_summary IS 'Summary of detected anomalies';

COMMENT ON FUNCTION calculate_repository_growth IS 'Calculate growth metrics for a repository over different time periods';