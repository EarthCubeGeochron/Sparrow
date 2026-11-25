import { hyperStyled } from "@macrostrat/hyper";
import { usePostgRESTResult } from "~/api/postgrest";
import { useAuth, LoginButton } from "~/auth";
import { NonIdealState, Spinner } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import { useModelURL } from "~/util/router";
import { Route, Switch } from "react-router-dom";
import { DataFileMatch } from "./page";
import { format } from "date-fns";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function DataFilesList(props) {
  const { login } = useAuth();
  // Where a lab keeps its files is visible to administrators only
  const data = usePostgRESTResult(login ? "/data_file" : null, {
    order: "file_mtime.desc.nullslast",
    limit: 100,
  });
  if (!login) {
    return h(NonIdealState, {
      icon: "lock",
      title: "Data files are visible to administrators",
      action: h(LoginButton),
    });
  }
  if (data == null) return h(Spinner);

  return h(
    "div.data-files",
    data.map((d) => {
      return h(
        LinkCard,
        { to: useModelURL(`/data-file/${d.file_hash}`) },
        h("div", { className: "data-file-card" }, [
          h("h2", d.basename),
          h("div.type", d.type_id),
        ])
      );
    })
  );
}

// This is for the Infinite Scroll, had to change the structure of data being passed
export function DataFilesCard(data) {
  const { file_hash, basename, type, date } = data;

  return h("div.data-files", [
    h(
      LinkCard,
      { to: useModelURL(`/data-file/${file_hash}`) },
      h("div.data-file-card", [
        h("div.content", [
          h.if(date !== null)("h4", { style: { padding: "0px" } }, [
            format(date, "MMMM D, YYYY"),
          ]),
          h("h2", basename),
          h("div.type", type),
        ]),
      ])
    ),
  ]);
}

// for catalog
function DataFilesMain(props) {
  const { match } = props;
  const base = "/catalog/data-file";
  return h(Switch, [
    h(Route, {
      path: base + "/:file_hash",
      component: DataFileMatch,
    }),
    h(Route, {
      path: base,
      component: DataFilesList,
      exact: true,
    }),
  ]);
}

export { DataFilesMain };
