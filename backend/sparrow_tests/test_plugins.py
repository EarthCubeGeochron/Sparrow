def test_core_plugins_loaded(app):
    assert app.plugins.get("versioning") is not None
