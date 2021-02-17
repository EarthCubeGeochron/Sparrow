import { hyperStyled } from "@macrostrat/hyper";
import { useReducer, useState, useContext } from "react";
import { useAPIResult } from "@macrostrat/ui-components";
import { Button, Popover, InputGroup, Divider } from "@blueprintjs/core";
import { Publication } from "../project/page";
import { ModelEditableText } from "../project/editor";
import { FormSlider } from "./utils";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function PublicationXDDInput(props) {
  const [search, setSearch] = useState("");
  const [pubs, setPubs] = useState([]);
  const [total, setTotal] = useState(0);
  //const [doi, setDoi] = useState("");

  console.log(pubs, total);

  const { context, type, payload_name } = props;

  const { dispatch } = useContext(context);

  //xdd route for
  //const doiRoute = "https://xdd.wisc.edu/api/articles";

  //crossref
  const crossrefRoute = "https://api.crossref.org/works";

  //const response = useAPIResult(doiRoute, { doi: search, max: 1 });
  const crossrefRes = useAPIResult(crossrefRoute, {
    query: search,
    select: "DOI,title",
    rows: 5,
  });

  const onSearch = () => {
    if (crossrefRes != null) {
      const { items, total } = crossrefRes.message;
      setPubs(items);
      setTotal(total);
    }
  };

  const rightElement = h(Button, {
    icon: "search",
    onClick: onSearch,
    minimal: true,
  });

  const unwrapPubData = (data) => {
    const title = data.title;
    const doi = data.identifier.map((ele) => {
      if (ele.type == "doi") {
        return ele.id;
      }
    });
    return { doi: doi[0], title };
  };

  const addToModel = (i) => {
    const { doi, title } = pubs[i];
    const data = new Array({ doi, title });
    console.log(data);
    dispatch({
      type: "add_pub",
      payload: {
        publication_collection: [{ title, doi }],
      },
    });
  };

  const SubmitButton = (props) => {
    const { disabled = false, i } = props;
    return h(
      Button,
      { onClick: () => addToModel(i), intent: "success", disabled },
      ["Add to Project"]
    );
  };
  const disabled = pubs.length == 0 ? true : false;

  return h("div", [
    h(InputGroup, {
      rightElement,
      onChange: (e) => {
        setSearch(e.target.value);
      },
    }),
    h("div", [
      pubs.length > 0
        ? pubs.map((pub, i) => {
            const { DOI: doi, title } = pub;
            return h("div.pub-edit-card", { key: doi }, [
              h(Publication, { doi, title }),
              h(SubmitButton, { disabled, i }),
            ]);
          })
        : null,
    ]),
  ]);
}

export function PublicationInputs(props) {
  const [pub, setPub] = useState({ doi: "", title: "" });
  const { context } = props;

  const { dispatch } = useContext(context);

  const addToModel = () => {
    const data = new Array(pub);
    dispatch({ type: "add_pub", payload: { publication_collection: data } });
  };

  const SubmitButton = ({ disabled }) => {
    return h(Button, { onClick: addToModel, intent: "success", disabled }, [
      "Add to Project",
    ]);
  };

  const changeDoi = (e) => {
    setPub((prevPub) => {
      return { ...pub, doi: e };
    });
  };
  const changeTitle = (e) => {
    setPub((prevPub) => {
      return { ...pub, title: e };
    });
  };
  const disabled = pub.doi.length == 0 || pub.title.length == 0 ? true : false;

  return h("div", [
    h(ModelEditableText, {
      is: "h3",
      field: "title",
      placeholder: "Publication Title",
      id: "name-text",
      editOn: true,
      onChange: changeTitle,
      value: pub.title,
      multiline: true,
    }),
    h(ModelEditableText, {
      is: "h3",
      field: "doi",
      placeholder: "Publication DOI",
      id: "name-text",
      editOn: true,
      onChange: changeDoi,
      value: pub.doi,
      multiline: true,
    }),
    h(SubmitButton, { disabled }),
  ]);
}

function DrawerContent(props) {
  const { context } = props;

  const topHeader = "Search for Publication by DOI";
  return h("div.drawer-body", [
    h("div.top-header", [
      h("h3", [topHeader]),
      h("h5", [
        "Powered by the ",
        h(
          "a",
          { href: "https://github.com/CrossRef/rest-api-doc" },
          "Crossref API"
        ),
      ]),
    ]),
    h(PublicationXDDInput, { context }),
    h("div.divi", [h(Divider)]),
    h("h3", ["Or enter in a Title and DOI"]),
    h(PublicationInputs, { context }),
  ]);
}

export function AddNewPubToModel(props) {
  const { context, type } = props;

  return h("div", [
    h(FormSlider, {
      content: h(DrawerContent, { context }),
      model: "Publication",
    }),
  ]);
}
