ALTER TABLE revenue_estimates ADD COLUMN IF NOT EXISTS user_count bigint null;
ALTER TABLE revenue_estimates ADD COLUMN IF NOT EXISTS rating text null;
ALTER TABLE revenue_estimates ADD COLUMN IF NOT EXISTS rating_count bigint null;

-- backfill revenue_estimates.name column
UPDATE revenue_estimates re
    SET user_count = scraped.user_count,
        rating = scraped.rating,
        rating_count = scraped.rating_count
    FROM google_workspace scraped
    WHERE scraped.google_id = re.google_id AND scraped.p_date = '2024-05-08';
