ALTER TABLE google_workspace_metadata ADD COLUMN IF NOT EXISTS lowest_paid_tier text;
ALTER TABLE chrome_extension_metadata ADD COLUMN IF NOT EXISTS lowest_paid_tier text;
