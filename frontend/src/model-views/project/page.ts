import { hyperStyled } from "@macrostrat/hyper";
import styled from "@emotion/styled";
import { EditableProjectDetails } from "./editor";
import {
  SampleCard,
  SampleEditCard,
  PubEditCard,
  ResearcherEditCard,
} from "../sample/detail-card";
import { DndChild } from "~/components";
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
              title,
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

export const ProjectSamples = function({
  data,
  isEditing,
  setID = () => {},
  link = true,
  onClick,
  rightElement,
  draggable = true,
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
            return h(
              DndChild,
              {
                id,
                data: d,
                draggable,
                childern: h(SampleEditCard, {
                  id,
                  name,
                  setID,
                  onClick,
                }),
              },
              [
                h(SampleEditCard, {
                  id,
                  name,
                  setID,
                  onClick,
                }),
              ]
            );
          }),
        ]),
      ]);
    }
  } else {
    if (isEditing) {
      return h("h4", { style: { display: "flex", alignItems: "baseline" } }, [
        "No Samples",
        rightElement,
      ]);
    } else {
      return h("h4", "No Samples");
    }
  }
};

const ProjectPage = function(props) {
  const { project, Edit } = props;

  return h("div.project-page", [
    h("div.flex-row", [
      h("div.basic-info", [h(EditableProjectDetails, { project, Edit })]),
    ]),
  ]);
};

export { ProjectPage };
