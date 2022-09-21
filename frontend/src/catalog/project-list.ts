import h from "@macrostrat/hyper";
import { Callout } from "@blueprintjs/core";
import { FilterListComponent } from "~/components/filter-list";
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
    h(FilterListComponent, {
      route: "/project",
      getTotalCount: (response) => {
        console.log(response.headers);
        return parseInt(response.headers["content-range"].split("/")[1]);
      },
      opts: {
        headers: {
          Prefer: "count=exact",
        },
      },
      filterFields: {
        name: "Name",
        description: "Description",
      },
      itemComponent: ProjectInfoLink,
    }),
  ]);
};

export { ProjectListComponent };
