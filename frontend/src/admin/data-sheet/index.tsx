import * as React from "react";
import { useState, useEffect, useContext, useRef } from "react";
import { useAPIResult } from "@macrostrat/ui-components";
import update from "immutability-helper";
import h from "@macrostrat/hyper";

import { Frame } from "~/frame";
import { DataSheetContext, DataSheetProvider } from "./provider";
import { SheetHeader } from "./header";
import { VirtualizedSheet } from "./virtualized";
import { useElementHeight } from "./util";
import { DataSheetSuggest } from "./sheet-enter-components/datasheet-suggest";
import { MapSelector } from "./sheet-enter-components/map-selector";
import "./datasheet.css";
import styles from "./module.styl";

const Row = ({ row, children, className }) => {
  const { rowHeight } = useContext(DataSheetContext);
  return (
    <tr style={{ height: rowHeight }}>
      <td className="cell read-only">{row + 1}</td>
      {children}
    </tr>
  );
};

const Sheet = ({ className, children, width }) => {
  const { columns } = useContext(DataSheetContext);
  return (
    <table className={className} style={{ width }}>
      <thead style={{ width }}>
        <tr className="cell header" style={{ width }}>
          <td>Index</td>
          {columns.map((col) => (
            <td key={col.name} style={{ width: col.width }}>
              {col.name}
            </td>
          ))}
        </tr>
      </thead>
      <tbody>{children}</tbody>
    </table>
  );
};

const columnSpec = [
  { name: "Sample Name", key: "name", width: 1000 / 8 },
  { name: "IGSN", key: "igsn", width: 0 },
  { name: "Public", key: "is_public", width: 0 },
  { name: "Material", key: "material", width: 1000 / 8 },
  { name: "Latitude", key: "latitude", width: 1000 / 8 },
  { name: "Longitude", key: "longitude", width: 1000 / 8 },
  { name: "Location name", key: "location_name", width: 1000 / 8 },
  { name: "Project", key: "project_name", width: null },
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

  const ref = useRef<HTMLDivElement>();
  const [height, width] = useElementHeight(ref) ?? [100, 20];

  useEffect(() => {
    // Set data to start with the value of the initial data
    if (initialData == null) return;
    setData(initialData);
  }, [initialData]);

  if (data.length === 0) {
    return null;
  }

  console.log(width);

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

  const onCellsChanged = (changes) => {
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
  };
  const MaterialList = ["Lava", "Porphriclastic Rocks"];

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
    const className = isChanged ? "edited" : null;
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
  console.log(cellData);

  const dataEditorComponents = ({ row, col, value, onCommit, cell }) => {
    const { key } = columns[col];
    const components = {
      name: null,
      igsn: null,
      is_public: null,
      material: h(DataSheetSuggest, {
        items: MaterialList,
        defaultValue: value,
        onCellsChanged,
        onCommit,
        row: row,
        col: col,
        cell: cell,
      }),
      latitude: h(MapSelector, {
        onCellsChanged,
        row,
        col,
        colTwo: col + 1,
      }),
      longitude: h(MapSelector, {
        onCellsChanged: onCommit,
        row,
        col,
        colTwo: col - 1,
      }),
      location_name: null,
      project_name: null,
    };
    return components[key];
  };

  return (
    <DataSheetProvider columns={columns}>
      <div className={styles["data-sheet"]}>
        <SheetHeader
          onSubmit={handleSubmit}
          onUndo={handleUndo}
          hasChanges={initialData != data}
        ></SheetHeader>
        <div className="sheet" ref={ref}>
          <VirtualizedSheet
            data={cellData}
            valueRenderer={(cell) => cell.value}
            sheetRenderer={Sheet}
            rowRenderer={Row}
            onCellsChanged={onCellsChanged}
            dataEditor={dataEditorComponents}
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
