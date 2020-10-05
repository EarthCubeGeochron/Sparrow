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
  const url = "http://localhost:5002/api/v2/models/project";

  const initData = useAPIResult("/project", {
    all: 1,
  });

  useEffect(() => {
    if (initData) {
      setData(initData);
    }
  }, [initData]);

  const fetchNewData = () => {
    const newData = getNextPageAPI(data, url, { per_page: 15 }); // next page of api data
    const newState = newData.data + data;
    setData(newState);
  };
  
  /* List of projects for the catalog. Could potentially move there... */
  return data.length > 0
    ? h(InfiniteScroll, {
        initialData: data,
        component: ProjectInfoLink,
        fetch: fetchNewData,
      })
    : h("div", { style: { marginTop: "100px" } }, [h(Spinner)]);
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

function getNextPageAPI(initData, url, params) {
  const nextPageUrl = initData.next_page;
  const newData = useAPIResult(url, { params, page: nextPageUrl });
  return newData;
}
