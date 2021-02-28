import click
from sparrow.plugins import SparrowPlugin
from sqlalchemy import func
from json import loads
from requests import get

# TODO: add geoalchemy to base docker image
# ..tricky because we are using Alpine
# from geoalchemy2.shape import to_shape

# Could also extend this to support the Mapbox places or Google Places API.


def get_location_name(coords):
    [lng, lat] = coords
    url = f"https://rockd.org/api/v2/nearby?lng={lng}&lat={lat}"
    # Right now this is synchronous, which is slow...
    response = get(url)
    name = response.json()
    # Do some sanitization
    name = name.replace(", , ", ", ")
    return name


class LocationNamesPlugin(SparrowPlugin):
    name = "location-names"

    def on_setup_cli(self, cli):
        @click.command(name="update-location-names")
        @click.option("--overwrite", is_flag=True, default=False)
        def cmd(*args, **kwargs):
            """
            Update location names
            """
            self.update_location_names(*args, **kwargs)

        cmd.plugin = self.name

        cli.add_command(cmd)

    def update_location_names(self, overwrite=False):
        db = self.app.database
        s = db.model.sample
        # Get unnamed locations
        q = (
            db.session.query(s)
            .with_entities(s, func.ST_AsGeoJSON(func.ST_Centroid(s.location)))
            .filter(s.location != None)
        )

        if not overwrite:
            q = q.filter(s.location_name == None)

        for (s, json_string) in q:
            # Get point coordinate
            coord = loads(json_string)["coordinates"]

            name = get_location_name(coord)
            s.location_name = name
            s.location_name_autoset = True
            db.session.add(s)
            db.session.commit()
            print(name)
