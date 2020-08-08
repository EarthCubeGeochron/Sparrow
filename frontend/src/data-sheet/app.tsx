import React, { useState, useEffect, useContext } from "react";
import { List, Grid, AutoSizer } from "react-virtualized";
import VirDataSheet from "./vDataSheet";
import ReactDataSheet from "react-datasheet";
import "react-datasheet/lib/react-datasheet.css";
import "./datasheet.modules.css";
import { useAPIResult, SubmitDialog } from "./ui-components";
import { Button } from "@blueprintjs/core";
import { DataSheetContext, DataSheetProvider } from "./provider";
import update from "immutability-helper";

const Row = ({ row, children, className }) => {
  return (
    <tr>
      <td className="cell read-only">{row}</td>
      {children}
    </tr>
  );
};

const Sheet = ({ className, children }) => {
  const { columns } = useContext(DataSheetContext);
  console.log(columns);
  return (
    <table className={className}>
      <thead>
        <tr className="cell read-only">
          <th>Index</th>
          {columns.map((col) => (
            <th key={col.name}>{col.name}</th>
          ))}
        </tr>
      </thead>
      <tbody>{children}</tbody>
    </table>
  );
};

const columnData = [
  { name: "Sample Name", key: "name" },
  { name: "IGSN", key: "igsn" },
  { name: "Public", key: "is_public" },
  { name: "Material", key: "material" },
  { name: "Latitude", key: "latitude" },
  { name: "Longitude", key: "longitude" },
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

  const columns = Object.keys(data[0]).map((d) => {
    return { name: d };
  });

  const onClickHandleUndo = () => {
    setData(initialData);
  };
  const onClickHandle = () => {
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
      const key: string = columns[col].name;
      spec[row] = {
        ...(spec[row] || {}),
        [key]: { $set: value },
      };
    });
    console.log(spec);
    setData(update(data, spec));
  };

  var constant =
    "Are you sure you want to Submit? All changes will be final. If you do not want to submit, click Cancel.";

  const buildCellProps = (value: any, row: number, key: string) => {
    const isChanged = value != initialData[row][key];
    const className = isChanged ? "edited" : null;
    return { value, className };
  };

  /* Instead of storing the cell values in a pre-computed useEffect hook,
     we just compute cell values on-demand. We get whether the cell was
     edited by doing an == comparison on the data value */
  const cellData = data.map((obj, row) =>
    Object.entries(obj).map(([key, value]) => buildCellProps(value, row, key))
  );

  return (
    <DataSheetProvider columns={columns}>
      <div className="data-sheet">
        <div className="sheet-header">
          <h3 className="sheet-title">Sample metadata</h3>
          <SubmitDialog
            className="save-btn"
            divClass="sheet-header"
            onClick={onClickHandle}
            content={constant}
          ></SubmitDialog>
          <Button onClick={onClickHandleUndo}>Undo Changes</Button>
        </div>

        <div className="sheet">
          <ReactDataSheet
            data={cellData.slice(0, 100)}
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
