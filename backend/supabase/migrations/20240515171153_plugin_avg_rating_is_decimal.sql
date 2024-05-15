ALTER TABLE plugin RENAME COLUMN rating TO avg_rating;
ALTER TABLE plugin ALTER COLUMN avg_rating TYPE decimal USING (NULLIF(avg_rating, '')::decimal);
