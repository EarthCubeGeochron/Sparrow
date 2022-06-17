import React, { useState, useEffect } from "react";
import { Icon, InputGroup, Button } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import {
  ProjectModelCard,
  SessionListModelCard,
  SampleModelCard,
} from "~/model-views/components";
import ForeverScroll from "~/components/infinite-scroll/forever-scroll";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

type OpenSearchCardData = { model: string; data: object };

interface OpenSearchCardProps {
  data: OpenSearchCardData[];
}
const OpenSearchCard = (props: OpenSearchCardProps) => {
  const { data } = props;

  return h(React.Fragment, [
    data.map((dat, i) => {
      const { model, data } = dat;
      return h(React.Fragment, [
        h.if(model == "sample")(SampleModelCard, { ...data }),
        h.if(model == "project")(ProjectModelCard, { ...data }),
        h.if(model == "session")(SessionListModelCard, { ...data }),
      ]);
    }),
  ]);
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
        handleChange: onChange,
        query,
      }),
    ]),
    h("div.results", [
      h.if(scrollData.length > 0)(
        ForeverScroll,
        {
          initialData: scrollData,
          fetch: () => {},
        },
        [h(OpenSearchCard)]
      ),
    ]),
  ]);
}

export { OpenSearch };
