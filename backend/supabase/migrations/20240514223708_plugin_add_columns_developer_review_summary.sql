ALTER TABLE public.plugin DROP COLUMN search_terms;
ALTER TABLE public.plugin
ADD COLUMN developer_name TEXT,
ADD COLUMN developer_link TEXT,
ADD COLUMN reviews_summary TEXT;
