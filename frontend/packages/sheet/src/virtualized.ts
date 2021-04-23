import ReactDataSheet, { DataEditor } from "react-datasheet/lib";
import { useDataSheet } from "./provider";

function VirtualizedDataEditor({ row, ...rest }) {
  const { rowOffset } = useDataSheet();
  return DataEditor({
    row: row + rowOffset,
    ...rest,
  });
}

type OptionalSelection = ReactDataSheet.Selection | null;

function offsetSelection(
  sel: OptionalSelection,
  offset: number
): OptionalSelection {
  if (sel == null) return null;
  const { start, end } = sel;
  return {
    start: { i: start.i + offset, j: start.j },
    end: { i: end.i + offset, j: end.j },
  };
}

export { VirtualizedDataEditor, offsetSelection };
