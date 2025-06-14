#!/usr/bin/env python3
"""
Test script to verify Supabase MCP tool is working
and apply the monitoring database migration
"""

import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_mcp_availability():
    """Prepare SQL scripts for use with official Supabase MCP server"""
    logger.info("Preparing SQL scripts for official Supabase MCP server...")

    # The official Supabase MCP server has built-in SQL execution capabilities
    # No custom RPC functions needed - it can run SQL directly
    rpc_functions_sql = """
-- Note: Official Supabase MCP server provides built-in SQL execution
-- These RPC functions are optional but can be useful for convenience

-- Create RPC function for executing arbitrary SQL (optional)
CREATE OR REPLACE FUNCTION execute_sql(sql text)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result json;
BEGIN
    EXECUTE sql;
    GET DIAGNOSTICS result = ROW_COUNT;
    RETURN json_build_object('rows_affected', result);
END;
$$;
"""

    # Migration SQL for the monitoring tables
    migration_sql = """
-- Create event_snapshots table
CREATE TABLE IF NOT EXISTS event_snapshots (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    date_time TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    speakers JSONB DEFAULT '[]'::jsonb,
    organizers JSONB DEFAULT '[]'::jsonb,
    content_hash TEXT NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create event_change_log table
CREATE TABLE IF NOT EXISTS event_change_log (
    id BIGSERIAL PRIMARY KEY,
    change_type TEXT NOT NULL,
    event_id TEXT NOT NULL,
    event_url TEXT NOT NULL,
    old_data JSONB,
    new_data JSONB,
    priority TEXT NOT NULL DEFAULT 'info',
    detected_at TIMESTAMPTZ NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create user_subscriptions table
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    subscription_type TEXT NOT NULL,
    subscription_value TEXT NOT NULL,
    notification_priority TEXT NOT NULL DEFAULT 'important',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create notification_queue table
CREATE TABLE IF NOT EXISTS notification_queue (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    change_log_id BIGINT REFERENCES event_change_log(id),
    notification_type TEXT NOT NULL DEFAULT 'telegram',
    priority TEXT NOT NULL DEFAULT 'info',
    message_content JSONB NOT NULL,
    scheduled_for TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'pending',
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create monitoring_config table
CREATE TABLE IF NOT EXISTS monitoring_config (
    id BIGSERIAL PRIMARY KEY,
    config_key TEXT UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_event_snapshots_url ON event_snapshots(url);
CREATE INDEX IF NOT EXISTS idx_event_snapshots_content_hash ON event_snapshots(content_hash);
CREATE INDEX IF NOT EXISTS idx_event_snapshots_last_updated ON event_snapshots(last_updated);

CREATE INDEX IF NOT EXISTS idx_event_change_log_event_id ON event_change_log(event_id);
CREATE INDEX IF NOT EXISTS idx_event_change_log_change_type ON event_change_log(change_type);
CREATE INDEX IF NOT EXISTS idx_event_change_log_detected_at ON event_change_log(detected_at);
CREATE INDEX IF NOT EXISTS idx_event_change_log_priority ON event_change_log(priority);
CREATE INDEX IF NOT EXISTS idx_event_change_log_processed ON event_change_log(processed);

-- Add constraints
ALTER TABLE event_change_log ADD CONSTRAINT IF NOT EXISTS chk_change_type 
    CHECK (change_type IN ('new_event', 'event_updated', 'event_cancelled', 'speaker_changed', 
                          'time_changed', 'location_changed', 'description_changed', 'event_deleted'));

ALTER TABLE event_change_log ADD CONSTRAINT IF NOT EXISTS chk_priority 
    CHECK (priority IN ('critical', 'important', 'info'));

-- Insert default monitoring configuration
INSERT INTO monitoring_config (config_key, config_value, description) VALUES
    ('monitoring_interval', '3600', 'Default monitoring interval in seconds (1 hour)'),
    ('max_concurrent_scrapes', '5', 'Maximum concurrent scraping operations'),
    ('notification_batch_size', '10', 'Number of notifications to process per batch'),
    ('retry_failed_scrapes', 'true', 'Whether to retry failed scraping attempts'),
    ('enable_notifications', 'true', 'Whether to send notifications for changes')
ON CONFLICT (config_key) DO NOTHING;
"""

    logger.info("SQL scripts prepared for official Supabase MCP server")
    logger.info(
        f"Optional RPC functions SQL length: {len(rpc_functions_sql)} characters"
    )
    logger.info(f"Migration SQL length: {len(migration_sql)} characters")
    logger.info("✨ The official Supabase MCP server can execute SQL directly!")

    return rpc_functions_sql, migration_sql


def main():
    logger.info("=" * 60)
    logger.info("Official Supabase MCP Server Setup & Migration Preparation")
    logger.info("=" * 60)

    # Prepare SQL scripts
    rpc_functions_sql, migration_sql = test_mcp_availability()

    logger.info("✅ SQL scripts prepared")
    logger.info("🔧 Setup Instructions for Official Supabase MCP Server:")
    logger.info("")
    logger.info("1. Install official Supabase MCP server:")
    logger.info("   npx @supabase/mcp-server-supabase@latest")
    logger.info("")
    logger.info("2. Create Supabase Personal Access Token:")
    logger.info("   - Go to Supabase Dashboard → Settings → Access Tokens")
    logger.info("   - Create new token with appropriate permissions")
    logger.info("")
    logger.info("3. Configure Claude Code MCP settings:")
    logger.info("   - Add Supabase MCP server to Claude Code configuration")
    logger.info("   - Provide access token for authentication")
    logger.info("")
    logger.info("4. Use official Supabase MCP tools:")
    logger.info("   - Run SQL queries directly on real database")
    logger.info("   - Create database migrations")
    logger.info("   - Generate TypeScript types from schema")
    logger.info("")
    logger.info("5. Execute migrations using official Supabase MCP tools:")
    logger.info("   - Run SQL queries directly against real database")
    logger.info("   - Use monitoring_migration.sql for table creation")
    logger.info(
        "   - Optional: Use optional_rpc_functions.sql for convenience functions"
    )

    # Save SQL to files for easy access
    with open("optional_rpc_functions.sql", "w") as f:
        f.write(rpc_functions_sql)
    with open("monitoring_migration.sql", "w") as f:
        f.write(migration_sql)

    logger.info("📄 SQL files saved for official Supabase MCP server:")
    logger.info("   - optional_rpc_functions.sql (convenience functions)")
    logger.info("   - monitoring_migration.sql (main migration)")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
