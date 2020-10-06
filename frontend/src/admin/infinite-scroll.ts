import h from "@macrostrat/hyper";
import { FilterListComponent } from "~/components/filter-list";
import { ProjectInfoLink } from "~/model-views/project";
import InfiniteScroll from "~/components/infinite-scroll";
//import { ForeverScroll } from "~/components/infinite-scroll;";
//import { InfiniteScrollView } from "@macrostrat/ui-components";
import { useAPIResult, useAPIActions } from "@macrostrat/ui-components";
import { useState, useEffect } from "react";
import { Spinner } from "@blueprintjs/core";

// function that performs an api call
async function getNextPageAPI(nextPage, url, params) {
  try {
    const response = await fetch(url + "?" + params + "&page=" + nextPage);
    const data = await response.json();
    return data;
  } catch (error) {
    console.log(error);
  }
}

// unwraps the data to be simpatico with the ProjectLink component, also gets the next page
function unWrapProjectCardData(data, setPage) {
  const dataObj = data.data.map((obj) => {
    const { id, name, description, publication, session } = obj;
    const samples = session.map((ob) => ob.sample);
    return { id, name, description, publication, samples };
  });
  setPage(data.next_page);
  return dataObj;
}

const params = "nest=publication,session,sample&per_page=15";

const ProjectListComponent = () => {
  const [data, setData] = useState([]);
  const [nextPage, setNextPage] = useState("");
  const url = "http://localhost:5002/api/v2/models/project";

  console.log(data);

  const initData = useAPIResult(url, {
    nest: "publication,session,sample",
    per_page: 15,
  });

  useEffect(() => {
    if (initData) {
      const dataObj = unWrapProjectCardData(initData, setNextPage);
      setData(dataObj);
    }
  }, [initData]);

  const fetchNewData = () => {
    if (!nextPage) return;
    const newData = getNextPageAPI(nextPage, url, params);
    newData.then((res) => {
      const dataObj = unWrapProjectCardData(res, setNextPage);
      const newState = [...data, ...dataObj];
      setData(newState);
    });
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
