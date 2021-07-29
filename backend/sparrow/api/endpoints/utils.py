from shapely.geometry import mapping, Point
from geoalchemy2.shape import from_shape
from ..api_info import get_field_description


def construct_schema_fields_object(schema):
    """func to create schema field documentation for the API
    field.required
    field.dump_only == id, audit_id
    field.allow_none
    """
    fields = schema.fields
    fields_object = {}
    for f in fields:
        field = fields[f]
        name = getattr(field, "data_key", f)
        if nested_schema := getattr(field, "schema", None):
            # nested model
            type_ = nested_schema.__class__.__name__
            if nested_schema.many:
                type_ += "[]"
            fields_object[name] = {
                "type": type_,
                **nested_model_link(field),
                **get_field_description(name),
                **construct_field_info(field),
            }
        else:
            type_ = field.__class__.__name__
            fields_object[name] = {
                "type": type_,
                **get_field_description(name),
                **construct_field_info(field),
            }
    return fields_object


def nested_model_link(field):
    """ generate api route for nested model """
    model_name = field.schema.opts.model.__name__
    route = ""
    if "vocabulary" in model_name or "tags" in model_name:
        schema, model = model_name.split("_", 1)
        route = f"/api/v2/{schema}/{model}"
    else:
        route = f"/api/v2/models/{model_name}"
    return {"link": route}


def construct_field_info(field):
    attributes = {
        "required": "required",
        "dump_only": "read_only",
        "allow_none": "nullable",
    }

    obj = {}
    for param, laymans in attributes.items():
        obj[laymans] = getattr(field, param)
    return obj


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


def collection_handler(db, data):
    """
    A function to handle creating new collections.

    db: database connection
    data: a python dictionary! Not list.

    NOTE: Right now it replaces the old collection with whatever is passed.

    """

    names = []  # sample
    col_names = []  # sample_collection
    plural_names = []
    for ele in data:
        if type(data[ele]) is list:  # collections will be lists
            # check if it's plural
            # TODO: need to check for analysis pluralization
            if ele[-1] == "s" and ele != "analysis":
                names.append(ele[:-1])
                col_names.append(ele[:-1] + "_collection")
                plural_names.append(ele)
            elif "collection" in ele:
                col_names.append(ele)
                names.append(ele.replace("_collection", ""))
            else:
                names.append(ele)
                col_names.append(ele + "_collection")

    ## maybe there are no collections
    if len(col_names) == 0 or len(names) == 0:
        return data

    # need to rename the key for plural keys
    for name in plural_names:
        data[name[:-1]] = data[name]
        data.pop(name)
    for i, name in enumerate(names):
        data[col_names[i]] = data[name]
        data.pop(name)

    ## Create a loop ability to go over the len of both name lists
    # for each name and collection name we perform the same actions.
    for i, val in enumerate(names):
        # if type(data[col_names[i]]) is list:
        #     data = collection_handler(db, data[col_names[i]])
        db_model = getattr(db.model, val)  ## the model for the collection.

        ## will become a new column in data that says model_collection
        collection = []
        for ele in data[col_names[i]]:
            if "id" not in ele:
                ## The data probably doesn't exsist in the db
                # get model that matches or create a new one.
                # NOTE: **ele spreads everything, so theres a chance we could be duplicating data...
                ele = location_check(ele, array=False)  ## this workds
                material_check(db, ele, array=False)
                new_model = db_model.get_or_create(
                    **ele
                )  ## doesn't set location for sample
                if "location" in ele:
                    new_model.location = ele["location"]

                collection.append(new_model)
            else:
                # id is present in the object.
                ele = location_check(ele, array=False)
                material_check(db, ele, array=False)
                existing_model = db_model.get_or_create(id=ele["id"])
                if "location" in ele:
                    existing_model.location = ele["location"]

                # for k in ele:
                #     setattr(existing_model, k, ele[k])
                collection.append(existing_model)
        data[col_names[i]] = collection

    return data
