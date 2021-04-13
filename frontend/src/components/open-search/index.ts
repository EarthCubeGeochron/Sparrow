import { useState, useEffect } from "react";
import { Button } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { ProjectModelCard } from "~/model-views/components";
import ForeverScroll from "~/components/infinite-scroll/forever-scroll";
import { SearchInput } from "~/filter/components";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

/**
 * React Component to create an open search on several models
 */
function OpenSearch() {
  const [query, setQuery] = useState("");
  const [scrollData, setScrollData] = useState<any>([]);
  const url = query == "" ? "/api/v2/search" : `/api/v2/search?query=${query}`;
  const data = useAPIv2Result(url);

  useEffect(() => {
    if (data && data["data"] != null) {
      setScrollData(data["data"]);
    } else if (query.length == 0) {
      setScrollData([]);
    }
    console.log("triggered");
    return () => {
      setScrollData([]);
    };
  }, [query, data]);

  if (!data) return null;

  const onChange = (text, value) => {
    setQuery(value);
  };

  const onSearch = (e) => {
    e.preventDefault();
  };

  return h("div", [
    h("div.searchbox", [
      h(SearchInput, {
        updateParams: onChange,
        value: query,
        rightElement: h(Button, {
          icon: "search",
          onClick: onSearch,
          minimal: true,
          type: "submit",
        }),
      }),
    ]),
    h("div.results", [
      h.if(scrollData.length > 0)(ForeverScroll, {
        initialData: scrollData,
        component: ProjectModelCard,
        fetch: () => {},
      }),
    ]),
  ]);
}

export { OpenSearch };
