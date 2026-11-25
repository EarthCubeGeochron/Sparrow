import React, { useState } from "react";
import { Icon, InputGroup, Button } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { usePostgRESTResult } from "~/api/postgrest";
import { normalizeSample, normalizeSession } from "~/api/models";
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
        h.if(model == "sample")(SampleModelCard, normalizeSample(data)),
        h.if(model == "project")(ProjectModelCard, { ...data }),
        h.if(model == "session")(SessionListModelCard, normalizeSession(data)),
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
  const term = query.trim();

  // Very short terms match nearly everything as prefixes
  const data = usePostgRESTResult(term.length >= 2 ? "/rpc/search" : null, {
    term,
  });
  const scrollData = term.length >= 2 ? data ?? [] : [];

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
          // Remount per term so the scroller drops the previous results
          key: term,
          initialData: scrollData,
          fetch: () => {},
        },
        [h(OpenSearchCard)]
      ),
    ]),
  ]);
}

export { OpenSearch };
