import * as React from "react";
import { useEffect, useState } from "react";
import ForeverScroll from "./forever-scroll";
import h from "@macrostrat/hyper";
import { useAPIResult } from "@macrostrat/ui-components";
import { Spinner } from "@blueprintjs/core";

async function getNextPageAPI(nextPage, url, params) {
  try {
    const response = await fetch(
      url + "?" + params + "&per_page=15" + "&page=" + nextPage
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.log(error);
  }
}
function unWrapData(data, destructure, optionalLogic) {
  const dataObj = data.data.map((obj) => {
    const destructure = obj;
    optionalLogic;
    return { ...destructure, ...optionalLogic };
  });
  return dataObj;
}

/**@description function to implement the infinite scroll component with certain API views
 *
 * @param {string} url: base url for API call.
 * @param {string} nest: Models to nest within base api. Optional
 * @param {function} unWrapData: function that destructures json from API call. Must return an object that is compatible with the component also passed
 * @param {string} params: string of full params to be added after base URL. Optional
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
    nest: projectNest,
    unWrapData: unWrapProjectCardData,
    params: projectParams,
    component: ProjectInfoLink,
  });
 */
function InfiniteAPIView({ url, nest, unWrapData, params, component }) {
  const [data, setData] = useState([]);
  const [nextPage, setNextPage] = useState("");

  const initData =
    nest == null
      ? useAPIResult(url, { per_page: 15 })
      : useAPIResult(url, { nest: nest, per_page: 15 });

  useEffect(() => {
    if (initData) {
      const dataObj = unWrapData(initData);
      //@ts-ignore
      const NextPage = initData.next_page;
      setNextPage(NextPage);
      setData(dataObj);
    }
  }, [initData]);

  const fetchNewData = () => {
    if (!nextPage) return;
    const newData = getNextPageAPI(nextPage, url, params);
    newData.then((res) => {
      const dataObj = unWrapData(res);
      const newState = [...data, ...dataObj];
      const NextPage = res.next_page;
      setNextPage(NextPage);
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
