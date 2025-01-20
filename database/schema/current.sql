-- Current database schema
CREATE TABLE IF NOT EXISTS public.oauth_tokens (
    id uuid default gen_random_uuid() primary key,
    state varchar unique not null,
    notion_token text not null,
    workspace_id varchar,
    workspace_name varchar,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

CREATE TABLE IF NOT EXISTS public.docusign_states (
    id uuid default gen_random_uuid() primary key,
    state varchar unique not null,
    params jsonb not null,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    expires_at timestamp with time zone not null,
    authorization_code varchar
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_docusign_states_auth_code 
ON public.docusign_states(authorization_code);

-- RLS Policies
ALTER TABLE public.oauth_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.docusign_states ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all for oauth_tokens"
    ON public.oauth_tokens FOR ALL USING (true);

CREATE POLICY "Enable all for docusign_states"
    ON public.docusign_states FOR ALL USING (true); 