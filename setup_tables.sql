-- Direct SQL script to create tables for FastAPI app
-- This is similar to the approach you used in the Crispy Crown project

-- Create user table if it doesn't exist
CREATE TABLE IF NOT EXISTS "user" (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(100) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS user_email_idx ON "user" (email);
CREATE INDEX IF NOT EXISTS user_username_idx ON "user" (username);

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Tables created successfully!';
END $$;
