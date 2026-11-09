CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO users (name, email) VALUES 
('Иван Иванов', 'ivan@example.com'),
('Петр Петров', 'petr@example.com'),
('Анна Сидорова', 'anna@example.com');

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    json_data JSONB,
    post_date  TIMESTAMP WITH TIME ZONE
);

CREATE TABLE ga4_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_pseudo_id VARCHAR(255),
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    country VARCHAR(100),
    region VARCHAR(100),
    city VARCHAR(100),
    
    lang VARCHAR(10),
    device_cat VARCHAR(50),
    platform VARCHAR(50),
    os VARCHAR(50),
    browser VARCHAR(50),
    screen_res VARCHAR(20),
    
    first_user_source VARCHAR(100),
    first_user_medium VARCHAR(100),
    engagement_time_msec INT DEFAULT 0,
    is_engaged BOOLEAN,

    uncategorized JSONB
);

CREATE INDEX idx_ga4_sessions_timestamp ON ga4_sessions (event_timestamp);
CREATE INDEX idx_ga4_sessions_geo ON ga4_sessions (country, region, city);
CREATE INDEX idx_ga4_sessions_traffic ON ga4_sessions (first_user_source, first_user_medium);
