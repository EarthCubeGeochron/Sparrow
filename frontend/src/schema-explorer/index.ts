import { Switch, Route, useRouteMatch } from "react-router-dom";
import { hyperStyled } from "@macrostrat/hyper";
import { SchemaExplorer } from "./schema-explorer";
import { SchemaExplorerContextProvider } from "./context";
import { ErrorBoundary } from "@macrostrat/ui-components";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function SchemaMatch() {
  const {
    params: { model },
  } = useRouteMatch();

  return h(SchemaExplorerContextProvider, [h(SchemaExplorer, { model })]);
}

function SchemaExplorerMainPanel() {
  const base = "/import-schema-explorer";

  return h(ErrorBoundary, [
    h(Switch, [
      h(Route, {
        path: base + "/:model",
        render: () => h(SchemaMatch),
      }),
      h(Route, {
        path: base,
        render: () => h(SchemaMatch),
      }),
    ]),
  ]);
}

export default SchemaExplorerMainPanel;
