from sparrow.core.util import relative_path
from json import load


def ensure_single(db, model_name, **filter_params):
    model = getattr(db.model, model_name)
    n = db.session.query(model).filter_by(**filter_params).count()
    assert n == 1


def load_relative(*pth):
    fn = relative_path(*pth)
    with open(fn) as fp:
        return load(fp)


def json_fixture(*pth):
    return load_relative(__file__, "..", "fixtures", *pth)
