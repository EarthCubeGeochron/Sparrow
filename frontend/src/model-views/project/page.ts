import { hyperStyled } from "@macrostrat/hyper";
import { EditableProjectDetails } from "./editor";
import "../main.styl";
import styles from "~/admin/module.styl";

const h = hyperStyled(styles);

const ProjectPage = function(props) {
  const { project, Edit } = props;

  return h("div.project-page", [
    h("div.flex-row", [
      h("div.basic-info", [h(EditableProjectDetails, { project, Edit })]),
    ]),
  ]);
};

export { ProjectPage };
