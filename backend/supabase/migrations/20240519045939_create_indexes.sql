-- This is already applied to the database from the unique (marketplace_name, marketplace_id) constraint
-- CREATE INDEX idx_plugin_marketplace_name ON public.plugin(marketplace_name);]
CREATE INDEX idx_plugin_marketplace_id ON public.plugin(marketplace_id);
CREATE INDEX idx_plugin_user_count ON public.plugin(user_count);
CREATE INDEX idx_plugin_rating_count ON public.plugin(rating_count);
CREATE INDEX idx_plugin_revenue_upper_bound ON public.plugin(revenue_upper_bound);


CREATE INDEX idx_google_workspace_p_date ON public.google_workspace(p_date);
CREATE INDEX idx_chrome_extension_p_date ON public.chrome_extension(p_date);