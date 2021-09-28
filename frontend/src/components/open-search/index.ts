import { useState, useEffect } from "react";
import { Icon } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import {
  ProjectModelCard,
  SessionListModelCard,
  SampleModelCard,
  ModelCard
} from "~/model-views/components";
import ForeverScroll from "~/components/infinite-scroll/forever-scroll";
import { SearchInput } from "~/filter/components";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

const OpenSearchCard = props => {
  const { model, data } = props;

  let possibleModels = {
    sample: SampleModelCard,
    project: ProjectModelCard,
    session: SessionListModelCard
  };
  let data_ = { ...data, showIdentity: "long" };
  for (const key in possibleModels) {
    if (model == key) {
      return h("div", [h(possibleModels[key], data_)]);
    }
  }
  return h(ModelCard, ["Working"]);
};

/**
 * React Component to create an open search on several models
 */
function OpenSearch() {
  const [query, setQuery] = useState("");
  const [scrollData, setScrollData] = useState<any>([]);
  const url = "search/query";

  const data = useAPIv2Result(url, { query: query, model: "all" });
  console.log("open search data", data);
  useEffect(() => {
    if (data) {
      setScrollData([]);
      setScrollData(data);
    } else if (query.length == 0) {
      setScrollData([]);
    }
    return () => {
      setScrollData([]);
    };
  }, [query, data]);

  useEffect(() => {
    setScrollData([]);
  }, [query]);

  if (!data) return null;

  const onChange = (text, value) => {
    setQuery(value);
  };

  return h("div", [
    h("div.searchbox", [
      h(SearchInput, {
        leftElement: h(Icon, { icon: "search" }),
        updateParams: onChange,
        value: query
      })
    ]),
    h("div.results", [
      h.if(scrollData.length > 0)(ForeverScroll, {
        initialData: scrollData,
        component: OpenSearchCard,
        fetch: () => {}
      })
    ])
  ]);
}

export { OpenSearch };
