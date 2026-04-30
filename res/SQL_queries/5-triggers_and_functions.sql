-- This SQL file builds on the queries seen in the previous file and adds to it:
-- A trigger that responds to the changes in the status of the chokepoints;
-- A function that wraps the rerouting and ship_state update in a way that allows us to avoid the concurrency related issues;



-- The function for rerouting and updating ship_state:
CREATE OR REPLACE FUNCTION handle_chokepoint_deactivation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN

    -- only act when a chokepoint is turned off
    IF OLD.active = TRUE AND NEW.active = FALSE THEN

        -- lock ships (avoid concurrency issues)
        PERFORM 1 FROM ship_state FOR UPDATE;

        -- reroute ships
        WITH ship_pos AS (
            SELECT
                sc.imo,
                sc.wkb_geometry AS ship_pos,
                ht.seaport_id
            FROM ship_state sc
            JOIN heading_to ht ON ht.imo = sc.imo
        ),

        ship_patch AS (
            SELECT
                sp.imo,
                sp.ship_pos,
                sp.seaport_id,
                p.patch_id,
                p.chokepoint
            FROM ship_pos sp
            JOIN patches p
              ON ST_Contains(p.wkb_geometry, sp.ship_pos)
        ),

        blocked_ships AS (
            SELECT
                sp.imo,
                sp.ship_pos,
                ht.seaport_id,
                sp.patch_id
            FROM ship_patch sp
            JOIN heading_to ht ON ht.imo = sp.imo
            JOIN seaports s ON s.seaport_id = ht.seaport_id
            JOIN patches target_patch
              ON ST_Contains(target_patch.wkb_geometry, s.wkb_geometry::geometry)
            WHERE sp.chokepoint = NEW.chokepoint_name
        ),

        reroute_candidates AS (
            SELECT
                bs.imo,
                MODE() WITHIN GROUP (ORDER BY ht2.seaport_id) AS new_seaport_id
            FROM blocked_ships bs
            JOIN ships s1 ON s1.imo = bs.imo
            JOIN ships s2 ON s2.ship_type = s1.ship_type
            JOIN heading_to ht2 ON ht2.imo = s2.imo
            GROUP BY bs.imo
        )

        UPDATE heading_to ht
        SET seaport_id = rc.new_seaport_id
        FROM reroute_candidates rc
        WHERE ht.imo = rc.imo;


        -- update ship states
        WITH directional AS (
            SELECT
                ss.imo,
                ss.wkb_geometry AS current_pos,
                sp.wkb_geometry AS target_pos,

                degrees(
                    ST_Azimuth(
                        ss.wkb_geometry::geography,
                        sp.wkb_geometry::geography
                    )
                ) + (random() * 40 - 20) AS heading

            FROM ship_state ss
            JOIN heading_to ht ON ht.imo = ss.imo
            JOIN seaports sp ON sp.seaport_id = ht.seaport_id
        ),

        candidates AS (
            SELECT
                imo,
                ST_Project(
                    current_pos::geography,
                    10000,
                    radians(heading)
                )::geometry AS next_pos
            FROM directional
        ),

        valid_moves AS (
            SELECT c.*
            FROM candidates c
            WHERE EXISTS (
    			SELECT 1
    			FROM oceans o
    			WHERE ST_Contains(o.geom, c.next_pos)
            )
        )

        INSERT INTO ship_state (imo, wkb_geometry, updated_at)
        SELECT
            imo,
            next_pos,
            clock_timestamp()
        FROM valid_moves
        ON CONFLICT (imo)
        DO UPDATE SET
            wkb_geometry = EXCLUDED.wkb_geometry,
            updated_at   = EXCLUDED.updated_at;

    END IF;

    RETURN NEW;
END;
$$;
-- End of Function;



-- Trigger to handle chokepoint deactivation:
CREATE TRIGGER trg_chokepoint_off
AFTER UPDATE ON chokepoints
FOR EACH ROW
WHEN (OLD.active IS DISTINCT FROM NEW.active AND NEW.active = FALSE)
EXECUTE FUNCTION handle_chokepoint_deactivation();

BEGIN;

-- lock ships
SELECT 1 FROM ship_state FOR UPDATE;

-- reroute ships
WITH ship_pos AS (
    SELECT
        sc.imo,
        sc.wkb_geometry AS ship_pos,
        ht.seaport_id
    FROM ship_state sc
    JOIN heading_to ht ON ht.imo = sc.imo
),

-- 1. Identify patch for each ship
ship_patch AS (
    SELECT
        sp.imo,
        sp.ship_pos,
        sp.seaport_id,
        p.patch_id,
        p.chokepoint
    FROM ship_pos sp
    JOIN patches p
      ON ST_Contains(p.wkb_geometry, sp.ship_pos)
),

-- 2. Define patch pairs (A ↔ B)
patch_pairs AS (
    SELECT
        pA.patch_id AS patch_a,
        pB.patch_id AS patch_b,
        pA.chokepoint
    FROM patches pA
    JOIN patches pB
      ON pA.chokepoint = pB.chokepoint
     AND pA.patch_id <> pB.patch_id
),

-- 3. Find blocked ships (convert seaport geometry properly)
blocked_ships AS (
    SELECT
        sp.imo,
        sp.ship_pos,
        ht.seaport_id,
        sp.patch_id AS current_patch
    FROM ship_patch sp
    JOIN heading_to ht ON ht.imo = sp.imo
    JOIN seaports s ON s.seaport_id = ht.seaport_id

    -- FIX: convert geography → geometry
    JOIN patches target_patch
      ON ST_Contains(
            target_patch.wkb_geometry,
            s.wkb_geometry::geometry
         )

    JOIN chokepoints c
      ON c.chokepoint_name = sp.chokepoint
    WHERE c.active = FALSE
),

-- 4. Reroute based on ship class behavior
reroute_candidates AS (
    SELECT
        bs.imo,
        MODE() WITHIN GROUP (
            ORDER BY ht2.seaport_id
        ) AS new_seaport_id
    FROM blocked_ships bs
    JOIN ships s1 ON s1.imo = bs.imo
    JOIN ships s2 ON s2.ship_type = s1.ship_type
    JOIN heading_to ht2 ON ht2.imo = s2.imo
    GROUP BY bs.imo
)

-- 5. Apply reroute
UPDATE heading_to ht
SET seaport_id = rc.new_seaport_id
FROM reroute_candidates rc
WHERE ht.imo = rc.imo;


-- move ships
WITH directional AS (

    -- 1) current position + destination + heading (ALL ships)
    SELECT
        ss.imo,
        ss.wkb_geometry AS current_pos,
        sp.wkb_geometry AS target_pos,

        degrees(
            ST_Azimuth(
                ss.wkb_geometry::geography,
                sp.wkb_geometry::geography
            )
        ) + (random() * 40 - 20) AS heading

    FROM ship_state ss
    JOIN heading_to ht ON ht.imo = ss.imo
    JOIN seaports sp ON sp.seaport_id = ht.seaport_id

),

candidates AS (

    -- 2) project next movement step
    SELECT
        imo,
        ST_Project(
            current_pos::geography,
            10000,
            radians(heading)
        )::geometry AS next_pos
    FROM directional

),

valid_moves AS (

    -- 3) ensure ship stays in ocean (not land)
    SELECT c.*
    FROM candidates c
    WHERE EXISTS (
    	SELECT 1
    	FROM oceans o
    	WHERE ST_Contains(o.geom, c.next_pos)
    )

)

-- 4) update CURRENT state (not insert history)
INSERT INTO ship_state (imo, wkb_geometry, updated_at)

SELECT
    imo,
    next_pos,
    clock_timestamp()
FROM valid_moves

ON CONFLICT (imo)
DO UPDATE SET
    wkb_geometry = EXCLUDED.wkb_geometry,
    updated_at   = EXCLUDED.updated_at;
-- End of query

COMMIT;