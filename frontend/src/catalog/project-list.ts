import h from "@macrostrat/hyper";
import { Callout } from "@blueprintjs/core";
import {
  FilterListComponent,
  PostgRESTFilterList,
} from "~/components/filter-list";
import { ProjectInfoLink } from "~/model-views/project";

// class PostgRESTPagedModelView extends FilterListComponent {
//   params(...args) {
//     let params = super.params(...args);
//     params = { ...params, offset };
//   }
// }

const ProjectListComponent = () => {
  /* List of projects for the catalog. Could potentially move there... */
  return h("div.data-view.projects", [
    h(
      Callout,
      {
        icon: "info-sign",
        title: "Projects",
      },
      `This page lists projects of related samples, measurements, and publications. \
Projects can be imported into Sparrow or defined using the managment interface.`
    ),
    h(PostgRESTFilterList, {
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
