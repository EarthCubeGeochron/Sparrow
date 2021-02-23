import { useState, useEffect, useContext } from "react";
import { Button } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { ProjectFormContext } from "../project/new-project";
import { ModelEditableText } from "../project/editor";
import { FormSlider } from "./utils";
import styles from "./module.styl";

const h = hyperStyled(styles);

/**
 * Only needs 2 fields:
 *  Name,
 *  Orcid_id
 * Both text
 */
function ResearcherForm(props) {
  const [researcher, setResearcher] = useState({
    name: "",
    orcid_id: "",
  });
  const { dispatch } = useContext(ProjectFormContext);

  const onSubmit = () => {
    dispatch({
      type: "add_researcher",
      payload: { researcher_collection: [researcher] },
    });
  };

  const onChangeName = (value) => {
    setResearcher((prevRes) => {
      return {
        ...prevRes,
        name: value,
      };
    });
  };
  const onChangeOrcid = (value) => {
    setResearcher((prevRes) => {
      return {
        ...prevRes,
        orcid_id: value,
      };
    });
  };

  return h("div.drawer-body", [
    h(ModelEditableText, {
      is: "h3",
      field: "name",
      placeholder: "Name your researcher",
      editOn: true,
      onChange: onChangeName,
      value: researcher.name,
      multiline: true,
    }),
    h(ModelEditableText, {
      is: "h3",
      field: "orcid_id",
      placeholder: "Add an Orcid_id",
      editOn: true,
      onChange: onChangeOrcid,
      value: researcher.orcid_id,
      multiline: true,
    }),
    h(Button, { onClick: onSubmit, intent: "success" }, [
      "Create new researcher",
    ]),
  ]);
}

export function AddResearcherDrawer(props) {
  return h(FormSlider, {
    content: h(ResearcherForm),
    model: "researcher",
  });
}
