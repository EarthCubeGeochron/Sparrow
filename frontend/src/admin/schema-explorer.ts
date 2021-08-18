import { Switch, Route, Link } from "react-router-dom";
import hype from "@macrostrat/hyper";
import styles from "./module.styl";
import { SchemaMatch } from "~/schema-explorer";

const h = hype.styled(styles);

function SchemaExplorerMainPanel() {
  const base = "/admin/schema-explorer";

  return h(Switch, [
    h(Route, {
      path: base + "/:model",
      render: () => h(SchemaMatch)
    }),
    h(Route, {
      path: base,
      render: () => h(SchemaMatch)
    })
  ]);
}

export { SchemaExplorerMainPanel };
