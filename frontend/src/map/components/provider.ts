import { createContext } from "react";
import h from "@macrostrat/hyper";

const DataSheetContext = createContext({ columns: [] });

function DataSheetProvider(props) {
  /** This context/context provider don't do much right now, but they will
      take an increasing role in state management going forward */
  const { columns, children } = props;
  const value = { columns };
  return h(DataSheetContext.Provider, { value }, children);
}

export { DataSheetContext, DataSheetProvider };
