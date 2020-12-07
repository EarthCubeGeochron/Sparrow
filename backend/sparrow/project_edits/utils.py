from sqlalchemy import Table, delete

def create_publication_collection(publications, publication_collection, db):
    '''
    function to create a publication collection list from the incoming changeset.

    - publications: the changeset list of publciations
    - publication_collection: the publications from the existing model
    - db: the database connection
    '''
    # find what publcations are the same based on id.. then edit attributes.
    # TODO: make this simpler? Make functionallity to create a new publication object

    collection = []
    def grab_by_id(publication_collection, id, db):
        for pub in publication_collection:
            if pub.id == id:
                return pub

    for ele in publications:

        # if there is no id.. means it was added in
        if 'id' not in ele:
            collection.append(create_publication_object(ele, db))
        else:

            model_pub = grab_by_id(publication_collection, ele['id'],db)

            for k in ele:
              setattr(model_pub, k, ele[k])

            collection.append(model_pub)

    return collection

def create_publication_object(pub, db):
    '''
     - Pub: the pub object that was added on the frontend, no associated id. 

     needs to check if doi exists in database, otherwise create a new publication object
    '''
    Publication = db.model.publication

    try:
        model_pub = db.session.query(Publication).filter(Publication.doi==pub['doi']).one()
        
        for k in pub:
            setattr(model_pub, k, pub[k])
        
        return model_pub
    except: 
        model_pub = Publication()

        for k in pub:
            setattr(model_pub, k, pub[k])
        return model_pub