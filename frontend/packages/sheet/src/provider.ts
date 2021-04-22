import { createContext, useReducer, useContext, Dispatch } from "react";
import h, { compose, C } from "@macrostrat/hyper";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";

const defaultContext = {
  columns: [],
  rowHeight: 20,
  offset: 0,
  actions: null,
  columnWidths: {},
  dispatch: () => {},
};

type ColumnInfo = {
  name: string;
  width: number | null;
};

type WidthSpec = {
  [key: string]: number;
};

interface DataSheetState {
  columnWidths: WidthSpec;
}

interface DataSheetCtx extends DataSheetState {
  columns: ColumnInfo[];
  rowHeight: number;
  dispatch: Dispatch<DataSheetAction>;
}

type DataSheetAction = any;

const DataSheetContext = createContext<DataSheetCtx>(defaultContext);

function dataSheetReducer(state: DataSheetState, action: DataSheetAction) {
  return state;
}

function DataSheetProviderBase(props) {
  /** This context/context provider don't do much right now, but they will
      take an increasing role in state management going forward */

  const [state, dispatch] = useReducer(dataSheetReducer, { columnWidths: {} });

  const { columns, rowHeight, offset, reorderColumns, children } = props;
  const value = {
    columns,
    rowHeight,
    offset,
    actions: { reorderColumns },
    columnWidths: state.columnWidths,
    dispatch,
  };
  return h(DataSheetContext.Provider, { value }, children);
}

DataSheetProviderBase.defaultProps = defaultContext;

const DataSheetProvider = compose(
  C(DndProvider, { backend: HTML5Backend }),
  DataSheetProviderBase
);

const useDataSheetDispatch = () => useContext(DataSheetContext).dispatch;

export {
  DataSheetContext,
  DataSheetProvider,
  ColumnInfo,
  useDataSheetDispatch,
};