import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { Card, Spinner } from "@blueprintjs/core";
import styles from "./module.styl";
import { LinkCard } from "@macrostrat/ui-components";
import { useModelURL } from "~/util/router";
import { Route, Switch } from "react-router-dom";
import { DataFilePage } from "./page";

const h = hyperStyled(styles);

export function DataFilesList(props) {
  const res =
    useAPIv2Result("/models/data_file", { per_page: 100 })?.data ?? [];
  if (!res) return;
  const data = res.map((d) => d);

  return data.length > 0
    ? h(
        "div.data-files",
        data.map((d) => {
          return h(
            LinkCard,
            { to: useModelURL(`/data-file/${d.file_hash}`) },
            h("div", { className: "data-file-card" }, [
              h("h2", d.basename),
              h("div.type", d.type),
            ])
          );
        })
      )
    : h(Spinner);
}

// This is for the Infinite Scroll, had to change the structure of data being passed
export function DataFilesCard(data) {
  const { file_hash, basename, type, date } = data;

  return h("div.data-files", [
    h(
      LinkCard,
      { to: useModelURL(`/data-file/${file_hash}`) },
      h("div", { className: "data-file-card" }, [
        // h("h4", [format(date, "MMMM D, YYYY")]),
        h("h2", basename),
        h("div.type", type),
      ])
    ),
  ]);
}

// for catalog
function DataFilesMain(props) {
  const { match } = props;
  const base = match.path;
  return h(Switch, [
    h(Route, {
      path: base + "/:file_hash",
      component: DataFilePage,
    }),
    h(Route, {
      path: base,
      component: DataFilesList,
      exact: true,
    }),
  ]);
}

export { DataFilesMain };
