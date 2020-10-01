import { hyperStyled } from "@macrostrat/hyper";
import { useRouteMatch } from "react-router-dom";
import { LinkCard, useAPIResult } from "@macrostrat/ui-components";
import { ProjectPage } from "./page";
import { useModelURL } from "~/util/router";
import "../main.styl";
import styles from "~/admin/module.styl";
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

const ContentArea = ({ data, title, className, minimal = false }) =>
  h("div.content-area", [
    h("h5", [h("span.count", data.length), " ", pluralize(title, data)]),
    h.if(!minimal)(
      "ul",
      { className },
      data.map((d) => h("li", d))
    ),
  ]);

interface Project {
  id: number;
  name: string;
  description: string;
  samples: any[];
  publications: any[];
}

interface ProjectInfoLinkProps extends Project {
  minimal: boolean;
}

function ProjectInfoLink(props: ProjectInfoLinkProps) {
  let {
    id,
    name,
    description,
    samples = [],
    publications = [],
    minimal = false,
  } = props;

  const to = useModelURL(`/project/${id}`);

  return h(
    LinkCard,
    {
      to,
      key: id,
      className: "project-card",
    },
    [
      h("h3", name),
      h("p.description", description),
      h.if(samples.length > 0)(ContentArea, {
        className: "samples",
        data: samples.map((d) => d.name),
        title: "sample",
      }),
      h.if(publications.length > 0)(ContentArea, {
        className: "publications",
        data: publications.map((d) => d.title),
        title: "publication",
      }),
    ]
  );
}

interface ProjectProps {
  id?: number;
}

const ProjectComponent = function (props: ProjectProps) {
  const { id } = props;
  const data = useAPIResult("/project", { id });
  if (id == null || data == null) {
    return null;
  }

  const project = data[0];
  return h("div.data-view.project", null, h(ProjectPage, { project }));
};

function ProjectMatch() {
  const {
    params: { id },
  } = useRouteMatch();
  return h(ProjectComponent, { id });
}

export { ProjectComponent, ProjectMatch, ProjectInfoLink };
