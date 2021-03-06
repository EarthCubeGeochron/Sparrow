import * as React from "react";
import { useState, useEffect, useRef, useCallback } from "react";
import { useAPIResult } from "@macrostrat/ui-components";
import update from "immutability-helper";
import h from "@macrostrat/hyper";
import { Frame } from "~/frame";
import { DataSheetProvider } from "./provider";
import { SheetToolbar } from "./toolbar";
import { VirtualizedSheet } from "./virtualized";
import classNames from "classnames";
import styles from "./module.styl";
import { Row, Sheet } from "./components";
import { useElementSize } from "./util";
import { sum } from "d3-array";
import { APIV2Context } from "~/api-v2";

interface ColumnData {
  name: string;
  key: string;
  width?: number;
  editable?: boolean;
}

const columnSpec: ColumnData[] = [
  { name: "Sample Name", key: "name", width: 300, editable: false },
  { name: "IGSN", key: "igsn", width: 50 },
  { name: "Public", key: "is_public", width: 50 },
  { name: "Material", key: "material", width: 50 },
  { name: "Latitude", key: "latitude", width: 50 },
  { name: "Longitude", key: "longitude", width: 50 },
  { name: "Location name", key: "location_name", width: 50, editable: false },
  { name: "Project", key: "project_name", width: 50 },
];

function unwrapSampleData(sampleData) {
  /** Unwrap samples from API response to a flattened version */
  const { geometry, ...rest } = sampleData;
  console.log(rest);
  let longitude: number, latitude: number;
  if (geometry != null) {
    [longitude, latitude] = geometry?.coordinates;
  }
  return { longitude, latitude, is_public: true, ...rest };
}

function calculateWidths(data, columns) {
  const minWidth = 5;
  const maxWidth = 30;
  return data.reduce((acc, row) => {
    let obj = {};
    for (const col of columns) {
      const contentLength = `${row[col.key]}`.length;
      obj[col.key] = Math.min(
        Math.max(minWidth, contentLength, acc[col.key] ?? 0),
        maxWidth
      );
    }
    return obj;
  }, {});
}

function apportionWidth(
  data,
  columns: ColumnData[],
  containerWidth: number
): ColumnData[] {
  if (data == null || columns == null || containerWidth == null) return columns;

  const maxContentWidth = calculateWidths(data, columns);
  const totalSize = sum(Object.values(maxContentWidth));

  console.log(maxContentWidth);

  return columns.map((col) => {
    return {
      ...col,
      width: (maxContentWidth[col.key] / totalSize) * (containerWidth - 50),
    };
  });
}

function unwrapResponse(apiResult) {
  /** Flatten latitudes and longitudes for entire API response */
  return apiResult.map(unwrapSampleData);
}

interface SampleData {
  latitude: number;
  longitude: number;
  name: string;
}

function DataSheet() {
  const [data, setData] = useState<SampleData[]>([]);
  const initialData = useAPIResult<SampleData[]>(
    "/sample",
    { all: true }, //, nest: "sample_geo_entity,geo_entity" },
    {
      //context: APIV2Context,
      unwrapResponse,
    }
  );

  useEffect(() => {
    // Set data to start with the value of the initial data
    if (initialData == null) return;
    setData(initialData);
  }, [initialData]);

  const ref = useRef<HTMLDivElement>();
  const size = useElementSize(ref) ?? { width: 500, height: 100 };

  const [columns, setColumns] = useState(columnSpec);

  const reorderColumns = useCallback(
    (dragIndex: number, hoverIndex: number) => {
      /** Reorder columns with drag/drop */
      setColumns(
        update(columns, {
          $splice: [
            [dragIndex, 1],
            [hoverIndex, 0, columns[dragIndex]],
          ],
        })
      );
    },
    [columns]
  );

  useEffect(() => {
    console.log(size);
    const col = apportionWidth(initialData, columnSpec, size.width);
    setColumns(col);
  }, [initialData, size]);

  if (data.length === 0) return null;

  // Change management
  const handleUndo = () => {
    setData(initialData);
  };
  const handleSubmit = () => {
    //push method for sending data back to api
    if (data.length === 0) {
      return null;
    }
    setData(data);
  };

  function onCellsChanged(changes) {
    /** Cell change function that uses immutability-helper */
    const spec = {};
    console.log(changes);
    changes.forEach(({ cell, row, col, value }) => {
      // Get the key that should be used to assign the value
      const { key } = columns[col];
      console.log(key);
      // Substitute empty strings for nulls
      const $set = value == "" ? null : value;

      spec[row] = {
        ...(spec[row] || {}),
        [key]: { $set },
      };
    });
    console.log(spec);
    setData(update(data, spec));
  }

  /** Builds the properties for the cell */
  const buildCellProps = (
    value: any,
    row: number,
    key: string,
    col: number
  ) => {
    /** Need to turn off submit on click away event for cell */

    // Check if values is the same as the initial data key

    const isChanged = value != initialData[row][key];
    const readOnly = !(columns[col].editable ?? true);
    const className = classNames(
      { edited: isChanged, "read-only": readOnly },
      "cell",
      "nowrap",
      "clip"
    );
    return { value, className, readOnly };
  };

  /** We now build cell properties in the render function, rather than storing
      them using a precomputed useEffect hook. We decide what cells have changed using
      a direct comparison with the equivalent value of initialData. (That's the
      power of immutable data.)

      This is where the Components should be attached.
      */

  const cellData = data.map(
    (obj, row) =>
      // Object is the row object for the sample, Row# is the row that it is
      columns.map(({ key }, col) => buildCellProps(obj[key], row, key, col))
    //key is name of column
  );

  return h(DataSheetProvider, { columns, reorderColumns }, [
    <div className={styles["data-sheet"]}>
      <SheetToolbar
        onSubmit={handleSubmit}
        onUndo={handleUndo}
        hasChanges={initialData != data}
      />
      {h("div.sheet", { ref }, [
        <VirtualizedSheet
          data={cellData}
          valueRenderer={(cell) => `${cell.value ?? ""}`}
          sheetRenderer={Sheet}
          rowRenderer={Row}
          onCellsChanged={onCellsChanged}
          width={size?.width}
          // dataEditor={dataEditorComponents}
        />,
      ])}
    </div>,
  ]);
}

function DataSheetPage(props) {
  return h(Frame, { id: "dataSheet" }, h(DataSheet, props));
}

export default DataSheetPage;
