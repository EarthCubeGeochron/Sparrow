import { Button } from "@blueprintjs/core";
import { AddCard, ProjectModelCard, ProjectEditCard } from "../index";
import { Tooltip } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useModelURL } from "~/util";
//@ts-ignore
import styles from "./module.styl";
import { useAPIv2Result } from "~/api-v2";

const h = hyperStyled(styles);

export const ProjectAdd = props => {
  const { onClickDelete, onClickList, data, isEditing } = props;

  return h("div", [
    h(PageViewProjects, {
      onClick: onClickDelete,
      isEditing,
      data
    }),
    h.if(isEditing)(AddCard, {
      model: "project",
      onClick: onClickList
    })
  ]);
};

const ProjectLink = ({ d }) => {
  const project = d.project.map(obj => {
    if (obj) {
      return obj;
    }
    return null;
  });

  const [test] = project;
  if (test == null) return null;

  return h("div", { style: { display: "flex", flexDirection: "column" } }, [
    project.map(ele => {
      if (!ele) return null;
      return h(ProjectLinks, {
        project: ele
      });
    })
  ]);
};

export const ProjectLinks = props => {
  const { project } = props;
  console.log(project);

  const projectTo = useModelURL(`/project/${project.id}`);

  return h(
    Tooltip,
    {
      content: h("div", { style: { maxWidth: "400px" } }, [
        h(ProjectModelCard, project)
      ]),
      position: "top"
    },
    [
      h("div.project", [
        h("div", [h("a", { href: projectTo }, project.name) || "—"])
      ])
    ]
  );
};

export const PageViewProjects = ({ data, isEditing, onClick }) => {
  if (isEditing) {
    return h("div.parameter", [
      h("h4.subtitle", "Project"),
      h("p.value", [h(ProjectEditCard, { d: data, onClick })])
    ]);
  }
  return h("div.parameter", [
    h.if(data.project.length > 0)("h4.subtitle", "Project"),
    h("p.value", [h(ProjectLink, { d: data })])
  ]);
};

export function NewProjectPageButton() {
  const to = useModelURL("/project/new");
  const handleClick = e => {
    e.preventDefault();
    window.location.href = to;
  };

  return h(
    Button,
    { minimal: true, intent: "success", onClick: handleClick, icon: "add" },
    ["Create New Project"]
  );
}
