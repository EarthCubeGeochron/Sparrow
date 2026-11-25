import React, { useEffect, useState } from "react";
import ForeverScroll from "./forever-scroll";
import { hyperStyled } from "@macrostrat/hyper";
import { setQueryString } from "@macrostrat/ui-components";
import { QueryParams, usePostgRESTGet } from "~/api/postgrest";
import { filterParams as toPostgRESTFilters } from "~/api/models";
import { useAuth } from "~/auth/context";
import { Spinner } from "@blueprintjs/core";
import { NoSearchResults } from "./utils";
import { ErrorCallout } from "~/util";
//@ts-ignore
import styles from "./main.styl";

const h = hyperStyled(styles);

const perPage = 15;

interface InfiniteAPIViewProps {
  url: string;
  /** Model name, for translating the admin filters */
  model: string;
  params?: QueryParams;
  filterParams?: object;
  normalize?: (row: object) => object;
  children: React.ReactNode;
  errorHandler?: React.ComponentType<any>;
}

/** An endless list of PostgREST records, fetched a page at a time with limit/offset */
function InfiniteAPIView({
  url,
  model,
  params = {},
  children,
  filterParams = {},
  normalize,
  errorHandler = ErrorCallout,
}: InfiniteAPIViewProps) {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const [noResults, setNoResults] = useState(false);
  const [nextOffset, setNextOffset] = useState(0);
  const [moreAfter, setMoreAfter] = useState(true);
  const get = usePostgRESTGet();
  const { token } = useAuth();

  const dataFetch = (data, offset = 0) => {
    setNoResults(false);
    const query = {
      ...params,
      ...toPostgRESTFilters(model, filterParams),
      limit: perPage,
      offset,
    };
    get(url, query).then((res) => {
      if (res == null) {
        setError("Could not load records");
        return;
      }
      if (res.length == 0 && offset == 0) {
        setNoResults(true);
      }
      const rows = normalize == null ? res : res.map(normalize);
      setMoreAfter(res.length == perPage);
      setNextOffset(offset + res.length);
      setData([...data, ...rows]);
    });
  };

  useEffect(() => {
    setData([]);
    setMoreAfter(true);
    dataFetch([]);
  }, [JSON.stringify(filterParams), token]);

  const fetchNewData = async () => {
    if (!moreAfter) return;
    dataFetch(data, nextOffset);
  };

  if (error) {
    return h(errorHandler, { error, title: "An API error has occured" });
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
