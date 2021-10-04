import { createContext, useContext, useReducer } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { ColumnData, useDataSheet } from "@earthdata/sheet/src";
import { Button, Card, FormGroup, Switch } from "@blueprintjs/core";
import { Popover2 } from "@blueprintjs/popover2";
import { createSettingsContext } from "@macrostrat/ui-components";

import "@blueprintjs/popover2/lib/css/blueprint-popover2.css";
import styles from "./module.styl";

const h = hyperStyled(styles);

interface DataSheetSettingsProps {
  allColumns: ColumnData[];
}

interface DataSheetSettingsState {
  showColumns: { [key: string]: boolean };
}

type DataSheetSettingsCtx = DataSheetSettingsProps & DataSheetSettingsState;

/* Actions */

interface ToggleColumnOn {
  type: "toggle-column";
  key: string;
  isShown: boolean;
}

type DataSheetAction = ToggleColumnOn;

const DataSheetSettingsContext = createContext<DataSheetSettingsCtx>({
  allColumns: [],
  showColumns: {},
});

const DataSheetDispatchContext = createContext<
  (action: DataSheetAction) => void
>(() => {});

function reducer(state, action) {
  switch (action.type) {
    case "toggle-column":
      return {
        showColumns: {
          ...state.showColumns,
          [action.key]: action.isShown,
        },
      };
  }
}

function DataSheetSettingsProvider(props) {
  const { children, allColumns = [] } = props;
  const [state, dispatch] = useReducer(reducer, {
    showColumns: {},
  });
  return h(
    DataSheetSettingsContext.Provider,
    { value: { allColumns, ...state } },
    h(DataSheetDispatchContext.Provider, { value: dispatch }, children)
  );
}

const useSettings = () => useContext(DataSheetSettingsContext);
const useSettingsDispatch = () => useContext(DataSheetDispatchContext);

function ColumnToggle({
  column,
  isShown,
}: {
  column: ColumnData;
  isShown: boolean;
}) {
  const dispatch = useSettingsDispatch();
  return h(Switch, {
    checked: isShown,
    label: column.name,
    onChange() {
      dispatch({ type: "toggle-column", key: column.key, isShown: !isShown });
    },
  });
}

function ColumnToggleList(props) {
  const { showColumns = {}, allColumns } = useSettings();
  return h(
    FormGroup,
    { label: "Columns" },
    allColumns.map((col) => {
      return h(ColumnToggle, {
        isShown: showColumns[col.key] ?? true,
        column: col,
      });
    })
  );
}

function ColumnTogglePanel() {
  return h(Card, { elevation: 0 }, h(ColumnToggleList));
}

function SettingsPopup() {
  return h(
    Popover2,
    {
      content: h("div", null, h(ColumnTogglePanel)),
      rootBoundary: document.querySelector(".data-sheet-page"),
    },
    h(Button, { icon: "cog" }, "Settings")
  );
}

export { useSettings, DataSheetSettingsProvider, SettingsPopup };
