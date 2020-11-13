import { useAPIResult } from "@macrostrat/ui-components";
import { useState, useEffect } from "react";
import { DataSheetSuggest } from "./datasheet-suggest";
import h from "@macrostrat/hyper";

const url = "http://localhost:5002/api/v2/vocabulary/material";

export function MaterialSuggest({
  defaultValue,
  onCellsChanged,
  onCommit,
  row,
  col,
  cell,
}) {
  const [materials, setMaterials] = useState([]);

  const init = useAPIResult(url, { has: "id" });

  useEffect(() => {
    if (init) {
      const materialslist = init.data.map((obj) => obj.id);

      const matSet = new Set(materialslist);
      const arrayMat = [...matSet];
      setMaterials(arrayMat);
    }
  }, [init]);

  return h("div", [
    h(DataSheetSuggest, {
      items: materials.slice(0, 10),
      defaultValue,
      onCellsChanged,
      onCommit,
      row,
      col,
      cell,
      sendQuery: () => null,
    }),
  ]);
}
