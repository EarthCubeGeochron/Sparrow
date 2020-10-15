import h from "@macrostrat/hyper";
import {
  MapSelector,
  MaterialSuggest,
  DoiSuggest,
} from "./sheet-enter-components";

const dataEditorComponents = ({ row, col, value, onCommit, cell }) => {
  const { key } = columns[col];
  const components = {
    name: h("div", [value]),
    igsn: h("div", [value]),
    is_public: h("div", [value]),
    material: h(MaterialSuggest, {
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
    project_name: h(DoiSuggest, {
      defaultValue: value,
      onCellsChanged,
      onCommit,
      row: row,
      col: col,
      cell: cell,
    }),
  };
  return components[key];
};
