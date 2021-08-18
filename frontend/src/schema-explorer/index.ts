import React, { useState, useEffect } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { SchemaExplorer } from "./schema-explorer";
import { SchemaExplorerContextProvider } from "./context";
import { useRouteMatch } from "react-router-dom";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function SchemaMatch() {
  const {
    params: { model }
  } = useRouteMatch();

  return h(SchemaExplorerContextProvider, [h(SchemaExplorer, { model })]);
}

export { SchemaMatch };
