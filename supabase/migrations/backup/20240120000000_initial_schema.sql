-- Create oauth_tokens table
create table if not exists public.oauth_tokens (
    id uuid default gen_random_uuid() primary key,
    state varchar unique not null,
    notion_token text not null,
    workspace_id varchar,
    workspace_name varchar,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create docusign_states table
create table if not exists public.docusign_states (
    id uuid default gen_random_uuid() primary key,
    state varchar unique not null,
    params jsonb not null,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    expires_at timestamp with time zone not null
);

-- Enable RLS but allow all operations for now
alter table public.oauth_tokens enable row level security;
alter table public.docusign_states enable row level security;

create policy "Enable all for oauth_tokens"
    on public.oauth_tokens for all using (true);

create policy "Enable all for docusign_states"
    on public.docusign_states for all using (true); 