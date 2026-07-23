import React, { useEffect, useState } from "react";
import ForeverScroll from "./forever-scroll";
import { hyperStyled } from "@macrostrat/hyper";
import { useAPIActions, setQueryString } from "@macrostrat/ui-components";
import { Spinner } from "@blueprintjs/core";
import { NoSearchResults } from "./utils";
import { ErrorCallout } from "~/util";
//@ts-ignore
import styles from "./main.styl?inline";

const h = hyperStyled(styles);

function errorMessage(error) {
  if (error == null) return "The API request failed.";
  if (typeof error == "string") return error;

  const responseData = error.response?.data;
  if (typeof responseData == "string") return responseData;
  if (responseData?.error?.detail != null) return responseData.error.detail;
  if (responseData?.detail != null) return responseData.detail;
  if (responseData?.message != null) return responseData.message;

  return error.message ?? error.toString();
}

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
  params,
  children,
  context,
  filterParams,
  errorHandler = ErrorCallout,
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
      return await get(url, newParams, {});
    } catch (error) {
      setError(errorMessage(error));
      setMoreAfter(false);
      return null;
    }
  }

  const dataFetch = async (currentData, next = "") => {
    setNoResults(false);
    const res = await getNextPageAPI(next, url, params);
    if (res == null) return;

    if (!Array.isArray(res.data)) {
      setError("The API response did not include a data array.");
      setMoreAfter(false);
      return;
    }

    const pageData = res.data;
    if (pageData.length == 0 && currentData.length == 0) {
      setNoResults(true);
    }

    const newState = [...currentData, ...pageData];
    const next_page = res.next_page;
    if (next_page == null || pageData.length == 0) {
      setMoreAfter(false);
    }
    setNextPage(next_page);
    setData(newState);
  };

  useEffect(() => {
    setData([]);
    setError(null);
    setNextPage("");
    setMoreAfter(true);
    dataFetch([]);
  }, [url, JSON.stringify(params ?? {}), JSON.stringify(filterParams ?? {})]);

  const fetchNewData = async () => {
    if (!nextPage) return;
    dataFetch(data, nextPage);
  };

  if (error) {
    return h(errorHandler, { error, title: "An API error has occurred" });
  }

  if (noResults) {
    return h(NoSearchResults);
  }

  if (data.length > 0) {
    return h(
      ForeverScroll,
      {
        initialData: data,
        fetch: fetchNewData,
        moreAfter,
      },
      [children]
    );
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
