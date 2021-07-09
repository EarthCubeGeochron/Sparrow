import { useState, useEffect } from "react";
import { Button, Popover, Menu, Icon } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import {
  ProjectModelCard,
  SessionListModelCard,
  SampleModelCard
} from "~/model-views/components";
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
  const [model, setModel] = useState("project");
  const [scrollData, setScrollData] = useState<any>([]);
  const url = "/api/v2/search/query";

  const unwrapData =
    model == "session"
      ? data => {
          const dataObj = data.data.map(obj => {
            const {
              id: session_id,
              technique,
              target,
              date,
              instrument,
              data
            } = obj;
            return {
              session_id,
              technique,
              target,
              date,
              data,
              instrument
            };
          });
          return { data: dataObj };
        }
      : data => data;

  const data = useAPIv2Result(
    url,
    { query: query, model: model },
    { unwrapResponse: unwrapData }
  );

  console.log(scrollData);

  useEffect(() => {
    if (data && data["data"] != null) {
      setScrollData([]);
      setScrollData(data["data"]);
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

  const possibleModels = ["project", "session"];

  const content = h(Menu, [
    possibleModels.map(model => {
      return h(
        Button,
        {
          key: model,
          minimal: true,
          onClick: () => {
            setScrollData([]);
            setModel(model);
          }
        },
        [model]
      );
    })
  ]);

  const rightElement = h(Popover, { content, position: "bottom-right" }, [
    h(Button, { minimal: true, rightIcon: "caret-down" }, model)
  ]);

  return h("div", [
    h("div.searchbox", [
      h(SearchInput, {
        leftElement: h(Icon, { icon: "search" }),
        updateParams: onChange,
        value: query,
        rightElement: rightElement
      })
    ]),
    h("div.results", [
      h.if(scrollData.length > 0)(ForeverScroll, {
        initialData: scrollData,
        component:
          model == "sample"
            ? SampleModelCard
            : model == "project"
            ? ProjectModelCard
            : SessionListModelCard,
        fetch: () => {}
      })
    ])
  ]);
}

export { OpenSearch };
