import * as React from "react";
import { useState, useEffect, useRef, useCallback } from "react";
import { useAPIResult } from "@macrostrat/ui-components";
import update from "immutability-helper";
import h from "@macrostrat/hyper";
import { Frame } from "~/frame";
import {
  DataSheetProvider,
  Row,
  Sheet,
  useElementSize,
  apportionWidths,
  ColumnSpec,
} from "@earthdata/sheet/src/index.ts";
import { SheetToolbar } from "./toolbar";
import { VirtualizedSheet } from "./virtualized";
import classNames from "classnames";
import styles from "./module.styl";
import { combineLikeIds, addNecesaryFields } from "./util";
import { postData } from "./post";
import { DoiProjectButton } from "./sheet-enter-components/doi-button";
import { DataEditor } from "react-datasheet/lib";

const columnSpec: ColumnData[] = [
  { name: "Sample ID", key: "id", editable: false },
  { name: "Sample Name", key: "name" },
  { name: "Material", key: "material" },
  { name: "Longitude", key: "longitude" },
  { name: "Latitude", key: "latitude" },
  { name: "Publication ID", key: "publication_id", editable: false },
  { name: "DOI", key: "doi" },
  { name: "Project ID", key: "project_id", editable: false },
  { name: "Project", key: "project_name" },
];

function unwrapSampleData(sampleData) {
  /** Unwrap samples from API response to a flattened version */
  const {
    geometry,
    project_id,
    project_name,
    publication_id,
    doi,
    ...rest
  } = sampleData;
  let longitude: number, latitude: number;
  if (geometry != null) {
    [longitude, latitude] = geometry?.coordinates;
  }
  // const [proj_id] = project_id;
  // const [proj_name] = project_name;
  // const [pub_id] = publication_id;
  // const [DOI] = doi;
  return {
    longitude,
    latitude,
    project_id,
    project_name,
    publication_id,
    doi,
    ...rest,
  };
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
  //console.log(data);

  const [edits, setEdits] = useState([]);
  /**
   * For edits, what I could do is create an array of indexes based on the row number.
   * And at the end I can grab the whole row and send it to the backend.
   */

  const initialData = useAPIResult(
    "http://localhost:5002/api/v2/datasheet/view",
    {},
    unwrapResponse
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
    // If we don't have this we'll get an infinite loop
    if (initialData == null || initialData.length == 0) return;
    const desiredWidths = calculateWidths(data, columnSpec);
    const col = apportionWidths(columnSpec, desiredWidths, size.width);
    setColumns(col);
  }, [initialData, size]);

  if (data.length === 0) return null;

  // Change management
  const handleUndo = () => {
    setData(initialData);
    setEdits([]);
  };
  const handleSubmit = () => {
    //push method for sending data back to api
    if (data.length === 0) {
      return null;
    }
    setData(data);
    const post_data = BuildEdits();
    console.log(post_data);
    postData(post_data);
    setEdits([]);
  };

  function BuildEdits() {
    /** Grabs the edits from the data for POST.
     *
     * How can I group them by rows so I don't have to send a item per cell
     */

    const editsList = addNecesaryFields(edits, data);
    const finalEdits = combineLikeIds(editsList);
    return finalEdits;
  }

  function onCellsChanged(changes) {
    /** Cell change function that uses immutability-helper */
    const spec = {};
    // const edits = []; // something like what's happening with spec
    console.log(changes);
    changes.forEach(({ cell, row, col, value }) => {
      // Get the key that should be used to assign the value
      const { key } = columns[col];
      // Substitute empty strings for nulls
      const $set = value == "" ? null : value;
      // sets edits to the state index and the column name
      setEdits((prevEdits) => [{ row, key }, ...prevEdits]);
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
          dataEditor={(props) =>
            props.col === 6
              ? h(DoiProjectButton, { data, ...props })
              : h(DataEditor, { ...props })
          }
        />,
      ])}
    </div>,
  ]);
}

function DataSheetPage(props) {
  return h(Frame, { id: "dataSheet" }, h(DataSheet, props));
}

export default DataSheetPage;
