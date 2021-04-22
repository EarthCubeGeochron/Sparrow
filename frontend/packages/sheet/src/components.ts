import { useContext, useRef } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { DataSheetContext, ColumnInfo } from "./provider";
import { useDrag, useDrop, DropTargetMonitor } from "react-dnd";
import Draggable from "react-draggable";
import styles from "./module.styl";
// https://codesandbox.io/s/github/react-dnd/react-dnd/tree/gh-pages/examples_hooks_ts/04-sortable/simple?from-embed=&file=/src/Container.tsx

const h = hyperStyled(styles);

function Row({ row, children, className }) {
  const { rowHeight } = useContext(DataSheetContext);
  const style = { height: rowHeight };
  return h("tr", { style, className }, [
    h("td.index-cell.cell.read-only.index", row + 1),
    children,
  ]);
}

type DragItem = {
  type: "column";
  id: string;
  index: number;
};

function useColumnDropTarget(ref, index) {
  const { actions } = useContext(DataSheetContext);
  return useDrop({
    accept: "column",
    hover(item: DragItem, monitor: DropTargetMonitor) {
      if (!ref.current) {
        return;
      }
      const dragIndex = item.index;
      const hoverIndex = index;

      // Don't replace items with themselves
      if (dragIndex === hoverIndex) {
        return;
      }

      // Determine rectangle on screen
      const hoverBoundingRect = ref.current?.getBoundingClientRect();

      // Get horizontal middle
      const hoverMiddleX =
        (hoverBoundingRect.right - hoverBoundingRect.left) / 2;

      // Determine mouse position
      const clientOffset = monitor.getClientOffset();

      // Get pixels to the left
      const hoverClientX = clientOffset.x - hoverBoundingRect.left;

      // Only perform the move when the mouse has crossed half of the items height
      // When dragging downwards, only move when the cursor is below 50%
      // When dragging upwards, only move when the cursor is above 50%
      // Dragging downwards
      if (dragIndex < hoverIndex && hoverClientX < hoverMiddleX) {
        return;
      }

      // Dragging upwards
      if (dragIndex > hoverIndex && hoverClientX > hoverMiddleX) {
        return;
      }

      // Time to actually perform the action
      actions?.reorderColumns(dragIndex, hoverIndex);
      //moveCard(dragIndex, hoverIndex);

      // Note: we're mutating the monitor item here!
      // Generally it's better to avoid mutations,
      // but it's good here for the sake of performance
      // to avoid expensive index searches.
      item.index = hoverIndex;
    },
  });
}

function HeaderCell({ col, index }: { col: ColumnInfo; index: number }) {
  const { name, width } = col;
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
    [
      h("div.cell-content", { ref }, name),
      h(
        Draggable,
        {
          axis: "x",
          positionOffset: { x: 0, y: 0 },
          onStop() {
            console.log(arguments);
          },
        },
        h("span.cell-drag-handle", {
          onMouseDown(e) {
            e.preventDefault();
            e.stopPropagation();
          },
        })
      ),
    ]
  );
}

function Columns({ width }) {
  const { columns } = useContext(DataSheetContext);
  return h("colgroup", [
    h("col.index-column", { key: "index", style: { width: 50 } }),
    columns.map((col) =>
      h("col", { key: col.name, style: { width: col.width } })
    ),
  ]);
}

function Header({ width }) {
  const style = { width };
  const { columns } = useContext(DataSheetContext);

  return h("thead", { style }, [
    h("tr.header", { style }, [
      h("td.index-column.cell", ""),
      columns.map((col, index) => {
        return h(HeaderCell, { key: col.name, col, index });
      }),
    ]),
  ]);
}

function Sheet({ className, children, width }) {
  return h("table", { className, style: { width } }, [
    h(Columns),
    h(Header, { width }),
    h("tbody", children),
  ]);
}

export { Sheet, Row };