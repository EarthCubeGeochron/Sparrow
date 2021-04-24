import { useRef, memo } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { ColumnInfo, useDataSheet } from "../provider";
import { useColumnDropTarget, useColumnWidths } from "./column-utils";
import { useDrag } from "react-dnd";
import Draggable from "react-draggable";
import styles from "../module.styl";

const h = hyperStyled(styles);

function Row({ row, children, className }) {
  const { rowHeight, rowOffset } = useDataSheet();
  const style = { height: rowHeight };
  return h("tr", { style, className }, [
    h("td.index-cell.cell.read-only.index", row + rowOffset + 1),
    children,
  ]);
}

function Columns() {
  const columns = useColumnWidths();
  return h("colgroup", [
    h("col.index-column", { key: "index", style: { width: 50 } }),
    columns.map(({ width, key }) => {
      return h("col", {
        key,
        style: { width },
      });
    }),
  ]);
}

function ColumnResizeHandles() {
  const { dispatch } = useDataSheet();
  const columnWidths = useColumnWidths();
  return h(
    "td.column-resizers",
    columnWidths.map((d, i) => {
      if (i == columnWidths.length - 1) return null;
      return h(
        Draggable,
        {
          axis: "x",
          position: { x: d.offset + d.width, y: 0 },
          onStop(event, { x }) {
            dispatch({
              type: "update-column-width",
              key: d.key,
              value: x - d.offset,
            });
          },
        },
        h("span.cell-drag-handle", {
          onMouseDown(e) {
            e.preventDefault();
            e.stopPropagation();
          },
        })
      );
    })
  );
}

function HeaderCell({ col, index }: { col: ColumnInfo; index: number }) {
  const ref = useRef();

  const [, drop] = useColumnDropTarget(ref, index);

  const [{ isDragging }, drag] = useDrag({
    item: { id: col.name, index },
    type: "column",
    collect: (monitor: any) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const opacity = isDragging ? 0 : 1;

  drag(drop(ref));
  return h(
    "td.cell.header.read-only.header-cell",
    { style: { opacity }, key: col.name },
    [h("div.cell-content", { ref }, col.name)]
  );
}

function Header_({ width }) {
  const style = { width };
  const { columns } = useDataSheet();

  return h("thead", { style }, [
    h("tr.header", { style }, [
      h("td.index-column.cell", ""),
      columns.map((col, index) => {
        return h(HeaderCell, { key: col.name, col, index });
      }),
      h(ColumnResizeHandles),
    ]),
  ]);
}

const Header = memo(Header_);

function Sheet({ className, children }) {
  const { containerWidth: width } = useDataSheet();
  return h("table", { className, style: { width } }, [
    h(Columns),
    h(Header, { width }),
    h("tbody", children),
  ]);
}

export * from "./column-utils";
export { Sheet, Row };
