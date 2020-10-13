import * as React from "react";
import { useState, useEffect } from "react";
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

const columnSpec = [
  { name: "Sample Name", key: "name", width: 300 },
  { name: "IGSN", key: "igsn", width: 50 },
  { name: "Public", key: "is_public", width: 50 },
  { name: "Material", key: "material", width: 50 },
  { name: "Latitude", key: "latitude", width: 50 },
  { name: "Longitude", key: "longitude", width: 50 },
  { name: "Location name", key: "location_name", width: 50 },
  { name: "Project", key: "project_name", width: 50 },
];

function unwrapSampleData(sampleData) {
  /** Unwrap samples from API response to a flattened version */
  const { geometry, ...rest } = sampleData;
  let longitude: number, latitude: number;
  if (geometry != null) {
    [longitude, latitude] = geometry?.coordinates;
  }
  return { longitude, latitude, ...rest };
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
    { all: true },
    unwrapResponse
  );

  useEffect(() => {
    // Set data to start with the value of the initial data
    if (initialData == null) return;
    setData(initialData);
  }, [initialData]);

  if (data.length === 0) {
    return null;
  }

  const columns = columnSpec;

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
    const className = classNames(
      { edited: isChanged },
      "cell",
      "nowrap",
      "clip"
    );
    return { value, className };
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

  return (
    <DataSheetProvider columns={columns}>
      <div className={styles["data-sheet"]}>
        <SheetToolbar
          onSubmit={handleSubmit}
          onUndo={handleUndo}
          hasChanges={initialData != data}
        />
        <div className="sheet">
          <VirtualizedSheet
            data={cellData}
            valueRenderer={(cell) => cell.value}
            sheetRenderer={Sheet}
            rowRenderer={Row}
            onCellsChanged={onCellsChanged}
            // dataEditor={dataEditorComponents}
          />
        </div>
      </div>
    </DataSheetProvider>
  );
}

function DataSheetPage(props) {
  return h(Frame, { id: "dataSheet" }, h(DataSheet, props));
}

export default DataSheetPage;
