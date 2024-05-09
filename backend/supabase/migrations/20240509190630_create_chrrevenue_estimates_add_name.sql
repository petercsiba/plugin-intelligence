ALTER TABLE revenue_estimates ADD COLUMN IF NOT EXISTS name text null;

-- backfill revenue_estimates.name column
UPDATE revenue_estimates re
    SET name = scraped.name
    FROM google_workspace scraped
    WHERE scraped.google_id = re.google_id AND scraped.p_date = '2024-05-08';
