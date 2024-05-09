ALTER TABLE chrome_extension ADD COLUMN IF NOT EXISTS logo_link text null;
ALTER TABLE google_workspace ADD COLUMN IF NOT EXISTS logo_link text null;
ALTER TABLE revenue_estimates ADD COLUMN IF NOT EXISTS logo_link text null;

ALTER TABLE chrome_extension ADD COLUMN IF NOT EXISTS featured_img_link text null;
ALTER TABLE google_workspace ADD COLUMN IF NOT EXISTS featured_img_link text null;
