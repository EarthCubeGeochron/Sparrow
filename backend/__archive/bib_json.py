from crossref.restful import Works
import json


def create_BibJSON(crossref_object, doi):
    """
    Function that returns a BibJSON Object
    Takes in a crossref object: i.e, pass the returned object from the crossref api
    """
    try:
        [title] = crossref_object["title"]
        if "type" in crossref_object:
            type_ = crossref_object["type"]
        else:
            type_ = ""
        year = crossref_object["created"]["date-time"].split("-")[0]
        journal = ""
        if len(crossref_object["short-container-title"]) == 0:
            pass
        else:
            [title] = crossref_object["short-container-title"]
            journal += title
        url = crossref_object["URL"]
        ## I realize this line comprehension is stupid long
        author = [
            {"name": n}
            for n in [
                " ".join(n)
                for n in [(n["given"], n["family"]) for n in crossref_object["author"]]
            ]
        ]

        BibJSON = {
            "title": title,
            "author": author,
            "type": type_,
            "year": year,
            "journal": journal,
            "link": url,
            "identifier": {"type": "doi", "id": doi},
        }
        return BibJSON
    except:
        return {"identifier": {"type": "doi", "id": doi}}


def doi_BibJSON_pipeline(dois):
    """
    Creates a list of BibJSON objects from a list of DOIs passed
    """
    works = Works()
    BibJSON_list = []
    for doi in dois:
        crossref_obj = works.doi(doi)
        BibJSON_list.append(json.dumps(create_BibJSON(crossref_obj, doi)))

    return BibJSON_list
