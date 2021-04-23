import { createContext, useReducer, useContext, Dispatch } from "react";
import h, { compose, C } from "@macrostrat/hyper";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import update from "immutability-helper";
import ReactDataSheet from "react-datasheet";

const defaultContext = {
  columns: [],
  rowHeight: 20,
  containerWidth: 500,
  offset: 0,
  actions: null,
  selection: null,
  columnWidths: {},
  dispatch: () => {},
  virtualized: false,
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
  selection: ReactDataSheet.Selection | null;
}

interface DataSheetCtx extends DataSheetState {
  columns: ColumnInfo[];
  rowHeight: number;
  containerWidth: number;
  virtualized: boolean;
  dispatch: Dispatch<DataSheetAction>;
}

type UpdateColumnWidth = {
  type: "update-column-width";
  key: string;
  value: number;
};

type SetSelection = {
  type: "set-selection";
  value: ReactDataSheet.Selection;
};

type DataSheetAction = UpdateColumnWidth | SetSelection;

const DataSheetContext = createContext<DataSheetCtx>(defaultContext);

function dataSheetReducer(state: DataSheetState, action: DataSheetAction) {
  switch (action.type) {
    case "update-column-width":
      return update(state, {
        columnWidths: { [action.key]: { $set: action.value } },
      });
    case "set-selection":
      return update(state, { selection: { $set: action.value } });
  }
  return state;
}

function DataSheetProviderBase(props) {
  /** This context/context provider don't do much right now, but they will
      take an increasing role in state management going forward */

  const [state, dispatch] = useReducer(dataSheetReducer, {
    columnWidths: {},
    selection: null,
  });

  const {
    columns,
    rowHeight,
    offset,
    reorderColumns,
    children,
    containerWidth,
  } = props;
  const value = {
    columns,
    rowHeight,
    offset,
    actions: { reorderColumns },
    dispatch,
    containerWidth,
    ...state,
  };
  return h(DataSheetContext.Provider, { value }, children);
}

DataSheetProviderBase.defaultProps = defaultContext;

const DataSheetProvider = compose(
  C(DndProvider, { backend: HTML5Backend }),
  DataSheetProviderBase
);

const useDataSheet = () => useContext(DataSheetContext);
const useDispatch = () => useDataSheet().dispatch;

export {
  DataSheetContext,
  DataSheetProvider,
  ColumnInfo,
  useDispatch,
  useDataSheet,
};
