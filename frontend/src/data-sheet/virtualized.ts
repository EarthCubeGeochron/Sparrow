import { hyperStyled } from "@macrostrat/hyper";
import { useContext, useRef, createContext, useState, useEffect } from "react";
import { useElementHeight, useScrollOffset } from "./util";
import ReactDataSheet from "react-datasheet";
import { DataSheetContext } from "./provider";
import styles from "./module.styl";
const h = hyperStyled(styles);

function VirtualizedSheet(props) {
  const { data, rowRenderer, sheetRenderer, onCellsChanged, ...rest } = props;
  const { rowHeight } = useContext(DataSheetContext);

  // { start: { i: number, j; number }, end: { i: number, j: number } }
  const [selection, setSelection] = useState(null);
  const [offsetSelection, setOffsetSelection] = useState(null);

  const ref = useRef<HTMLDivElement>();

  const [height, width] = useElementHeight(ref) ?? [100, 20];
  console.log(width);
  const scrollOffset = useScrollOffset(ref);
  const buffer = 50;

  const scrollerHeight = data.length * rowHeight;
  const percentage = scrollOffset / scrollerHeight;
  const rowsToDisplay = Math.ceil((height + buffer) / rowHeight);
  const rowOffset = Math.floor(percentage * (data.length - rowsToDisplay + 5));

  function virtualRowRenderer({ row, children, className }) {
    return rowRenderer({ row: row + rowOffset, children, className });
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
    const startI = start.i + rowOffset;
    const startJ = start.j;
    const endI = end.i + rowOffset;
    const endJ = end.j;
    const selected = {
      start: { i: startI, j: startJ },
      end: { i: endI, j: endJ },
    };
    console.log({ start, end });
    setSelection(selected);
    setOffsetSelection({ start, end });
  }
  console.log(selection);
  console.log(offsetSelection);
  console.log(rowOffset);

  return h("div.virtualized-sheet", { ref }, [
    h("div.ui", { style: { height, width } }, [
      h(ReactDataSheet, {
        data: data.slice(rowOffset, lastRow),
        //selected: offsetSelection,
        onSelect,
        rowRenderer: virtualRowRenderer,
        sheetRenderer: virtualSheetRenderer,
        onCellsChanged(changes) {
          changes.forEach((d) => (d.row += rowOffset));
          onCellsChanged(changes);
        },
        ...rest,
      }),
    ]),
    h("div.scroll-panel", {
      style: { height: scrollerHeight },
    }),
  ]);
}

export { VirtualizedSheet };
