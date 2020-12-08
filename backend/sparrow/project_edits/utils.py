from sqlalchemy import Table, delete

def create_publication_collection(publications, publication_collection, db):
    '''
    function to create a publication collection list from the incoming changeset.

    - publications: the changeset list of publciations
    - publication_collection: the publications from the existing model
    - db: the database connection
    '''
    # find what publcations are the same based on id.. then edit attributes.
    # TODO: make this simpler?

    collection = [] 
    for ele in publications:

        if 'id' not in ele:

            #NOTE: assuming that if no id is in changeset, then the DOI was added on the frontend
            #collection.append(create_publication_object(ele, db))
            Publication = db.model.publication
            model_pub = Publication.get_or_create(doi=ele['doi'])
            
            collection.append(model_pub)

        else:
            model_pub = grab_by_id(publication_collection, ele['id'],db)

            for k in ele:
              setattr(model_pub, k, ele[k])

            collection.append(model_pub)

    return collection

def grab_by_id(publication_collection, id, db):
    '''
        Returns a publication model object from the collection in the project model
    '''
    for pub in publication_collection:
        if pub.id == id:
            return pub

## try using get_or_create instead
def create_publication_object(pub, db):
    '''
     deals with additions of publications to the collection. 

     - Pub: the pub object that was added on the frontend, no associated id. 

     needs to check if doi exists in database, otherwise create a new publication object
    '''
    # Publication model
    Publication = db.model.publication

    # using the try and except is probably a bad way to do this..
    try:
        # see if the doi exists in the database
        model_pub = db.session.query(Publication).filter(Publication.doi==pub['doi']).one()

        # if it does, set the attributes
        for k in pub:
            setattr(model_pub, k, pub[k])

        #add it to the collection
        return model_pub
    except: 
        # if it does NOT, create a new publication model object
        model_pub = Publication()

        # set the attributes
        for k in pub:
            setattr(model_pub, k, pub[k])

        # add it to the collection
        return model_pub