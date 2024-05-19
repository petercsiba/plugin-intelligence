CREATE TABLE intake_form (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::TEXT, now()) NOT NULL,
    name TEXT NULL,
    email TEXT NULL,
    job_position TEXT NULL,
    intent TEXT NULL,
    message TEXT NULL,
    action TEXT NULL
);

ALTER TABLE public.intake_form ENABLE ROW LEVEL SECURITY;