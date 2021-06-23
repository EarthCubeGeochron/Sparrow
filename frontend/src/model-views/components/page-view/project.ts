import { Button } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useModelURL } from "~/util";
import { PageViewModelCard, PageViewBlock } from "~/model-views";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const ProjectAdd = props => {
  const { onClickDelete, onClickList, data, isEditing } = props;

  return h(
    PageViewBlock,
    {
      model: "project",
      onClick: onClickList,
      isEditing,
      title: "Projects",
      modelLink: true,
      hasData: data.project.length != 0
    },
    [
      h(PageViewProjects, {
        onClick: onClickDelete,
        isEditing,
        data
      })
    ]
  );
};

export const PageViewProjects = ({ data, isEditing, onClick }) => {
  return h("div", [h(ProjectCard, { d: data, onClick, isEditing })]);
};

const ProjectCard = props => {
  const { d, onClick, isEditing } = props;
  const project = d.project.map(obj => {
    if (obj) {
      const { name, id } = obj;
      return { name, id };
    }
    return null;
  });

  return h("div", [
    project.map(obj => {
      if (!obj) return null;
      const { name, id } = obj;
      const to = useModelURL(`/project/${id}`);

      return h(
        PageViewModelCard,
        {
          isEditing,
          styles: { minWidth: "500px" },
          to,
          link: true,
          onClick: () => onClick({ id, name })
        },
        [h("h4.name", name)]
      );
    })
  ]);
};
