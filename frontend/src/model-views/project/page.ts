import { useState, Component } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import styled from "@emotion/styled";
import { ProjectMap } from "./map";
import { EditableProjectDetails, EditNavBar } from "./editor";
import {
  SampleCard,
  AddSampleCard,
  SampleEditCard,
  PubEditCard,
  ResearcherEditCard,
} from "../sample/detail-card";
import { SampleSelectDialog } from "./sample-select";
import "../main.styl";
import styles from "~/admin/module.styl";

const h = hyperStyled(styles);

export function Publication(props) {
  const { doi, title } = props;

  const interior = () => {
    let doiAddendum = [];
    if (doi != null) {
      doiAddendum = [
        " – ",
        h("span.doi-info", [
          h("span.label", "DOI:"),
          h("span.doi.bp3-monospace-text", doi),
        ]),
      ];
    }
    return h("div.publication", [h("span.title", title), ...doiAddendum]);
  };

  if (doi == null) {
    return h(interior);
  } else {
    const href = `https://dx.doi.org/${doi}`;
    return h("a.publication", { href, target: "_blank" }, h(interior));
  }
}

export const ProjectPublications = function({
  data,
  isEditing = false,
  onClick,
  rightElement,
}) {
  if (data == null) {
    data = [];
  }
  if (isEditing) {
    return h("div.publications", [
      h("div", { style: { display: "flex", alignItems: "baseline" } }, [
        h("h4", "Publications"),
        rightElement,
      ]),
      data.length > 0
        ? data.map((pub) => {
            const { id, title, doi } = pub;
            return h(PubEditCard, {
              id,
              content: h(Publication, { doi, title }),
              onClick,
            });
          })
        : null,
    ]);
  }
  return h([
    h.if(data.length)("div.publications", [
      h("h4", "Publications"),
      (data || []).map((d, i) =>
        h(Publication, { key: i, doi: d.doi, title: d.title })
      ),
    ]),
    h.if(data == null)("div.publications", "No publications"),
  ]);
};

export const ProjectResearchers = function({
  data,
  isEditing,
  onClick,
  rightElement,
}) {
  let content = [h("p", "No researchers")];
  if (data != null) {
    content = data.map((d) => h("div.researcher", d.name));
  }
  if (isEditing) {
    return h("div.researchers", [
      h("h4", { style: { display: "flex", alignItems: "baseline" } }, [
        "Researchers",
        rightElement,
      ]),
      data.length > 0
        ? data.map((res) => {
            const { id, name } = res;
            return h(ResearcherEditCard, { id, name, onClick });
          })
        : null,
    ]);
  } else {
    return h("div.researchers", [h("h4", "Researchers"), ...content]);
  }
};

const SampleContainer = styled.div`\
display: flex;
flex-flow: row wrap;
margin: 0 -5px;\
`;

export function AddSampleControls() {
  const [isOpen, setIsOpen] = useState(false);

  const onClick = () => {
    setIsOpen(!isOpen);
  };
  return h([
    h(SampleSelectDialog, {
      isOpen,
      onClose() {
        setIsOpen(false);
      },
    }),
    h(AddSampleCard, { onClick, icon_name: "plus" }),
  ]);
}

export const ProjectSamples = function({
  data,
  isEditing,
  setID = () => {},
  link = true,
  onClick,
  rightElement,
}) {
  let content = [h("p", "No samples")];
  if (data != null) {
    if (!isEditing) {
      return h("div.sample-area", [
        h("h4", "Samples"),
        h(SampleContainer, [
          data.map((d) => {
            const { material, id, name, location_name } = d;
            return h(SampleCard, {
              material,
              id,
              name,
              location_name,
              setID,
              link,
            });
          }),
        ]),
      ]);
    } else {
      return h("div.sample-area", [
        h("div", { style: { display: "flex", alignItems: "baseline" } }, [
          h("h4", "Samples"),
          rightElement,
        ]),
        h(SampleContainer, [
          data.map((d) => {
            const { id, name } = d;
            return h(SampleEditCard, {
              id,
              name,
              onClick,
            });
          }),
        ]),
      ]);
    }
  } else {
    return h("h4", "No Samples");
  }
};

function SampleMapComponent(props) {
  const { samples, project } = props;
  const [hoverID, setHoverID] = useState();

  return h("div", [
    h("div", { style: { display: "flex", flexDirection: "row" } }, [
      h("div", { style: { paddingRight: "10px" } }, [
        h("h4", "Location"),
        h(ProjectMap, { samples, hoverID }),
      ]),
      h(ProjectSamples, { data: project.samples, setID: setHoverID }),
    ]),
  ]);
}

const ProjectPage = function(props) {
  const [edit, setEdit] = useState(false);

  const { project, Edit } = props;
  const { samples } = project;

  return h("div.project-page", [
    h("div.flex-row", [
      h("div.basic-info", [
        h(EditableProjectDetails, { project, Edit }),
        //h(ProjectPublications, { data: project.publications }),
        //h(ProjectResearchers, { data: project.researchers }),
        //h(SampleMapComponent, { project, samples }),
      ]),
    ]),
  ]);
};

export { ProjectPage };
