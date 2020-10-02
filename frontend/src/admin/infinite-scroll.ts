import h from "@macrostrat/hyper";
import { FilterListComponent } from "~/components/filter-list";
import { ProjectInfoLink } from "~/model-views/project";
import InfiniteScroll from "~/components/infinite-scroll";
//import { ForeverScroll } from "~/components/infinite-scroll;";
//import { InfiniteScrollView } from "@macrostrat/ui-components";
import { useAPIResult } from "@macrostrat/ui-components";
import { useState, useEffect } from "react";
import { Spinner } from "@blueprintjs/core";

const ProjectListComponent = () => {
  const [data, setData] = useState([]);

  const initData = useAPIResult("/project", { all: 1 });

  useEffect(() => {
    if (initData) {
      const data = initData.filter((d) => d.samples !== null);
      console.log(data);
      setData(data);
    }
  }, [initData]);
  /* List of projects for the catalog. Could potentially move there... */
  return data.length > 0
    ? h(InfiniteScroll, { initialData: data })
    : h(Spinner);
  // return h(FilterListComponent, {
  //   route: "/project",
  //   filterFields: {
  //     name: "Name",
  //     description: "Description",
  //   },
  //   itemComponent: ProjectInfoLink,
  // });
  //return h("div");
  // return h(
  //   InfiniteScrollView,
  //   {
  //     route: "/project",
  //     params: { all: true },
  //     getItems(res) {
  //       console.log(res);
  //       return res;
  //     },
  //   },
  //   ({ data }) => {
  //     if (data == null) return null;
  //     return h(
  //       "div.results",
  //       data.map((d) => h(ProjectInfoLink, d))
  //     );
  //   }
  // );
};

export { ProjectListComponent };
