-- Fix missing case_number_seq sequence
-- Run with: docker-compose exec postgres psql -U bankrot -d bankrot -f /fix_sequence.sql
-- Or copy-paste into psql

-- Create sequence if it doesn't exist
CREATE SEQUENCE IF NOT EXISTS case_number_seq START WITH 1 INCREMENT BY 1;

-- Set sequence to max existing case number + 1 (if cases exist)
DO $$
DECLARE
    max_num INTEGER;
BEGIN
    SELECT COALESCE(
        MAX(CAST(SPLIT_PART(case_number, '-', 3) AS INTEGER)),
        0
    ) INTO max_num
    FROM cases
    WHERE case_number ~ '^BP-[0-9]{4}-[0-9]{4}$';

    -- Only set sequence value if there are existing cases
    IF max_num > 0 THEN
        PERFORM setval('case_number_seq', max_num);
        RAISE NOTICE 'Sequence set to %', max_num;
    ELSE
        RAISE NOTICE 'No existing cases found, sequence starts at 1';
    END IF;
END $$;

-- Verify sequence exists
SELECT sequence_name, start_value, increment
FROM information_schema.sequences
WHERE sequence_name = 'case_number_seq';
