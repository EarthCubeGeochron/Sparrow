/*
Creates a GeoJSON object from sample table
*/
SELECT json_build_object(
    'type', 'Feature',
    'properties', json_build_object(
        'id', id,
        'name', name,
        'material', material
    )::json,
    'geometry', ST_AsGeoJSON(location)::json
) FROM sample WHERE location IS NOT null;