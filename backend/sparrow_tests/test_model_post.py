from bs4 import BeautifulSoup as soup
from crossref.restful import Works
from urllib.request import urlopen as uReq

from .helpers import json_fixture
import json
import sys
from datetime import datetime


def create_BibJSON(crossref_object,doi):
    '''
        Function that returns a BibJSON Object
        Takes in a crossref object: i.e, pass the returned object from the crossref api
    '''
    try:
        [title]= crossref_object['title']
        if 'type' in crossref_object:
            type_ = crossref_object['type']
        else:
            type_ = ""
        year = crossref_object['created']['date-time'].split("-")[0]
        journal = "" 
        if len(crossref_object['short-container-title']) == 0:
            pass
        else:
            [title] = crossref_object['short-container-title']
            journal += title
        url = crossref_object['URL']
        ## I realize this line comprehension is stupid long
        author = [{'name': n} for n in [" ".join(n) for n in [(n['given'], n['family']) for n in crossref_object['author']]]]   
        
        BibJSON = {
            "title": title,
            "author" : author,
            "type" : type_,
            "year": year,
            "journal" : journal,
            "link" : url,
            "identifier": {"type":"doi", "id": doi}
        }
        return BibJSON
    except:
        return {"identifier": {"type":"doi", "id": doi}}

    
def doi_BibJSON_pipeline(dois):
    '''
        Creates a list of BibJSON objects from a list of DOIs passed
    '''
    works = Works()
    BibJSON_list = []
    for doi in dois:
        crossref_obj = works.doi(doi)
        BibJSON_list.append(json.dumps(create_BibJSON(crossref_obj, doi)))

    return BibJSON_list


class TestModelPost:
    '''
        Testing Suite to test the universal POST method on the api
    '''
    
    def test_import_project(self, db, client):
        '''
            Test Importing some projects        
        '''

        data = json_fixture("projects-post.json")
        route = "/api/v2/models/project"

        res = client.post(route, json=data)

        res_json = res.json()

        assert len(res_json['data']) > 0

    
    def test_add_project_from_existing(self, db, client):
        route = "/api/v2/models/project"

        new_project = json_fixture("new-project.json")

        res = client.post(route, json=new_project)

        data = res.json()

        assert 0 == 1

    def test_edit_researcher_in_project(self,db,client):
        route = "/api/v2/models/project/1" ## editing the first researcher

        edits = {"researchers": [{"name": "casey"}]}
        res_put = client.put(route, json = edits)
        assert res_put.status_code == 200

    
    def test_verylarge_import(self, client):

        import_size = 1e7
        i = 0
        analysis = []
        size = sys.getsizeof(analysis)
        for i in range(0,2):
            item = {
                            "analysis_type": "Stable isotope analysis",
                            "session_index": i,
                            "datum": [
                                {
                                    "value": 0.2,
                                    "error": 0.035,
                                    "type": {"parameter": "delta 13C", "unit": "permille"},
                                }
                            ],
                        }
            analysis.append(item)
        
        data = {
                    "date": str(datetime.now()),
                    "name": "Session with existing instances",
                    "sample": {"name": "LargeImport"},
                    "analysis": analysis
        }
        res = client.put("/api/v1/import-data/session", json=json.dumps(data))

        assert 0 == 1
        assert res.status_code == 201


    def test_webscrape_app_sims(self,db, client):
        '''
            Test for the webscaper! 
        '''
        route = "/api/v2/models/project"

        sims_pub_url = "http://www.geology.wisc.edu/~wiscsims/publications.html"

        page = uReq(sims_pub_url)
        page_html = page.read()
        page.close()

        page_soup = soup(page_html, "html.parser")

        content = page_soup.findAll('p', {'class' : 'item article'})
        title_list = []
        doi_list = []
        for pub in content:
            title = pub.findAll('span', {"class": "body"})[0].text
            title_list.append(title)

            doi = pub.findAll('span', {"class": "doi"})[0].text
            doi_list.append(doi)

        proj_titles = []
        for i, title in enumerate(title_list):
            proj_titles.append({"name":title, "publications" :[{"title":title, "doi": doi_list[i]}]})


        res = client.post(route, json= proj_titles)

        up_json = res.json()
        assert len(up_json['data']) > 0
        assert 0 ==1


    

    # def test_webscrape_publications_sims(self,db,client):
    #     '''
    #         Test for the webscraper to publications pipeline.

    #         Gather DOI's and then create bibJSON.
    #     '''
    #     route = "/api/v2/models/publication"

    #     sims_pub_url = "http://www.geology.wisc.edu/~wiscsims/publications.html"

    #     page = uReq(sims_pub_url)
    #     page_html = page.read()
    #     page.close()

    #     page_soup = soup(page_html, "html.parser")

    #     content = page_soup.findAll('p', {'class' : 'item article'})


    #     doi_list = []
    #     for pub in content:
    #         doi = pub.findAll('span', {'class':'doi'})[0].text
    #         doi_list.append(doi)

    #     BibJSON_list = doi_BibJSON_pipeline(doi_list[:10])

    #     for_post = []
    #     for bib in BibJSON_list:
    #         try:
    #             for_post.append({"doi": json.loads(bib)['identifier']['id'], "data": bib})
    #         except:
    #             for_post.append({'doi': json.loads(bib)['identifier']['id']})

    #     res = client.post(route, json=for_post)

