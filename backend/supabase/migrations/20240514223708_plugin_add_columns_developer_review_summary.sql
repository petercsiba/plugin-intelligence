ALTER TABLE public.plugin DROP COLUMN search_terms;
-- TODO(P0, ux): Replace this with a canonical company object;
ALTER TABLE public.plugin ADD COLUMN developer_name;
ALTER TABLE public.plugin ADD COLUMN developer_link;
ALTER TABLE public.plugin ADD COLUMN reviews_summary;
