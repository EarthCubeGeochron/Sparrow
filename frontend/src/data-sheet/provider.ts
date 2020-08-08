import { createContext } from "react";
import h from "@macrostrat/hyper";

const DataSheetContext = createContext({ columns: [] });

function DataSheetProvider(props) {
  const { columns, children } = props;
  const value = { columns };
  return h(DataSheetContext.Provider, { value }, children);
}

export { DataSheetContext, DataSheetProvider };
