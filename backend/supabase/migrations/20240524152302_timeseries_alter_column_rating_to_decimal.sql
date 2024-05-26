-- Update the rating column to convert 'K' and 'M' suffixes to numeric values
UPDATE google_workspace
SET rating = CASE
    WHEN rating LIKE '%K%' THEN (TRIM(TRANSLATE(rating, 'K+', ''))::numeric * 1000)::text
    WHEN rating LIKE '%M%' THEN (TRIM(TRANSLATE(rating, 'M+', ''))::numeric * 1000000)::text
    ELSE rating
END
WHERE rating ~ '[^0-9]';

ALTER TABLE chrome_extension ALTER COLUMN rating TYPE decimal USING (NULLIF(rating, '')::decimal);
ALTER TABLE google_workspace ALTER COLUMN rating TYPE decimal USING (NULLIF(rating, '')::decimal);