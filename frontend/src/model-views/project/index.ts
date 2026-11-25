import { hyperStyled } from "@macrostrat/hyper";
import { useRouteMatch } from "react-router-dom";
import { LinkCard } from "@macrostrat/ui-components";
import { Spinner } from "@blueprintjs/core";
import { useProjectModel } from "~/api/models";
import { ProjectPage } from "./page";
import { useModelURL } from "~/util/router";
import { pluralize } from "../components";
import "../main.styl";
import styles from "~/admin/module.styl";
const h = hyperStyled(styles);

interface Project {
  id: number;
  name: string;
  description: string;
  samples: any[];
  publication: any[];
  publications?: any[];
}

interface ProjectInfoLinkProps extends Project {
  minimal: boolean;
}

const ellipseAppend = (props) => {
  const { data, attribute } = props;
  if (data.length == 0) return null;

  if (data.length > 1) {
    return data[0][attribute] + "....";
  } else {
    return data[0][attribute];
  }
};

function ProjectInfoLink(props: ProjectInfoLinkProps) {
  let {
    id,
    name,
    description,
    samples = [],
    publication = props.publications,
    minimal = false,
  } = props;

  if (!samples) {
    samples = [];
  }
  if (!publication) {
    publication = [];
  }

  const to = useModelURL(`/project/${id}`);
  const pubData = ellipseAppend({ data: publication, attribute: "title" });

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

export const ContentArea = ({ data, title, className, minimal = false }) =>
  h("div.content-area", [
    h("h5", [h("span.count", data.length), " ", pluralize(title, data)]),
    h.if(!minimal)(
      "ul",
      { className },
      data.map((d) => h("li", d))
    ),
  ]);

interface ProjectProps {
  Edit: boolean;
  id?: number;
}

const ProjectComponent = function (props: ProjectProps) {
  const { id, Edit } = props;
  const project = useProjectModel(id);

  if (id == null) return null;
  if (project == null) return h(Spinner);

  return h("div.data-view.project", null, h(ProjectPage, { project, Edit }));
};

function ProjectMatch({ Edit }) {
  const {
    params: { id },
  } = useRouteMatch();
  return h(ProjectComponent, { id, Edit });
}

export { ProjectComponent, ProjectMatch, ProjectInfoLink };
