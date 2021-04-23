import { sum } from "d3-array";

interface ColumnData {
  name: string;
  key: string;
  width?: number;
  idealWidth?: number;
  editable?: boolean;
}

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

export { ColumnData, apportionWidths };
