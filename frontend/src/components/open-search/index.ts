import React, { useState, useEffect, ChangeEventHandler } from "react";
import { Icon, InputGroup, Button } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import {
  ProjectModelCard,
  SessionListModelCard,
  SampleModelCard,
  ModelCard,
} from "~/model-views/components";
import ForeverScroll from "~/components/infinite-scroll/forever-scroll";
import { SearchInput } from "~/filter/components";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

const OpenSearchCard = (props) => {
  const { model, data } = props;

  let possibleModels = {
    sample: SampleModelCard,
    project: ProjectModelCard,
    session: SessionListModelCard,
  };
  let data_ = { ...data, showIdentity: "long" };
  for (const key in possibleModels) {
    if (model == key) {
      return h("div", [h(possibleModels[key], data_)]);
    }
  }
  return h(ModelCard, ["Working"]);
};

interface OpenSearchInputProps {
  query: string;
  handleChange: (query: string) => void;
}

function OpenSearchInput(props: OpenSearchInputProps) {
  const { query, handleChange } = props;

  return h(InputGroup, {
    leftElement: h(Icon, { icon: "search" }),
    placeholder: "Search for anything...",
    value: query,
    onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
      handleChange(e.target.value),
    rightElement: h(Button, {
      icon: "arrow-right",
      // onClick: onSubmit,
      minimal: true,
      type: "submit",
    }),
  });
}

/**
 * React Component to create an open search on several models
 */
function OpenSearch() {
  const [query, setQuery] = useState("");
  const [scrollData, setScrollData] = useState<any>([]);
  const url = "search/query";

  const data = useAPIv2Result(url, { query: query, model: "all" });

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

  const onChange = (value) => {
    setQuery(value);
  };

  return h("div", [
    h("div.searchbox", [
      h(OpenSearchInput, {
        // onSubmit: ,
        handleChange: onChange,
        query,
      }),
    ]),
    h("div.results", [
      h.if(scrollData.length > 0)(ForeverScroll, {
        initialData: scrollData,
        component: OpenSearchCard,
        fetch: () => {},
      }),
    ]),
  ]);
}

export { OpenSearch };
