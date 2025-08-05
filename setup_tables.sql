-- Direct SQL script to create tables for FastAPI app
-- Using direct SQL scripts like in the Crispy Crown project for reliable deployment

-- Begin transaction for data consistency
BEGIN;

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

-- Insert admin user if it doesn't exist
-- Note: password is 'admin123' hashed with bcrypt
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM "user" WHERE username = 'admin') THEN
        INSERT INTO "user" (id, email, username, hashed_password, full_name, is_active, is_admin)
        VALUES (
            '00000000-0000-0000-0000-000000000000',
            'admin@example.com',
            'admin',
            '$2b$12$Q9oLaVG5NwAvRLWZd7Zyb.jLCFJ8W9oNvTMfOFKkpN8gzNkY7sdDG',
            'System Administrator',
            TRUE,
            TRUE
        );
        RAISE NOTICE 'Admin user created';
    ELSE
        RAISE NOTICE 'Admin user already exists';
    END IF;
END $$;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database setup completed successfully!';
END $$;

-- Commit the transaction
COMMIT;
