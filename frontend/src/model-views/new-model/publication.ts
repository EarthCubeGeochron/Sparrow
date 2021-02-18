import { hyperStyled } from "@macrostrat/hyper";
import { useReducer, useState, useContext } from "react";
import { useAPIResult } from "@macrostrat/ui-components";
import {
  Button,
  Tooltip,
  InputGroup,
  Divider,
  PanelStack,
  IPanelProps,
} from "@blueprintjs/core";
import { Publication } from "../project/page";
import { ModelEditableText } from "../project/editor";
import { FormSlider, isTitle } from "./utils";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function PublicationXDDInput(props) {
  const [search, setSearch] = useState("");
  const [pubs, setPubs] = useState([]);
  const [total, setTotal] = useState(0);
  //const [doi, setDoi] = useState("");
  const { context, type, payload_name } = props;
  console.log(total);

  const { dispatch } = useContext(context);

  //xdd route for
  const doiRoute = "https://xdd.wisc.edu/api/articles";
  const response = isTitle(search)
    ? useAPIResult(doiRoute, { title_like: search, max: 50 })
    : useAPIResult(doiRoute, { doi: search, max: 20 });

  //crossref
  const crossrefRoute = "https://api.crossref.org/works";

  const crossrefRes = isTitle(search)
    ? useAPIResult(crossrefRoute, {
        query: search,
        select: "DOI,title",
        rows: 5,
      })
    : search.length > 6
    ? useAPIResult(crossrefRoute, {
        filter: `doi:${search}`,
        select: "DOI,title",
        rows: 5,
      })
    : useAPIResult(crossrefRoute, {
        query: search,
        select: "DOI,title",
        rows: 5,
      });

  const onSearch = () => {
    // first check the xDD route
    if (response != null) {
      const { data } = response.success;
      if (data) {
        const unData = data.map((ele) => unwrapPubData(ele));
        if (unData.length > 0) {
          setPubs(unData.slice(0, 4)); // first 5
          setTotal(unData.length); // can be at max 20
        }
        //Move onto crossref
      } else if (crossrefRes != null) {
        console.log(crossrefRes);
        const { items, "total-results": total } = crossrefRes.message;
        const nItems = items.map((ele) => {
          const { DOI: doi, title } = ele;
          return { doi, title };
        });
        setPubs(nItems);
        setTotal(total);
      }
    } else {
    }
  };

  const message =
    total <= 5
      ? "Only 5 or less results!"
      : total > 5 && total <= 10
      ? "More results than are shown, try to narrow your search"
      : "Ouufff, looks like you have a lot of results. Try to narrow your search";

  const intent =
    total <= 5 ? "success" : total > 5 && total <= 10 ? "warning" : "danger";

  const leftElement =
    pubs.length > 0
      ? h(Tooltip, { content: message, intent }, [
          h(Button, { intent }, [total]),
        ])
      : null;

  const rightElement = h(Button, {
    icon: "search",
    onClick: onSearch,
    minimal: true,
  });

  const unwrapPubData = (data) => {
    const title = data.title;
    const { identifier } = data;
    if (identifier) {
      const doi = identifier.map((ele) => {
        if (ele.type == "doi") {
          return ele.id;
        }
      });
      return { doi: doi[0], title };
    }
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
    return h(Button, {
      onClick: () => addToModel(i),
      intent: "success",
      minimal: true,
      disabled,
      icon: "plus",
    });
  };
  const disabled = pubs.length == 0 ? true : false;

  return h("div", [
    h(InputGroup, {
      leftElement,
      rightElement,
      onChange: (e) => {
        setSearch(e.target.value);
      },
    }),
    h("div", [
      pubs.length > 0
        ? pubs.map((pub, i) => {
            const { doi, title } = pub;
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

/**
 * 
 * function Menubar(props: MenubarProps) {
  const [panels, setPanels] = useState<(IPanel<MenubarProps>| IPanel)[]>([ // it works
    {
      component: Settings,
      props,
      title: "Settings",
    },
  ]);

  return (
    <PanelStack
      className="Menubar"
      initialPanel={panels[0]}
      onOpen={(new_) => setPanels([new_, ...panels])}
      onClose={() => setPanels(panels.slice(1))}
    />
  );
}
 */
function Stack({ context }) {
  const [panels, setPanels] = useState<IPanelProps[]>([
    { component: h(PublicationXDDInput, { context }), title: "Test" },
  ]);
  return h(PanelStack, {
    initialPanel: panels[0],
    onOpen: (new_) => setPanels([new_, ...panels]),
    onClose: () => setPanels(panels.slice(1)),
  });
}

function DrawerContent(props) {
  const { context } = props;

  const topHeader = "Search for Publication by DOI";
  return h("div.drawer-body", [
    h("div.top-header", [
      h("h3", [topHeader]),
      h("h5", [
        "Powered by ",
        h("a", { href: "https://xdd.wisc.edu/" }, "xDD"),
        " and the ",
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
