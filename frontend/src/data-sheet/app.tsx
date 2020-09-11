import * as React from "react";
import { useState, useEffect, useContext } from "react";
import { useAPIResult } from "@macrostrat/ui-components";
import { SheetHeader } from "./header";
import { VirtualizedSheet } from "./virtualized";
import { DataSheetContext, DataSheetProvider } from "./provider";
import update from "immutability-helper";
import h from "@macrostrat/hyper";
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

const Sheet = ({ className, children }) => {
  const { columns } = useContext(DataSheetContext);
  return (
    <table className={className} style={{ width: 1000 }}>
      <thead style={{ width: 1000 }}>
        <tr className="cell header" style={{ width: 1000 }}>
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
  { name: "Project", key: "project_name", width: 1000 / 2 },
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

  const onCellsChanged = (changes) => {
    /** Cell change function that uses immutability-helper */
    const spec = {};
    changes.forEach(({ cell, row, col, value }) => {
      // Get the key that should be used to assign the value
      const { key } = columns[col];
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

  const buildCellProps = (value: any, row: number, key: string) => {
    // Check if values is the same as the initial data key

    const isChanged = value != initialData[row][key];
    const className = isChanged ? "edited" : null;
    return { value, className };
  };

  /** We now build cell properties in the render function, rather than storing
      them using a precomputed useEffect hook. We decide what cells have changed using
      a direct comparison with the equivalent value of initialData. (That's the
      power of immutable data.) */
  const cellData = data.map((obj, row) =>
    columns.map(({ key }) => buildCellProps(obj[key], row, key))
  );
  console.log(cellData);

  const testComponent = () => {
    return h("button", { onClick: console.log("Hello Casey") }, ["Click This"]);
  };

  /**
   * Function to Add components to the grid data structure
   * current Structure:
   *   [[{value: "name"},{value: igsn},{value: public},{value: material},{value: Latitude},{value: Longitude},{value: Location Name},{value: Project Name},]]
   *  Need to add specific components like:
   *   [[{value: 'name', component: (<Component/>)}]]
   *
   * will return an array with components
   * indexs are 0 - 7
   */
  const [[...ele]] = cellData;
  var [, , , object] = ele;
  object = { ...object, Component: h(testComponent) };
  //console.log(ele);
  //console.log(object);
  const components = ["0", "1", "2", "3", "4", "5", "6", "7"];

  const testData = cellData.map((ele) => {
    const newList = [];
    // ele is an Array of 8 objects
    ele.map((ele, index) => {
      const newEle = { ...ele, component: components[index] };
      newList.push(newEle);
    });
    return newList;
  });
  console.log(testData);

  return (
    <DataSheetProvider columns={columns}>
      <div className={styles["data-sheet"]}>
        <SheetHeader
          onSubmit={handleSubmit}
          onUndo={handleUndo}
          hasChanges={initialData != data}
        ></SheetHeader>
        <div className="sheet">
          <VirtualizedSheet
            data={cellData}
            valueRenderer={(cell) => cell.value}
            sheetRenderer={Sheet}
            rowRenderer={Row}
            onCellsChanged={onCellsChanged}
          />
        </div>
      </div>
    </DataSheetProvider>
  );
}

export default DataSheet;
