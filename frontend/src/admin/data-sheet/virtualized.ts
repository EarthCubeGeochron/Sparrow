import { hyperStyled } from "@macrostrat/hyper";
import { useContext, useRef, useState } from "react";
import ReactDataSheet from "react-datasheet";
import {
  DataSheetContext,
  useElementSize,
  useScrollOffset,
} from "@earthdata/sheet/src/index.ts";
import styles from "./module.styl";

const h = hyperStyled(styles);

const defaultSize = { height: 20, width: 100 };

function VirtualizedSheet(props) {
  const {
    data,
    rowRenderer,
    sheetRenderer,
    dataEditor,
    onCellsChanged,
    scrollBuffer = 50,
    ...rest
  } = props;
  const { rowHeight } = useContext(DataSheetContext);

  // { start: { i: number, j; number }, end: { i: number, j: number } }
  const [selection, setSelection] = useState({
    offset: null,
    notOffset: null,
  });

  const ref = useRef<HTMLDivElement>();

  const { height, width } = useElementSize(ref) ?? defaultSize;
  const scrollOffset = useScrollOffset(ref);

  const scrollerHeight = data.length * rowHeight;
  const percentage = scrollOffset / scrollerHeight;
  const rowsToDisplay = Math.ceil((height + scrollBuffer) / rowHeight);
  const rowOffset = Math.floor(percentage * (data.length - rowsToDisplay + 5));

  function virtualRowRenderer({ row, children, className }) {
    return rowRenderer({ row: row + rowOffset, children, className });
  }
  function virtualDataEditor({
    row,
    children,
    value,
    col,
    cell,
    onChange,
    onCommit,
    onKeyDown,
    onRevert,
  }) {
    return dataEditor({
      row: row + rowOffset,
      children,
      value,
      col,
      cell,
      onChange,
      onCommit,
      onKeyDown,
      onRevert,
    });
  }
  function virtualSheetRenderer({ column, children, className }) {
    return sheetRenderer({
      column: column,
      children,
      className,
      width,
    });
  }

  const lastRow = Math.min(rowOffset + rowsToDisplay, data.length - 1);

  function onSelect({ start, end }) {
    /** Offset the row selection by the displayed range of rows */
    const startI = start.i + rowOffset;
    const startJ = start.j;
    const endI = end.i + rowOffset;
    const endJ = end.j;
    const selected = {
      start: { i: startI, j: startJ },
      end: { i: endI, j: endJ },
    };
    setSelection({ offset: selected, notOffset: { start, end } });
  }

  return h("div.virtualized-sheet", { ref }, [
    h("div.ui", { style: { height, width } }, [
      h(ReactDataSheet, {
        data: data.slice(rowOffset, lastRow),
        //selected: selection.notOffset,
        //onSelect,
        rowRenderer: virtualRowRenderer,
        sheetRenderer: virtualSheetRenderer,
        onCellsChanged(changes) {
          changes.forEach((d) => (d.row += rowOffset));
          onCellsChanged(changes);
        },
        dataEditor: virtualDataEditor,
        ...rest,
      }),
    ]),
    h("div.scroll-panel", {
      style: { height: scrollerHeight },
    }),
  ]);
}

export { VirtualizedSheet };
