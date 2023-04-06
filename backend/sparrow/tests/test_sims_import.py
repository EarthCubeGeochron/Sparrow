from sparrow.core.util import relative_path
import gzip
import json
from pytest import mark
from bs4 import BeautifulSoup as soup
from pathlib import Path


class TestSIMSImport:
    @mark.slow
    def test_large_sims_dataset(self, db):
        fn = relative_path(__file__, "fixtures", "2_20140602_d18O_KennyBefus.json.gz")
        with gzip.open(fn, "rb") as zipfile:
            data = json.loads(zipfile.read())
        db.load_data("session", data)


class TestSIMSWebscraper:
    def test_webscrape_app_sims(self, db, client, token):
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

        page = relative_path(__file__, "fixtures/wiscsims_publications.html")
        with open(page, "r") as f:
            page_html = f.read()

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
            proj_titles.append(
                {"name": title, "publication": [{"title": title, "doi": doi_list[i]}]}
            )

        res = client.post(route, headers={"Authorization": token}, json=proj_titles)

        up_json = res.json()
        assert len(up_json["data"]) > 0
