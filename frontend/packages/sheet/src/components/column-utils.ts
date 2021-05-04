import { sum } from "d3-array";
import { useDataSheet } from "../provider";
import { useDrop, DropTargetMonitor } from "react-dnd";

interface ColumnData {
  name: string;
  key: string;
  width?: number;
  idealWidth?: number;
  editable?: boolean;
}

interface ColumnWidthInfo {
  key: string;
  offset: number;
  width: number;
}

type DragItem = {
  type: "column";
  id: string;
  index: number;
};

/* Column width functionality */
function apportionWidths(
  columns: ColumnData[],
  desiredWidths: { [key: string]: number },
  containerWidth: number
): ColumnData[] {
  if (columns == null || desiredWidths == null || containerWidth == null)
    return columns;

  const totalSize = sum(Object.values(desiredWidths));

  //console.log(maxContentWidth);

  return columns.map((col) => {
    return {
      ...col,
      width: (desiredWidths[col.key] / totalSize) * (containerWidth - 50),
    };
  });
}

function useColumnDropTarget(ref, index) {
  const { dispatch } = useDataSheet();
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
      dispatch({ type: "move-column", dragIndex, hoverIndex });
      //moveCard(dragIndex, hoverIndex);

      // Note: we're mutating the monitor item here!
      // Generally it's better to avoid mutations,
      // but it's good here for the sake of performance
      // to avoid expensive index searches.
      item.index = hoverIndex;
    },
  });
}

function useColumnWidths(): ColumnWidthInfo[] {
  const { columns, columnWidths, containerWidth } = useDataSheet();
  console.log("Container width:", containerWidth);

  let widthArray = [];
  let offset = 50; // for index, we should probably not hard-code this...
  for (const [i, col] of columns.entries()) {
    let width = columnWidths[col.name] ?? col.width ?? 0;
    if (i == columns.length - 1) {
      // special case for last column to fill container
      width = containerWidth - offset;
    }

    widthArray.push({
      key: col.name,
      offset: offset,
      width,
    });
    offset += width;
  }
  return widthArray;
}

export { ColumnData, apportionWidths, useColumnWidths, useColumnDropTarget };
