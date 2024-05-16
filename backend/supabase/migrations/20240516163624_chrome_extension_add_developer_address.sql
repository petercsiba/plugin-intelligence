ALTER TABLE public.chrome_extension ADD COLUMN developer_address TEXT NULL;
-- link, name might be unknown for extensions removed from the chrome store
ALTER TABLE public.chrome_extension ALTER COLUMN link DROP NOT NULL;
ALTER TABLE public.chrome_extension ALTER COLUMN name DROP NOT NULL;
