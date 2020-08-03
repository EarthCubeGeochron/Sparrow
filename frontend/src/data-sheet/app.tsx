import React, { useState, useEffect, useContext } from "react";
import { List, Grid, AutoSizer } from "react-virtualized";
import VirDataSheet from "./vDataSheet";
import ReactDataSheet from "react-datasheet";
import "react-datasheet/lib/react-datasheet.css";
import "./datasheet.modules.css";
import useAPIResult from "./ui-components";
import { Button } from "@blueprintjs/core";
import { AppToaster } from "../toaster";

const Row = ({ row, children, className }) => {
  return (
    <tr>
      <td className={className}>{row}</td>
      {children}
    </tr>
  );
};

const SheetRender = ({ className, columns, children }) => {
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

function DataSheet() {
  const [geo, setGeo] = useState([]);
  const [edited, setEdited] = useState(false);
  const [data, setData] = useState([]);
  const [iData, setiData] = useState([]);
  const [upData, setUpData] = useState([]);
  const initialData = useAPIResult("/sample", { all: true });

  console.log(upData);
  useEffect(() => {
    if (initialData == null) return;
    const markers = initialData.filter((d) => d.geometry != null);
    const mutMarker = markers.map((sample) => {
      const {
        geometry: {
          coordinates: [longitude, latitude],
        },
        ...rest
      } = sample;
      const mutSample = { longitude, latitude, ...rest };
      return mutSample;
    });
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
  const geoCol = geo.map((obj) => Object.keys(obj).map((d) => ({ name: d })));
  const columns2 = geoCol[0];

  const renderRow = (props) => {
    return (
      <Row
        className="cell read-only"
        row={props.row}
        children={props.children}
      ></Row>
    );
  };

  const renderSheet = (props) => {
    return (
      <SheetRender
        className={props.className}
        columns={columns2}
        children={props.children}
      ></SheetRender>
    );
  };

  const onClickHandleUndo = () => {
    setData(iData);
  };
  const onClickHandle = (changes) => {
    //push method for sending data back to api
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

  return (
    <div className="data-sheet">
      <div className="sheet-header">
        <h3 className="sheet-title">DataSheet for Editing</h3>
        <Button onClick={onClickHandle} className="save-btn">
          Submit Changes
        </Button>
        <Button onClick={onClickHandleUndo} className="save-btn">
          Undo Changes
        </Button>
      </div>

      <div className="sheet">
        <ReactDataSheet
          data={data.slice(0, 100)}
          valueRenderer={(cell) => cell.value}
          sheetRenderer={renderSheet}
          rowRenderer={renderRow}
          onCellsChanged={onCellsChanged}
        />
      </div>
    </div>
  );
}
export default DataSheet;
