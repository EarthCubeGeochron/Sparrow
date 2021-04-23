import React, {
  createContext,
  useReducer,
  useContext,
  Dispatch,
  useEffect,
} from "react";
import h, { compose, C } from "@macrostrat/hyper";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import update from "immutability-helper";
import ReactDataSheet from "react-datasheet";
import { offsetSelection } from "./virtualized";
import { ColumnData, apportionWidths } from "./components/column-utils";

const defaultContext = {
  columns: [],
  rowHeight: 20,
  containerWidth: 500,
  rowOffset: 0,
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
  rowOffset: number;
  columns: ColumnData[];
}

interface DataSheetParams {
  rowHeight: number;
  containerWidth: number;
  virtualized: boolean;
  columns: ColumnData[];
}

type DataSheetCtx = DataSheetState &
  DataSheetParams & {
    dispatch: Dispatch<DataSheetAction>;
  };

type SetColumns = {
  type: "set-columns";
  value: ColumnData[];
};

type UpdateColumnWidth = {
  type: "update-column-width";
  key: string;
  value: number;
};

type SetSelection = {
  type: "set-selection";
  value: ReactDataSheet.Selection;
};

type MoveColumn = {
  type: "move-column";
  dragIndex: number;
  hoverIndex: number;
};

type SetRowOffset = {
  type: "set-row-offset";
  value: number;
};

type DataSheetProps = DataSheetParams & {
  // This is too complicated by half...
  desiredWidths: WidthSpec;
  children: React.ReactNode;
};

type DataSheetAction =
  | UpdateColumnWidth
  | SetSelection
  | SetRowOffset
  | SetColumns
  | MoveColumn;

const DataSheetContext = createContext<DataSheetCtx>(defaultContext);

function dataSheetReducer(state: DataSheetState, action: DataSheetAction) {
  switch (action.type) {
    case "update-column-width":
      return update(state, {
        columnWidths: { [action.key]: { $set: action.value } },
      });
    case "set-columns":
      return { ...state, columns: action.value };
    case "move-column":
      // Move a column in response ot a drag
      const { dragIndex, hoverIndex } = action;
      return update(state, {
        columns: {
          $splice: [
            [dragIndex, 1], // remove column from drag index
            [hoverIndex, 0, state.columns[dragIndex]], // ...and insert at hover index
          ],
        },
      });
    case "set-selection":
      return update(state, {
        selection: { $set: offsetSelection(action.value, state.rowOffset) },
      });
    case "set-row-offset":
      return update(state, { rowOffset: { $set: action.value } });
  }
  return state;
}

function DataSheetProviderBase(props: DataSheetProps) {
  /** This context/context provider don't do much right now, but they will
      take an increasing role in state management going forward */
  const {
    columns,
    rowHeight,
    children,
    virtualized = true,
    desiredWidths,
    containerWidth,
  } = props;

  const [state, dispatch] = useReducer(dataSheetReducer, {
    columnWidths: {},
    selection: null,
    rowOffset: 0,
    columns,
  });

  useEffect(() => {
    // If we don't have this we'll get an infinite loop
    const col = apportionWidths(columns, desiredWidths, containerWidth);
    console.log(col, containerWidth);
    dispatch({ type: "set-columns", value: col });
  }, [containerWidth, desiredWidths, columns]);

  const value = {
    virtualized,
    rowHeight,
    rowOffset: state.rowOffset,
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
