import React, { useState, useEffect } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { SchemaExplorer } from "./schema-explorer";
import { SchemaExplorerContextProvider } from "./context";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function SchemaExplorerRoot() {
  return h(SchemaExplorerContextProvider, [h(SchemaExplorer)]);
}

export default SchemaExplorerRoot;
