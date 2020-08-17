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

  const scrollerHeight = data.length * rowHeight;
  const percentOffset = scrollOffset / scrollerHeight;
  const rowsToDisplay = Math.round((height / rowHeight) * 1.1);
  const rowOffset = Math.round(data.length * percentOffset);

  console.log(scrollOffset);

  function virtualRowRenderer({ row, children, className }) {
    return rowRenderer({ row: row + rowOffset, children, className });
  }

  return h("div.virtualized-sheet", { ref }, [
    h("div.ui", { style: { height } }, [
      h(ReactDataSheet, {
        data: data.slice(rowOffset, rowOffset + rowsToDisplay),
        rowRenderer: virtualRowRenderer,
        ...rest,
      }),
      h("div.scroll-panel", {
        style: { height: scrollerHeight },
      }),
    ]),
  ]);
}
