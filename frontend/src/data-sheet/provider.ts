import { createContext } from "react";
import h from "@macrostrat/hyper";

const DataSheetContext = createContext(null);

function DataSheetProvider() {
  const value = {};
  return h(DataSheetContext.Provider, { value });
}
