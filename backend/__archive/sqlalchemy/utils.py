from sqlalchemy import Table, select
import pandas as pd


def get_proj_pub(db):
    """
    Creates a dataframe that joins publications on projects and contains sample_id to
    merge onto main dataframe in view.
    """
    connection = db.engine.connect()

    ## Tables getting mapped using expressional language
    project_pub = Table(
        "project_publication", db.meta, autoload=True, autoload_with=db.engine
    )
    project_sample = Table(
        "project_sample", db.meta, autoload=True, autoload_with=db.engine
    )

    ## Select Statments
    project_pub = connection.execute(select([project_pub]))
    project_sample = connection.execute(select([project_sample]))

    ## Turn into pd.DataFrames
    project_pub = pd.DataFrame(project_pub, columns=project_pub.keys())
    project_sample = pd.DataFrame(project_sample, columns=project_sample.keys())

    df = pd.merge(project_sample, project_pub, on="project_id")

    df.drop(["audit_id_x", "audit_id_y"], axis=1, inplace=True)

    ## Create a Projects dataframe with id and name
    Project = Table("project", db.meta, autoload=True, autoload_with=db.engine)
    Project = connection.execute(select([Project]))
    Projects = pd.DataFrame(Project, columns=Project.keys())
    Projects = Projects[["id", "name"]]
    Projects.rename(columns={"id": "project_id", "name": "proj_name"}, inplace=True)

    ## Create a Pub dataframe with id and doi
    Pubs = Table("publication", db.meta, autoload=True, autoload_with=db.engine)
    Pubs = connection.execute(select([Pubs]))
    Pubs = pd.DataFrame(Pubs, columns=Pubs.keys())
    Pubs = Pubs[["id", "doi"]]
    Pubs.rename(columns={"id": "publication_id"}, inplace=True)

    # Merge all together so I have a dataframe with all ids
    df = pd.merge(df, Projects, on="project_id")
    df = pd.merge(df, Pubs, on="publication_id")

    return df
