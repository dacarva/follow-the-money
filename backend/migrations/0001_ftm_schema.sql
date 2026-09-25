CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA extensions;

REVOKE ALL ON SCHEMA ftm FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA ftm FROM PUBLIC;

DO $$
DECLARE r text;
BEGIN
  FOREACH r IN ARRAY ARRAY['anon', 'authenticated'] LOOP
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
      EXECUTE format('REVOKE ALL ON SCHEMA ftm FROM %I', r);
      EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA ftm FROM %I', r);
      EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA ftm REVOKE ALL ON TABLES FROM %I', r);
      EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA ftm REVOKE ALL ON SEQUENCES FROM %I', r);
      EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA ftm REVOKE ALL ON FUNCTIONS FROM %I', r);
    END IF;
  END LOOP;
END $$;

-- R23: RLS deny-all on anything in public. A fresh project has no tables there;
-- this covers any that exist, and the PR check below fails any later public table without RLS.
DO $$
DECLARE t text;
BEGIN
  FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t);
  END LOOP;
END $$;
