def schema_collection(db, model, data):
    schema = db.model_schema(model)
    data_model = getattr(db.model, model)

    model_list = []
    if isinstance(data, list):
        # data is an array
        for ele in data:
            if "id" in ele:
                # id as been passed, instance exists
                existing = data_model.query.get(ele["id"])
                new = schema.load(ele, session=db.session, instance=existing)
                new.id = existing.id
                db.session.rollback()
                res = db.session.merge(new)
                db.session.commit()
                model_list.append(res)
            else:  # assume its a new model
                new = schema.load(ele, session=db.session)
                db.session.add(new)
                db.session.commit()
                model_list.append(new)
    return model_list


def schema_collection_hanlder(db, model, data):
    schema = db.model_schema(model)
    collections = schema._available_nests()  ## list of collections for a schema

    for coll in collections:
        if coll in data:
            new_col = schema_collection(db, coll, data[coll])

    pass