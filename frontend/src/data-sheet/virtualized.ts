import { hyperStyled } from "@macrostrat/hyper";
import { useContext, useRef } from "react";
import { useElementHeight, useScrollOffset } from "./util";
import ReactDataSheet from "react-datasheet";
import { DataSheetContext } from "./provider";
import styles from "./module.styl";
const h = hyperStyled(styles);

export function VirtualizedSheet(props) {
  const { data, rowRenderer, ...rest } = props;
  const { rowHeight } = useContext(DataSheetContext);

  const ref = useRef<HTMLDivElement>();

  const height = useElementHeight(ref) ?? 100;
  const scrollOffset = useScrollOffset(ref);
  const buffer = 50;

  const scrollerHeight = data.length * rowHeight;
  const percentage = scrollOffset / scrollerHeight;
  const rowsToDisplay = Math.ceil((height + buffer) / rowHeight);
  const rowOffset = Math.floor(percentage * (data.length - rowsToDisplay + 5));

  function virtualRowRenderer({ row, children, className }) {
    return rowRenderer({ row: row + rowOffset, children, className });
  }

  const lastRow = Math.min(rowOffset + rowsToDisplay, data.length - 1);
  console.log(rowOffset, rowsToDisplay);

  return h("div.virtualized-sheet", { ref }, [
    h("div.ui", { style: { height } }, [
      h(ReactDataSheet, {
        data: data.slice(rowOffset, lastRow),
        rowRenderer: virtualRowRenderer,
        ...rest,
      }),
    ]),
    h("div.scroll-panel", {
      style: { height: scrollerHeight },
    }),
  ]);
}
