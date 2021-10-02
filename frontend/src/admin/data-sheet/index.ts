import { useState, useEffect, useRef, useContext, useCallback } from "react";
import { useAPIResult, APIHelpers } from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import update from "immutability-helper";
import { hyperStyled } from "@macrostrat/hyper";
import { Frame } from "~/frame";
import {
  DataSheetProvider,
  Row,
  useElementSize,
  apportionWidths,
  VirtualizedSheet,
  ColumnData,
} from "@earthdata/sheet/src";
import { SheetToolbar } from "./toolbar";
import classNames from "classnames";
import styles from "./module.styl";
import { combineLikeIds, addNecesaryFields } from "./util";
import { postData } from "./post";
import { DoiProjectButton } from "./sheet-enter-components/doi-button";
import { DataEditor } from "react-datasheet/lib";
import { join } from "path";
import { memo } from "react";
import { Button } from "@blueprintjs/core";
import { createSettingsContext } from "@macrostrat/ui-components";

const h = hyperStyled(styles);

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
  const { geometry, project_id, project_name, publication_id, doi, ...rest } =
    sampleData;
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

interface DataSheetSettings {}

const [DataSheetSettingsProvider, useSettings, useSettingsUpdater] =
  createSettingsContext<DataSheetSettings>({});

function ColumnTogglePanel() {
  return h("div.toggle-panel");
}

function SettingsPopup() {
  return h(Button, { icon: "cog" }, "Settings");
}

const valueRenderer = (cell) => `${cell.value ?? ""}`;

function DataSheet() {
  const [data, setData] = useState<SampleData[]>([]);
  //console.log(data);

  const columns = columnSpec;

  const [edits, setEdits] = useState([]);
  /**
   * For edits, what I could do is create an array of indexes based on the row number.
   * And at the end I can grab the whole row and send it to the backend.
   */

  const initialData = useAPIResult(
    "/datasheet/view",
    {},
    { unwrapResponse, context: APIV2Context }
  );

  useEffect(() => {
    // Set data to start with the value of the initial data
    if (initialData == null) return;
    setData(initialData);
  }, [initialData]);

  const ref = useRef();
  const size = useElementSize(ref);
  console.log("Size 2:", size);

  //const [columns, setDesiredWidth] = useState(columnSpec);

  const desiredWidths =
    initialData != null ? calculateWidths(initialData, columnSpec) : {};

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
    return {
      value,
      className,
      readOnly,
    };
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

  //console.log(size);
  return h(
    DataSheetSettingsProvider,
    { storageID: "datasheet" },
    h(
      DataSheetProvider,
      { columns, containerWidth: size?.width ?? 500, desiredWidths },
      h("div.data-sheet", [
        h(
          SheetToolbar,
          {
            onSubmit: handleSubmit,
            onUndo: handleUndo,
            hasChanges: initialData != data,
          },
          h("div.right-actions", null, h(SettingsPopup))
        ),
        h("div.sheet", { ref }, [
          h(VirtualizedSheet, {
            data: cellData,
            valueRenderer,
            rowRenderer: Row,
            onCellsChanged,
            width: size?.width ?? 500,
            dataEditor: DataEditor,
          }),
        ]),
      ])
    )
  );
}

/*
(props) =>
            props.col === 6
              ? h(DoiProjectButton, { data, ...props })
              : h(DataEditor, { ...props }),
        }
*/

function DataSheetPage(props) {
  return h(Frame, { id: "dataSheet" }, h(DataSheet, props));
}

export default DataSheetPage;
