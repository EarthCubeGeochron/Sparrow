import { Component } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Callout } from "@blueprintjs/core";
import styled from "@emotion/styled";
import T from "prop-types";
import { FilterListComponent } from "../../components/filter-list";
import { LinkCard, APIResultView } from "@macrostrat/ui-components";
import { ProjectMap } from "./map";
import { EditableProjectDetails } from "./editor";

import classNames from "classnames";
import { SampleCard } from "../sample/detail-card";
import "../main.styl";
import styles from "../module.styl";
const h = hyperStyled(styles);

const pluralize = function (term, arrayOrNumber) {
  let count = arrayOrNumber;
  if (Array.isArray(arrayOrNumber)) {
    count = arrayOrNumber.length;
  }
  if (count > 1) {
    term += "s";
  }
  return term;
};

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

const ProjectPublications = function ({ data }) {
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

const ProjectResearchers = function ({ data }) {
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

const ProjectSamples = function ({ data }) {
  let content = [h("p", "No samples")];
  if (data != null) {
    content = data.map((d) => h(SampleCard, d));
  }
  return h("div.sample-area", [
    h("h4", "Samples"),
    h(SampleContainer, content),
  ]);
};

const ContentArea = ({ data, title, className }) =>
  h("div.content-area", [
    h("h5", [h("span.count", data.length), " ", pluralize(title, data)]),
    h(
      "ul",
      { className },
      data.map((d) => h("li", d))
    ),
  ]);

const ProjectInfoLink = function (props) {
  let { id, name, description, samples, publications } = props;
  if (publications == null) {
    publications = [];
  }
  return h(
    LinkCard,
    {
      to: `/catalog/project/${id}`,
      key: id,
      className: "project-card",
    },
    [
      h("h3", name),
      h("p.description", description),
      h.if(samples.length)(ContentArea, {
        className: "samples",
        data: samples.map((d) => d.name),
        title: "sample",
      }),
      h.if(publications.length)(ContentArea, {
        className: "publications",
        data: publications.map((d) => d.title),
        title: "publication",
      }),
    ]
  );
};

const ProjectListComponent = () =>
  h("div.data-view.projects", [
    h(
      Callout,
      {
        icon: "info-sign",
        title: "Projects",
      },
      `This page lists projects of related samples, measurements, and publications. \
Projects can be imported into Sparrow or defined using the managment interface.`
    ),
    h(FilterListComponent, {
      route: "/project",
      filterFields: {
        name: "Name",
        description: "Description",
      },
      itemComponent: ProjectInfoLink,
    }),
  ]);

const ProjectPage = function (props) {
  const { project } = props;
  const { samples } = project;
  return h("div.project-page", [
    h(EditableProjectDetails, { project }),
    h(ProjectPublications, { data: project.publications }),
    h(ProjectResearchers, { data: project.researchers }),
    h("div.flex-row", [
      h(ProjectSamples, { data: project.samples }),
      h("div", [h("h4", "Location"), h(ProjectMap, { samples })]),
    ]),
  ]);
};

const ProjectComponent = function (props) {
  const { id } = props;
  if (id == null) {
    return null;
  }
  return h("div.data-view.project", [
    h(
      APIResultView,
      {
        route: "/project",
        params: { id },
      },
      (data) => {
        const project = data[0];
        return h(ProjectPage, { project });
      }
    ),
  ]);
};

ProjectComponent.propTypes = {
  id: T.number,
};

export { ProjectListComponent, ProjectComponent };
