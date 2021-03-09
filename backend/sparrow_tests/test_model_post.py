from bs4 import BeautifulSoup as soup
from sparrow.util import relative_path
from pathlib import Path

from .helpers import json_fixture
import json
import sys
from datetime import datetime


class TestModelPost:
    """
    Testing Suite to test the universal POST method on the api
    """

    def test_import_project(self, db, client):
        """
        Test Importing some projects
        """

        data = json_fixture("projects-post.json")
        route = "/api/v2/models/project"

        res = client.post(route, json=data)

        res_json = res.json()

        #maybe need to do something here?

        assert len(res_json["data"]) > 0

    def test_add_project_from_existing(self, db, client):
        route = "/api/v2/models/project"

        new_project = json_fixture("new-project.json")

        res = client.post(route, json=new_project)

        data = res.json()

    def test_edit_researcher_in_project(self, db, client):
        route = "/api/v2/models/project/1"  ## editing the first researcher

        edits = {"researcher": [{"name": "casey", "orcid": None}]}
        res_put = client.put(route, json=edits)

    # assert res_put.status_code == 200

    def test_webscrape_app_sims(self, db, client):
        """
        This test webscrapes an html page, taken from online.

            # sims_pub_url = "http://www.geology.wisc.edu/~wiscsims/publications.html"

        This can also be achieved by accessing the html through a network connection directly.

            # from urllib.request import urlopen as uReqfrom
            #
            # page = uReq(sims_pub_url)
            # page_html = page.read()
            # page.close()

        """
        route = "/api/v2/models/project"

        page = Path(relative_path(__file__, "fixtures/wiscsims_publications.html"))
        page_open = open(page, "r")
        page_html = page_open.read()
        page_open.close()

        page_soup = soup(page_html, "html.parser")

        content = page_soup.findAll("p", {"class": "item article"})
        title_list = []
        doi_list = []
        for pub in content:
            title = pub.findAll("span", {"class": "body"})[0].text
            title_list.append(title)

            doi = pub.findAll("span", {"class": "doi"})[0].text
            doi_list.append(doi)

        proj_titles = []
        for i, title in enumerate(title_list):
            proj_titles.append({"name": title, "publications": [{"title": title, "doi": doi_list[i]}]})

        res = client.post(route, json=proj_titles)

        up_json = res.json()
        assert len(up_json["data"]) > 0
