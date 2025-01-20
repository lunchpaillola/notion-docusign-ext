-- Add authorization_code to docusign_states
DO $$ 
BEGIN
    -- Add column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'docusign_states' 
        AND column_name = 'authorization_code'
    ) THEN
        ALTER TABLE public.docusign_states 
        ADD COLUMN authorization_code varchar;
    END IF;

    -- Create index if it doesn't exist
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'docusign_states'
        AND indexname = 'idx_docusign_states_auth_code'
    ) THEN
        CREATE INDEX idx_docusign_states_auth_code 
        ON public.docusign_states(authorization_code);
    END IF;
END $$; 