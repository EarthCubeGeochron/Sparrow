import collections
from ..interface.converter import allowed_collections


def nested_collection_path(start, end, allowed_collections=allowed_collections):
    """
    Function to return the path of nesting needed to get from one model to another. 

    start (string) : Starting model
    end (string) : Ending model

    Dependencies: allowed_collections, and collections library from python.
    """

    dist = {start: [start]}
    q = collections.deque([start])
    while len(q):
        current = q.popleft()
        if current not in allowed_collections:
            pass
        else:
            for node in allowed_collections[current]:
                if node not in dist:
                    dist[node] = dist[current] + [node]
                    q.append(node)

    shortest_path = dist.get(end)
    return shortest_path


def nested_collection_joins(path, query, db, model):
    """
    Function to create a query join through a loop depending on the path passed.


    path ([string]): path of allowed collections
    query: db query to join and filter off of
    db: database to be used to call models off of
    model: current model, generally will be self.model

    ex)
    ['sample', 'session', 'analysis', 'datum']

    needs to become:

      query.join(self.model.session_collection).join(session.analysis_collection).join(analysis.datum_collection)

    """

    model_col = []  # ['session_collection'....]
    for i, ele in enumerate(path):
        if i + 1 < len(path):
            # determines whether it will be a collection join or normal table
            ##   This checks if the current model has the next element has a collection attribute
            if hasattr(getattr(db.model, ele), path[i + 1] + "_collection"):
                model_col.append(path[i + 1] + "_collection")
            else:
                model_col.append(path[i + 1])

    list1 = []
    for i, val in enumerate(path):
        if i + 1 < len(path):
            # implements a collection join or normal table join
            if "collection" not in model_col[i]:
                list1.append(getattr(db.model, model_col[i]))  ## just join the table
            else:
                list1.append(getattr(getattr(db.model, path[i]), model_col[i]))

    db_query = getattr(query, "join")(*list1)

    return db_query


def text_fields(model):
    """
    Function to return the column model attributes for a sqlalchemy model whose type is text
    i.e sample.name
    """
    fields = model.__table__.columns.keys()
    text_fields = []
    for c in fields:
        if f"{getattr(model,c).type}" == "TEXT":
            text_fields.append(c)

    atr = []
    for c in text_fields:
        atr.append(getattr(model, c))

    return atr
