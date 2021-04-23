import { hyperStyled } from "@macrostrat/hyper";
import { useContext, useRef, useState, memo, useMemo } from "react";
import ReactDataSheet from "react-datasheet";
import {
  useElementSize,
  useScrollOffset,
  useDataSheet,
} from "@earthdata/sheet/src/index.ts";
import styles from "./module.styl";

const h = hyperStyled(styles);

const defaultSize = { height: 20, width: 100 };

function VirtualizedSheet(props) {
  const {
    data,
    rowRenderer,
    dataEditor,
    onCellsChanged,
    scrollBuffer = 50,
    ...rest
  } = props;

  const { rowHeight, selection, dispatch } = useDataSheet();

  const ref = useRef<HTMLDivElement>();

  const { height, width } = useElementSize(ref) ?? defaultSize;
  const scrollOffset = useScrollOffset(ref);

  const scrollerHeight = data.length * rowHeight;
  const percentage = scrollOffset / scrollerHeight;
  const rowsToDisplay = Math.ceil((height + scrollBuffer) / rowHeight);
  const rowOffset = Math.floor(percentage * (data.length - rowsToDisplay + 5));

  const virtualRowRenderer = ({ row, ...rest }) =>
    rowRenderer({ row: row + rowOffset, ...rest });

  function virtualDataEditor({ row, ...rest }) {
    return dataEditor({
      row: row + rowOffset,
      ...rest,
    });
  }
  const virtualSheetRenderer = (props) => {
    console.log(props);
    return sheetRenderer(props);
  };

  const lastRow = Math.min(rowOffset + rowsToDisplay, data.length - 1);

  /*
  function onSelect(sel) {
    setSelection(sel);
    return;
    console.log(sel);
    // Offset the row selection by the displayed range of rows
    const { start, end } = sel;
    console.log(sel, rowOffset);
    setSelection({
      start: { i: start.i + rowOffset, j: start.j },
      end: { i: end.i + rowOffset, j: end.j },
    });
  }

  let offsetSelection = null;
  if (selection != null) {
    offsetSelection = {
      start: { i: selection.start.i - rowOffset, j: selection.start.j },
      end: { i: selection.end.i - rowOffset, j: selection.end.j },
    };
  }
  */

  return h("div.virtualized-sheet", { ref }, [
    h("div.ui", { style: { height, width } }, [
      h(ReactDataSheet, {
        ...rest,
        data: data.slice(rowOffset, lastRow),
        selected: selection,
        onSelect(sel) {
          dispatch({ type: "set-selection", value: sel });
        },
        rowRenderer: virtualRowRenderer,
        onCellsChanged(changes) {
          console.log(changes);
          changes.forEach((d) => (d.row += rowOffset));
          onCellsChanged(changes);
        },
        //dataEditor: virtualDataEditor,
      }),
    ]),
    h("div.scroll-panel", {
      style: { height: scrollerHeight },
    }),
  ]);
}

export { VirtualizedSheet };
