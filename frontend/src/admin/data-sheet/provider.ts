import { createContext } from "react";
import h, { compose, C } from "@macrostrat/hyper";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";

const defaultContext = { columns: [], rowHeight: 20, offset: 0, actions: null };

type ColumnInfo = {
  name: string;
  width: number | null;
};

interface DataSheetContext {
  columns: ColumnInfo[];
  rowHeight: number;
}

const DataSheetContext = createContext(defaultContext);

function DataSheetProviderBase(props) {
  /** This context/context provider don't do much right now, but they will
      take an increasing role in state management going forward */

  const { columns, rowHeight, offset, reorderColumns, children } = props;
  const value = { columns, rowHeight, offset, actions: { reorderColumns } };
  return h(DataSheetContext.Provider, { value }, children);
}

DataSheetProviderBase.defaultProps = defaultContext;

const DataSheetProvider = compose(
  C(DndProvider, { backend: HTML5Backend }),
  DataSheetProviderBase
);

export { DataSheetContext, DataSheetProvider, ColumnInfo };
