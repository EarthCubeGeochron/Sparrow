from shapely.geometry import mapping, Point
from geoalchemy2.shape import from_shape


def create_location_from_coordinates(longitude, latitude):
    """This function will create the json-like object in database from long & lat given in a post request"""
    location = from_shape(Point(longitude, latitude), srid=4326)
    return location


def location_check(data, array=True):
    """
    function to check for location info and create a location column and drop lat and long
    """
    if array:
        for ele in data:
            if "longitude" and "latitude" in ele:
                ele["location"] = create_location_from_coordinates(
                    float(ele["longitude"]), float(ele["latitude"])
                )
                ele.pop("longitude")
                ele.pop("latitude")
    else:
        if "longitude" and "latitude" in data:
            data["location"] = create_location_from_coordinates(
                float(data["longitude"]), float(data["latitude"])
            )
            data.pop("longitude")
            data.pop("latitude")

    return data


def material_check(db, changes, array=True):
    """Checks if material exists in database.
    If passed material is new, it is added to vocabulary.material before the sample is updated.
    """
    if array:
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
    else:
        if "material" not in changes:
            pass
        else:
            Material = db.model.vocabulary_material
            current_materials = db.session.query(Material).all()

            ## This has to happen otherwise the materials has ()'s and ""'s around it
            current_material_list = []
            for row in current_materials:
                current_material_list.append(row.id)

            if changes["material"] not in current_material_list:
                db.session.add(Material(id=changes["material"]))
                db.session.commit()


def commit_changes(db, model, data):
    """
    function to create a new model given a python dict (data) and commit it to the database
    """
    ## spread operator like **kwargs
    new_row = model(**data)

    ## add to session and try to commit, rollback if there are errors
    db.session.add(new_row)
    try:
        db.session.commit()
    except:
        db.session.rollback()


def commit_edits(db, model, data, id_=None):
    """
    function to put edits into a row of the database
    """

    if id_ == None:
        query_id = data["id"]
        keys = list(data.keys())
        keys.remove("id")
    else:
        query_id = id_
        keys = list(data.keys())

    ## grab the row we are gonna change
    row = db.session.query(model).filter_by(id=query_id).one()

    for item in keys:
        setattr(row, item, data[item])  ## Set the new value

    try:
        db.session.commit()
    except:
        db.session.rollback()


def collection_handler(db, data, schema):
    """
    Make simpler by using schema._available_nests() to check if its a "collection"
    A function to handle creating new collections.

    This function will assume that collections passed will be as id's

    db: database connection
    data: a python dictionary! Not list.
    schema: the schema interface for the current model

    returns: data, model_collections

        model_collections will be a dictionary where keys correspond to what they would appear as in model
    """
    nests = schema._available_nests()

    names = []  # sample
    for ele in data:
        if ele in nests:
            names.append(ele)

    ## maybe there are no collections
    if len(names) == 0:
        return data

    # for each name that is a collection
    # get the nested models by id and add them to model_collections -> to be added to the model later
    model_collections = {}
    for name in names:

        db_model = getattr(db.model, name)  ## the model for the collection.
        ids = data[name]

        collection = []
        for id in ids:
            instance = db.session.query(db_model).get(id)
            collection.append(instance)

        collection_name = name + "_collection"
        model_collections[collection_name] = collection

        data.pop(name)

    return data, model_collections
