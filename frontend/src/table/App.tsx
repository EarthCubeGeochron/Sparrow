import React, { useState, useEffect } from "react";
import TableUI from "./Components/Table/table";
import {
  EditableCell,
  EditableNumCell,
} from "./Components/EditableCell/EditableCell";

function Table() {
  const [data, setData] = useState([]);
  const skipPageResetRef = React.useRef();

  

  useEffect(() => {
    getMarkers();
  }, []);

  async function getMarkers() {
    const response = await fetch(
      "https://sparrow-data.org/labs/wiscar/api/v1/sample?all=1"
    );
    const mrkers = await response.json();
    const markers = mrkers.filter((d) => d.geometry != null);
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
    setData(mutMarker);
  }

  const updateMyData = (rowIndex, columnId, value) => {
    skipPageResetRef.current = true;
    setData((old) =>
      old.map((row, index) => {
        if (index === rowIndex) {
          return {
            ...old[rowIndex],
            [columnId]: value,
          };
        }
        return row;
      })
    );
  };
  React.useEffect(() => {
    skipPageResetRef.current = false;
  }, [data]);

  const columns = React.useMemo(
    () => [
      {
        Header: "Name",
        accessor: "name",
      },
      {
        Header: "Sparrow Id",
        accessor: "id",
      },

      {
        Header: "Longitude",
        accessor: "longitude",
      },
      {
        Header: "Latitude",
        accessor: "latitude",
      },

      {
        Header: "Material",
        accessor: "material",
      },
      {
        Header: "Project",
        accessor: "project_name",
      },
    ],
    []
  );
  let cell = [];
  const columns2 = React.useMemo(
    () => [
      {
        Header: "Name",
        accessor: "name",
        Cell: EditableCell,
      },
      {
        Header: "Sparrow Id",
        accessor: "id",
      },

      {
        Header: "Longitude",
        accessor: "longitude",
        Cell: EditableNumCell,
      },
      {
        Header: "Latitude",
        accessor: "latitude",
        Cell: EditableNumCell,
      },
      {
        Header: "Material",
        accessor: "material",
        Cell: EditableCell,
      },
      {
        Header: "Project",
        accessor: "project_name",
        Cell: EditableCell,
      },
    ],
    []
  );
  return (
    <div>
      <TableUI
        data={data}
        setData={setData}
        columns={columns}
        columns2={columns2}
        skipPageResetRef={skipPageResetRef}
        updateMyData={updateMyData}
      />
    </div>
  );
}

export default Table;
