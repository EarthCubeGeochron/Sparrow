import { useEffect, useState } from "react";
import ForeverScroll from "./forever-scroll";
import { hyperStyled } from "@macrostrat/hyper";
import { useAPIActions, setQueryString } from "@macrostrat/ui-components";
import { Spinner } from "@blueprintjs/core";
import { NoSearchResults } from "./utils";
import { ErrorCallout } from "~/util";
//@ts-ignore
import styles from "./main.styl";

const h = hyperStyled(styles);

/**@description function to implement the infinite scroll component with certain API views
 *
 * @param {string} url: base url for API call.
 * @param {function} unwrapData: function that destructures json from API call. Must return an object that is compatible with the component also passed
 * @param {object} params: object of params to be added to base URL. Optional
 * @param {component} component: react component designed to take in data object created by the unwrapData function
 *
 *
 * @example function unwrapProjectCardData(data) {
  const dataObj = data.data.map((obj) => {
    const { id, name, description, publication, session } = obj;
    const samples = session.map((ob) => ob.sample);
    return { id, name, description, publication, samples };
  });
  return dataObj;
}
 return h(InfiniteAPIView, {
    url: projectURL,
    unwrapData: unwrapProjectCardData,
    params: {nest: "session,sample"},
    component: ProjectInfoLink,
  });
 */
function InfiniteAPIView({
  url,
  unwrapData,
  params,
  component,
  componentProps = {},
  context,
  filterParams,
  errorHandler = ErrorCallout,
  modelName,
}) {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const [noResults, setNoResults] = useState(false);
  const [nextPage, setNextPage] = useState("");
  const [moreAfter, setMoreAfter] = useState(true);
  const { get } = useAPIActions(context);

  async function getNextPageAPI(nextPage, url, params) {
    const constParams =
      nextPage == "" ? { per_page: 15 } : { per_page: 15, page: nextPage };
    const moreParams = { ...params, ...filterParams };
    const newParams = { ...moreParams, ...constParams };
    try {
      const data = await get(url, newParams, {});
      return data;
    } catch (error) {
      let msg;
      if (error != null) {
        msg = error.message;
        setError(msg);
      }
    }
  }

  useEffect(() => {
    dataFetch(data);
  }, []);

  const dataFetch = (data, next = "") => {
    setNoResults(false);
    const initData = getNextPageAPI(next, url, params);
    initData.then((res) => {
      if (res.data.length == 0) {
        setNoResults(true);
      }
      const dataObj = unwrapData(res);
      const newState = [...data, ...dataObj];
      const next_page = res.next_page;
      if (next_page == null) {
        setMoreAfter(false);
      }
      setNextPage(next_page);
      setData(newState);
    });
  };

  useEffect(() => {
    setData([]);
    dataFetch([]);
  }, [JSON.stringify(filterParams)]);

  const fetchNewData = async () => {
    if (!nextPage) return;
    dataFetch(data, nextPage);
  };

  if (error) {
    return h(errorHandler, { error, title: "An API error has occured" });
  }

  if (noResults) {
    return h(NoSearchResults);
  }

  if (data.length > 0) {
    return h(ForeverScroll, {
      initialData: data,
      fetch: fetchNewData,
      modelName,
      component,
      moreAfter,
      componentProps,
    });
  }
  return h("div", { style: { marginTop: "100px" } }, [h(Spinner)]);
}

export { InfiniteAPIView };

/**
 * This can probably get replaced with something from U.I Components
 * @param params {} key, value pairs of parameters
 */
export function urlSearchFromParams(params) {
  setQueryString(params);
}
