import { hyperStyled } from "@macrostrat/hyper";
import { useRouteMatch } from "react-router-dom";
import { LinkCard, useAPIResult } from "@macrostrat/ui-components";
import { ProjectPage } from "./page";
import { useModelURL } from "~/util/router";
import "../main.styl";
import styles from "~/admin/module.styl";
const h = hyperStyled(styles);

const pluralize = function(term, arrayOrNumber) {
  let count = arrayOrNumber;
  if (Array.isArray(arrayOrNumber)) {
    count = arrayOrNumber.length;
  }
  if (count > 1) {
    term += "s";
  }
  return term;
};

interface Project {
  id: number;
  name: string;
  description: string;
  samples: any[];
  publication: any[];
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
    publication = [],
    minimal = false,
  } = props;

  const to = useModelURL(`/project/${id}`);
  const pubData =
    publication.length > 0
      ? publication.length > 1
        ? publication[0].title + "...."
        : publication[0].title
      : null;

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
      samples
        ? h(ContentArea, {
            className: "samples",
            data: samples.map((d) => d.name),
            title: "sample",
          })
        : null,
      h.if(publication.length > 0)("div.content-area", [
        h("h5", [
          h("span.count", [
            publication.length + " " + pluralize("Publication", publication),
          ]),
          h("h5", [pubData]),
        ]),
      ]),
    ]
  );
}

const ContentArea = ({ data, title, className, minimal = false }) =>
  h("div.content-area", [
    h("h5", [h("span.count", data.length), " ", pluralize(title, data)]),
    h.if(!minimal)(
      "ul",
      { className },
      data.map((d) => h("li", d))
    ),
  ]);

interface ProjectProps {
  id?: number;
}

const ProjectComponent = function(props: ProjectProps) {
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
