from ..context import app_context
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, Polygon
from sparrow.core.api.endpoints.utils import create_location_from_coordinates


def create_bound_shape(pnts: [float], srid=4326):
    """
    Function to create a bounding polygon location filtering

    points: needs to be 4 numbers long, [minLong, minLat, maxLong, maxLat]
    """
    # TODO: make it accept any number of points
    points = [pnt for pnt in pnts]  ## make sure all values are positive b/c of error
    minLong, minLat, maxLong, maxLat = points

    poly = Polygon(
        [
            [minLong, minLat],
            [minLong, maxLat],
            [maxLong, minLat],
            [maxLong, maxLat],
            [minLong, minLat],
        ]
    )
    bounding_poly = from_shape(poly, srid=srid)

    return bounding_poly


def create_coordinates_from_location(location):
    """
    Takes location column from database (SIRD:4346;POINT(long,lat))
    and turns it into {'type':'point','coordinates':[long,lat]}
    """
    if location is None:
        return None
    return mapping(to_shape(location))


def make_changes(tablename, changes, session):
    """Function that takes in a list of dictionaries with changes to the database

    -tablename: name of table class, sqlalchemy object.
    -changes: list of objects. with changes to be persisted
    -session: current session on the engine.

    Creates pending changes, can be seen in the session.dirty

    """
    ## TODO: Context manager for the function.. Error checking that would call a session.rollback()

    new_changes = project_pub_check(changes)

    for ele in new_changes:

        ## make sure the ID was passed
        if "id" not in ele:
            raise Exception("You need to pass the row ID")

        ## change the longitude and latitude values to location with the correct format
        if "longitude" and "latitude" in ele:
            ele["location"] = create_location_from_coordinates(
                float(ele["longitude"]), float(ele["latitude"])
            )
            ele.pop("longitude")
            ele.pop("latitude")

        ## get the keys and the id
        query_id = ele["id"]
        keys = list(ele.keys())
        keys.remove("id")

        ## grab the row we are gonna change
        row = session.query(tablename).filter_by(id=query_id).one()

        for item in keys:
            setattr(row, item, ele[item])  ## Set the new value


def material_check(db, changes):
    """Checks if material exists in database.
    If passed material is new, it is added to vocabulary.material before the sample is updated.
    """

    for ele in changes:
        if "material" not in ele:
            pass
        else:
            Material = db.model.vocabulary_material
            current_materials = db.session.query(Material).all()

            ## This has to happen otherwise the materials has ()'s and ""'s around it
            current_material_list = []
            for row in current_materials:
                current_material_list.append(row.id)

            if ele["material"] not in current_material_list:
                db.session.add(Material(id=ele["material"]))
                db.session.commit()


def project_pub_check(changes):
    """
    Handler for incoming changes to projects and publication. For now will just ignore them.
    """
    proj_pub_list = ["project_id", "proj_name", "pub_id", "DOI"]

    ## Check proj_pub_list contains a field from changes
    # if it does, remove it
    for ele in changes:
        for i in ele:
            if i in proj_pub_list:
                ele.pop(i)

    return changes
