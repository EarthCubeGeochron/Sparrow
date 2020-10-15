import * as React from "react";
import { useEffect, useState } from "react";
import ForeverScroll from "./forever-scroll";
import h from "@macrostrat/hyper";
import { useAPIActions } from "@macrostrat/ui-components";
import { Spinner } from "@blueprintjs/core";

/**@description function to implement the infinite scroll component with certain API views
 *
 * @param {string} url: base url for API call.
 * @param {function} unWrapData: function that destructures json from API call. Must return an object that is compatible with the component also passed
 * @param {object} params: object of params to be added to base URL. Optional
 * @param {component} component: react component designed to take in data object created by the unWrapData function
 *
 *
 * @example function unWrapProjectCardData(data) {
  const dataObj = data.data.map((obj) => {
    const { id, name, description, publication, session } = obj;
    const samples = session.map((ob) => ob.sample);
    return { id, name, description, publication, samples };
  });
  return dataObj;
}
 return h(InfiniteAPIView, {
    url: projectURL,
    unWrapData: unWrapProjectCardData,
    params: {nest: "session,sample"},
    component: ProjectInfoLink,
  });
 */
function InfiniteAPIView({ url, unWrapData, params, component, context }) {
  const [data, setData] = useState([]);
  const [nextPage, setNextPage] = useState("");
  const { get } = useAPIActions(context);

  async function getNextPageAPI(nextPage, url, params) {
    const constParams =
      nextPage == "" ? { per_page: 15 } : { per_page: 15, page: nextPage };
    const newParams = { ...params, ...constParams };
    try {
      const data = await get(url, newParams, {});
      return data;
    } catch (error) {
      console.log(error);
    }
  }

  useEffect(() => {
    const initData = getNextPageAPI("", url, params);
    initData.then((res) => {
      const dataObj = unWrapData(res);
      const newState = [...data, ...dataObj];
      setNextPage(res.next_page);
      setData(newState);
    });
  }, []);

  const fetchNewData = () => {
    if (!nextPage) return;
    const newData = getNextPageAPI(nextPage, url, params);
    newData.then((res) => {
      const dataObj = unWrapData(res);
      const newState = [...data, ...dataObj];
      setNextPage(res.next_page);
      setData(newState);
    });
  };

  return data.length > 0
    ? h(ForeverScroll, {
        initialData: data,
        fetch: fetchNewData,
        component,
      })
    : h("div", { style: { marginTop: "100px" } }, [h(Spinner)]);
}

export { InfiniteAPIView };
