-- Run this query to insert new ship locations into the ship_locations database:

INSERT INTO ship_locations (
    imo,
    updated_at,
    latitude,
    longitude,
    wkb_geometry
)
SELECT
    current.imo,
    CURRENT_TIMESTAMP,

    ST_Y(next.new_geom::geometry),
    ST_X(next.new_geom::geometry),

    next.new_geom
FROM (

    -- 1. Get latest position per ship
    SELECT DISTINCT ON (imo)
        imo,
        wkb_geometry
    FROM ship_locations
    ORDER BY imo, updated_at DESC

) AS current

JOIN heading_to ht ON ht.imo = current.imo
JOIN seaports sp ON sp.seaport_id = ht.seaport_id

-- 2. compute movement
CROSS JOIN LATERAL (
    SELECT
        ST_Project(
            current.wkb_geometry,
            10000,
            ST_Azimuth(
                current.wkb_geometry::geometry,
                sp.wkb_geometry::geometry
            )
        )::geography AS new_geom,

        ST_MakeLine(
            current.wkb_geometry::geometry,
            ST_Project(
                current.wkb_geometry,
                10000,
                ST_Azimuth(
                    current.wkb_geometry::geometry,
                    sp.wkb_geometry::geometry
                )
            )::geometry
        ) AS path
) AS next

-- Ocean constraint: We don't want ships to cross land while they are travelling;
WHERE EXISTS (
    SELECT 1
    FROM oceans o
    WHERE ST_Contains(o.geom, next.path)
);
-- End of query



-- Plot a trajectory for a ship with a given imo
-- Remark: Don't forget to update the imo to the one that you are looking for
SELECT imo, ST_MakeLine(wkb_geometry::geometry ORDER BY updated_at) AS route_geom
FROM ship_locations
WHERE imo = '9708590'
GROUP BY imo;
-- End of query


-- Problem with the row insertions above: They can only create straight lines; if a ships hits the ground, it gets stuck;
-- Our fix: If the new ship location is not within ocean, we attempt again and choose the awimuth at random from a permitted range.
-- See the isnertion query for one imo and ten attempts at update allowed;
-- A query for updating all the ships is presented after this query
WITH directional AS (

    SELECT
        sl.imo,
        sl.wkb_geometry AS current_pos,
        sp.wkb_geometry AS target_pos,

        degrees(
            ST_Azimuth(
                sl.wkb_geometry::geography,
                sp.wkb_geometry::geography
            )
        ) + (random() * 40 - 20) AS heading

    FROM ship_locations sl
    JOIN heading_to ht ON ht.imo = sl.imo
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
        WHERE ST_Contains(o.geom::geometry, c.next_pos)
    )

)

INSERT INTO ship_locations (
    imo,
    updated_at,
    latitude,
    longitude,
    wkb_geometry
)
SELECT
    imo,
    clock_timestamp(),
    ST_Y(next_pos),
    ST_X(next_pos),
    next_pos
FROM valid_moves;
-- End of query



-- Create an index to speed up the ship_location update:
CREATE INDEX ship_locations_imo_time_idx
ON ship_locations (imo, updated_at DESC);
-- End of query




-- Notice that even after creating an index on ship_locations, the queries became slower;
-- This happens due to the fact that the size of the ship_locations dataset grows
-- To mitigate this, we created a separate table:
-- This table stores ONLY the latest position of each ship.
-- It is the core of your simulation performance.

CREATE TABLE ship_state (
    imo VARCHAR(9),
	wkb_geometry geometry(Point, 4326),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT clock_timestamp(),
	PRIMARY KEY (imo),
    FOREIGN KEY (imo) REFERENCES ships(imo) ON DELETE CASCADE
	);
	
	-- We create indexes for ship_state on the geometry and 
CREATE INDEX ship_state_geom_gix
ON ship_state
USING GIST (wkb_geometry);

CREATE INDEX ship_state_imo_idx
ON ship_state (imo);

	-- Populate the ship_state before the first run:
INSERT INTO ship_state (imo, wkb_geometry, updated_at)
SELECT
    imo,
    wkb_geometry::geometry,
    clock_timestamp()
FROM ship_locations
WHERE updated_at = (
    SELECT MAX(updated_at)
    FROM ship_locations sl
    WHERE sl.imo = ship_locations.imo
);
-- End of query

WITH directional AS (

    SELECT
        sl.imo,
        sl.wkb_geometry AS current_pos,
        sp.wkb_geometry AS target_pos,

        degrees(
            ST_Azimuth(
                sl.wkb_geometry::geography,
                sp.wkb_geometry::geography
            )
        ) + (random() * 40 - 20) AS heading

    FROM ship_locations sl
    JOIN heading_to ht ON ht.imo = sl.imo
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

INSERT INTO ship_locations (
    imo,
    updated_at,
    latitude,
    longitude,
    wkb_geometry
)
SELECT
    imo,
    clock_timestamp(),
    ST_Y(next_pos),
    ST_X(next_pos),
    next_pos
FROM valid_moves;

-- Updated ocean-constraint aware query for generating new sea positions that makes use of and updates ship_state table 
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

    -- 3) ensure ship stays in ocean (must be inside valid ocean polygons)
    SELECT c.*
    FROM candidates c
    WHERE EXISTS (
        SELECT 1
        FROM oceans o
        WHERE ST_Contains(o.geom, c.next_pos)
    )

)

-- 4) update CURRENT state (not insert history)
INSERT INTO ship_state (
    imo,
    wkb_geometry,
    updated_at
)
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



-- Run this query to change the status of a chokepoint:
UPDATE chokepoints
SET active = FALSE
WHERE chokepoint_name = 'Suez Canal';
-- End of query


-- Reroute ships using our logic of patches and chokepoints:
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

-- Query End








