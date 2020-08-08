import React, { useState, useEffect, useContext } from "react";
import { List, Grid, AutoSizer } from "react-virtualized";
import VirDataSheet from "./vDataSheet";
import ReactDataSheet from "react-datasheet";
import "react-datasheet/lib/react-datasheet.css";
import "./datasheet.modules.css";
import { useAPIResult, SubmitDialog } from "./ui-components";
import { Button } from "@blueprintjs/core";
import { DataSheetContext, DataSheetProvider } from "./provider";

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

function DataSheet() {
  const [geo, setGeo] = useState([]);
  const [data, setData] = useState([]);
  const [iData, setiData] = useState([]);
  const [upData, setUpData] = useState([]);
  const initialData = useAPIResult("/sample", { all: true });

  console.log(upData);
  useEffect(() => {
    if (initialData == null) return;
    const mutMarker = initialData.map(unwrapSampleData);
    setGeo(mutMarker);
    const geoVal = mutMarker.map((obj) =>
      Object.values(obj).map((d) => ({ value: d }))
    );
    setData(geoVal);
    setiData(geoVal);
  }, [initialData]);

  if (geo.length === 0) {
    return null;
  }

  const columns = Object.keys(geo[0]).map((d) => {
    return { name: d };
  });

  const onClickHandleUndo = () => {
    setData(iData);
  };
  const onClickHandle = () => {
    //push method for sending data back to api
    if (upData.length === 0) {
      return null;
    }
    setData(upData);
  };

  const onCellsChanged = (changes) => {
    const grid1 = data.map((row) => [...row]);
    changes.forEach(({ cell, row, col, value }) => {
      grid1[row][col] = { ...grid1[row][col], value };
    });
    setUpData(grid1);
    const grid = data.map((row) => [...row]);
    changes.forEach(({ cell, row, col, value }) => {
      grid[row][col] = { ...grid[row][col], value };
      grid[row][col].className = "edited";
    });
    setData(grid);
  };

  var constant =
    "Are you sure you want to Submit? All changes will be final. If you do not want to submit, click Cancel.";

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
            data={data.slice(0, 100)}
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
