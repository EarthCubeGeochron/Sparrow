import h from "@macrostrat/hyper";
import { useAPIv2Result } from "../../api-v2";
import { Card } from "@blueprintjs/core";

function DataFilesList(props) {
  return h("div.data-files-list");
}

function DataFilesPage(props) {
  const res = useAPIv2Result("/models/data_file")?.data ?? [];
  return h(
    "div.data-files",
    res.map((d) => {
      return h(Card, [h("h2", d.basename), h("div.type", d.type)]);
    })
  );
}

export { DataFilesPage };
