import h from "@macrostrat/hyper";
import { FilterListComponent } from "~/components/filter-list";
import { ProjectInfoLink } from "~/model-views/project";

const ProjectListComponent = () => {
  /* List of projects for the catalog. Could potentially move there... */
  return h("div.data-view.projects", [
    h(FilterListComponent, {
      route: "/project",
      filterFields: {
        name: "Name",
        description: "Description",
      },
      itemComponent: ProjectInfoLink,
    }),
  ]);
};

export { ProjectListComponent };
