import { useAPIv2Result } from "~/api-v2";
import { useState, useEffect } from "react";
import { DataSheetSuggest } from "./datasheet-suggest";
import { Suggest } from "@blueprintjs/select";
import h from "@macrostrat/hyper";

const url = "/api/v2/vocabulary/material";

export function DataSheetMaterialSuggest({
  defaultValue,
  onCellsChanged,
  onCommit,
  row,
  col,
  cell,
}) {
  const [materials, setMaterials] = useState([]);

  const init = useAPIv2Result(url, { has: "id" });

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
