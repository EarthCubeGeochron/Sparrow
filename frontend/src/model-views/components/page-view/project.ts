import { AddCard, ProjectModelCard, ProjectEditCard } from "../index";
import { hyperStyled } from "@macrostrat/hyper";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const ProjectAdd = (props) => {
  const { onClickDelete, onClickList, data, isEditing } = props;

  return h("div", [
    h(PageViewProjects, {
      onClick: onClickDelete,
      isEditing,
      data,
    }),
    h.if(isEditing)(AddCard, {
      model: "project",
      onClick: onClickList,
    }),
  ]);
};

const ProjectLink = function({ d }) {
  const project = d.project.map((obj) => {
    if (obj) {
      const { name: project_name, id: project_id } = obj;
      return { project_name, project_id };
    }
    return null;
  });

  const [test] = project;
  if (test == null) return null;

  return project.map((ele) => {
    if (!ele) return null;
    const { project_name, project_id, description } = ele;
    return h(ProjectModelCard, {
      id: project_id,
      name: project_name,
      description,
      link: true,
    });
  });
};

export const PageViewProjects = ({ data, isEditing, onClick }) => {
  if (isEditing) {
    return h("div.parameter", [
      h("h4.subtitle", "Project"),
      h("p.value", [h(ProjectEditCard, { d: data, onClick })]),
    ]);
  }
  return h("div.parameter", [
    h.if(data.project.length > 0)("h4.subtitle", "Project"),
    h("p.value", [h(ProjectLink, { d: data })]),
  ]);
};
