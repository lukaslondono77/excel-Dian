-- Create database schema for Excel to DIAN SaaS application

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (for future auth integration)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- File uploads table
CREATE TABLE IF NOT EXISTS file_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    row_count INTEGER NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'parsed',
    metadata JSONB
);

-- PDF generations table
CREATE TABLE IF NOT EXISTS pdf_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    file_id UUID REFERENCES file_uploads(id),
    pdf_filename VARCHAR(255) NOT NULL,
    s3_url TEXT NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'completed',
    metadata JSONB
);

-- Workflow logs table (for gateway service)
CREATE TABLE IF NOT EXISTS workflow_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    workflow_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_file_uploads_user_id ON file_uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_file_uploads_uploaded_at ON file_uploads(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_pdf_generations_user_id ON pdf_generations(user_id);
CREATE INDEX IF NOT EXISTS idx_pdf_generations_file_id ON pdf_generations(file_id);
CREATE INDEX IF NOT EXISTS idx_pdf_generations_generated_at ON pdf_generations(generated_at);
CREATE INDEX IF NOT EXISTS idx_workflow_logs_user_id ON workflow_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_workflow_logs_created_at ON workflow_logs(created_at);

-- Insert sample data for testing
INSERT INTO file_uploads (id, user_id, filename, file_size, row_count, status) VALUES
    (uuid_generate_v4(), 'user_123', 'sample_data.xlsx', 1024000, 150, 'parsed'),
    (uuid_generate_v4(), 'user_456', 'financial_report.xlsx', 2048000, 300, 'parsed')
ON CONFLICT DO NOTHING;

-- Create a view for combined file and PDF data
CREATE OR REPLACE VIEW file_pdf_summary AS
SELECT 
    fu.id as file_id,
    fu.filename,
    fu.row_count,
    fu.uploaded_at,
    pg.id as pdf_id,
    pg.pdf_filename,
    pg.s3_url,
    pg.generated_at,
    fu.user_id
FROM file_uploads fu
LEFT JOIN pdf_generations pg ON fu.id = pg.file_id
ORDER BY fu.uploaded_at DESC; 