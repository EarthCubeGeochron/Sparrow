from sqlalchemy import Table, delete


def handle_publications(project, db):
    '''
        Handles the publications array from project model. 

        project: full data model returned from request
        db: database that can have query and session called upon (sqlalchemy)
    '''
    if 'publications' not in project:
        pass

    ## will be a list of pub objects
    pubs = project['publications']

    model = db.model.publication

    for ele in pubs:
        ## need to add a check to see if pub is in database and add if not
        pub = db.session.query(model).get(ele['id'])

        for k in ele:
            setattr(pub, k, ele[k])
    
    project.pop('publications')
    return project

def edit_project_references(db, id_number:int, model: str):
    '''
        Function to delete project_(publication/sample) relationships using sqlalchemy Core

        - db: database
        - id_number (int): id number in the reference table corresponding to the row to be deleted
        - model (str): either "publication" or "sample"
    '''
    if id_number is None:
        pass
    connection = db.engine.connect()
    # use some sqlalchemy expressional langauge to delete rows.

    # get project_publication table
    table = Table(f"project_{model}", db.meta, autoload=True, autoload_with=db.engine)

    if model == "publication":
        delete_statement = delete(table).where(table.c.publication_id == id_number)
    if model == "sample":
        delete_statement = delete(table).where(table.c.sample_id == id_number)

    connection.execute(delete_statement)