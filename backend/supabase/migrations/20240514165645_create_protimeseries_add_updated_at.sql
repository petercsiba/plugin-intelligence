ALTER TABLE public.google_workspace ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL;

CREATE TRIGGER update_google_workspace_updated_at
BEFORE UPDATE ON public.google_workspace
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE public.chrome_extension ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL;

CREATE TRIGGER update_chrome_extension_updated_at
BEFORE UPDATE ON public.chrome_extension
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
