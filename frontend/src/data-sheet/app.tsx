import React, {
  useState,
  useEffect,
  useContext,
  useLayoutEffect,
  useRef,
} from "react";
import { List, Grid, AutoSizer } from "react-virtualized";
import VirDataSheet from "./vDataSheet";
import ReactDataSheet from "react-datasheet";
import { useAPIResult } from "@macrostrat/ui-components";
import { SheetHeader } from "./header";
import { DataSheetContext, DataSheetProvider } from "./provider";
import update from "immutability-helper";

import "./datasheet.css";
import styles from "./module.styl";

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
  const onScroll = (evt) => {
    console.log(evt);
  };
  return (
    <table className={className} onScroll={onScroll}>
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

const columnSpec = [
  { name: "Sample Name", key: "name" },
  { name: "IGSN", key: "igsn" },
  { name: "Public", key: "is_public" },
  { name: "Material", key: "material" },
  { name: "Latitude", key: "latitude" },
  { name: "Longitude", key: "longitude" },
  { name: "Location name", key: "location_name" },
  { name: "Project", key: "project_name" },
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

// Should factor this into UI Components
function useElementHeight(ref: React.Ref<HTMLElement>): number | null {
  const [height, setHeight] = useState<number>(null);
  useLayoutEffect(() => {
    if (ref.current == null) return;
    const { height } = ref.current.getBoundingClientRect();
    setHeight(height);
  }, [ref.current]);
  return height;
}

function useScrollOffset(ref: React.Ref<HTMLElement>): number {
  const [offset, setOffset] = useState(0);
  useEffect(() => {
    ref.current?.addEventListener("scroll", (evt) => {
      setOffset(evt.target.scrollTop);
    });
  }, [ref.current]);
  return offset;
}

function VirtualizedSheet(props) {
  const { data, onCellsChanged } = props;
  const { rowHeight } = useContext(DataSheetContext);

  const ref = useRef<HTMLDivElement>();
  const height = useElementHeight(ref) ?? 100;
  const scrollOffset = useScrollOffset(ref);

  const scrollerHeight = data.length * rowHeight;
  const nRowsDisplayed = Math.round((height / rowHeight) * 1.2);

  return (
    <div ref={ref} className={styles["virtualized-sheet"]}>
      <div className={styles["ui"]}>Scroll offset: {scrollOffset}</div>
      <div
        className={styles["scroll-panel"]}
        style={{ height: scrollerHeight }}
      />
    </div>
  );

  // <ReactDataSheet
  //   data={cellData.slice(0, 100)}
  //   valueRenderer={(cell) => cell.value}
  //   sheetRenderer={Sheet}
  //   rowRenderer={Row}
  //   onCellsChanged={onCellsChanged}
  // />
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

  return (
    <DataSheetProvider columns={columns}>
      <div className={styles["data-sheet"]}>
        <SheetHeader
          onSubmit={handleSubmit}
          onUndo={handleUndo}
          hasChanges={initialData != data}
        ></SheetHeader>
        <div className="sheet">
          <VirtualizedSheet rowHeight={40} data={data} />
        </div>
      </div>
    </DataSheetProvider>
  );
}

export default DataSheet;
