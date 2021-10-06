import ReactDataSheet from "react-datasheet";
import { Field } from "./components";

interface GridElement extends ReactDataSheet.Cell<GridElement, number> {
  value: number | null;
}

export function getFieldData<K>(field: Field<K>): Field<K> {
  const {
    transform = (d) => parseFloat(d),
    isValid = (d) => !isNaN(d),
    required = true,
    ...rest
  } = field;
  return { ...rest, transform, isValid, required };
}

export function enhanceRow(row: GridElement[], fields: Field[]): any[] {
  if (row == null) return [];
  return row.map((cellData, i) => {
    const { dataEditor, valueViewer, key } = getFieldData(fields[i]);

    let addedProps = {};
    // if (key == "color") {
    //   addedProps.valueViewer = cell =>
    //     h(
    //       "span.value-viewer",
    //       { style: { color: getColor(cell.value), bacbac  } },
    //       cell.value
    //     );
    // }

    return { dataEditor, valueViewer, ...cellData, ...addedProps };
  });
}
