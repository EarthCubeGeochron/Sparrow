import React, { useState, useEffect, useContext } from "react";
import TableUI from "./Components/Table/table";
import {
  EditableCell,
  EditableNumCell,
} from "./Components/EditableCell/EditableCell";
import {
  useAPIResult
} from "@macrostrat/ui-components";

const Table = function (props) {
  const [data, setData] = useState([]);
  const skipPageResetRef = React.useRef();

  const initialData = useAPIResult("/sample", { all: true });

  useEffect(() => {
    // Set the data back to the initial data
    if (initialData == null) return;
    const markers = initialData.filter((d) => d.geometry != null);
    const mutMarkers = markers.map((sample) => {
      const {
        geometry: {
          coordinates: [longitude, latitude],
        },
        ...rest
      } = sample;
      return { longitude, latitude, ...rest };
    });
    setData(mutMarkers);
  }, [initialData]);

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
};

export default Table;
