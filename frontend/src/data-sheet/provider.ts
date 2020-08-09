import { createContext } from "react";
import h from "@macrostrat/hyper";

const defaultContext = { columns: [], rowHeight: 20, offset: 0 };

const DataSheetContext = createContext(defaultContext);

function DataSheetProvider(props) {
  /** This context/context provider don't do much right now, but they will
      take an increasing role in state management going forward */
  const { columns, rowHeight, offset, children } = props;
  const value = { columns, rowHeight, offset };
  return h(DataSheetContext.Provider, { value }, children);
}

DataSheetProvider.defaultProps = defaultContext;

export { DataSheetContext, DataSheetProvider };
