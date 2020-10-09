import { useState, Component } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Button, Icon } from "@blueprintjs/core";
import styled from "@emotion/styled";
import { ProjectMap } from "./map";
import { EditableProjectDetails } from "./editor";
import { SampleCard, AddSampleCard } from "../sample/detail-card";
import { SampleSelectDialog } from "./sample-select";
import "../main.styl";
import styles from "~/admin/module.styl";

const h = hyperStyled(styles);

class Publication extends Component {
  renderMain() {
    const { doi, title } = this.props;
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
  }

  render() {
    const interior = this.renderMain();
    const { doi } = this.props;
    if (doi == null) {
      return interior;
    }
    const href = `https://dx.doi.org/${doi}`;
    return h("a.publication", { href, target: "_blank" }, interior);
  }
}

const ProjectPublications = function({ data }) {
  if (data == null) {
    data = [];
  }
  return h([
    h.if(data.length)("div.publications", [
      h("h4", "Publications"),
      (data || []).map((d, i) => h(Publication, { key: i, ...d })),
    ]),
    h.if(data == null)("div.publications", "No publications"),
  ]);
};

const ProjectResearchers = function({ data }) {
  let content = [h("p", "No researchers")];
  if (data != null) {
    content = data.map((d) => h("div.researcher", d.name));
  }
  return h("div.researchers", [h("h4", "Researchers"), ...content]);
};

const SampleContainer = styled.div`\
display: flex;
flex-flow: row wrap;
margin: 0 -5px;\
`;

function AddSampleControls() {
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

const ProjectSamples = function({ data }) {
  let content = [h("p", "No samples")];
  if (data != null) {
    content = data.map((d) => h(SampleCard, d));
  }
  return h("div.sample-area", [
    h("h4", "Samples"),
    h(SampleContainer, content),
    h(AddSampleControls),
  ]);
};

const ProjectPage = function(props) {
  const [edit, setEdit] = useState(false);

  const { project } = props;
  const { samples } = project;

  return h("div.project-page", [
    h("div.flex-row", [
      h("div.basic-info", [
        h(EditableProjectDetails, { project }),
        h(ProjectPublications, { data: project.publications }),
        h(ProjectResearchers, { data: project.researchers }),
      ]),
      h("div", [h("h4", "Location"), h(ProjectMap, { samples })]),
    ]),
    h(ProjectSamples, { data: project.samples }),
  ]);
};

export { ProjectPage };
