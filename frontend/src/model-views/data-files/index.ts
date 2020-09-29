import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { Card } from "@blueprintjs/core";
import styles from "./module.styl";

const h = hyperStyled(styles);

function DataFileCard(props) {
  const { data: d } = props;
  return h(Card, { className: "data-file-card" }, [
    h("h2", d.basename),
    h("div.type", d.type),
  ]);
}

function DataFilesList(props) {
  return h("div.data-files-list");
}

function DataFilesPage(props) {
  const res =
    useAPIv2Result("/models/data_file", { per_page: 100 })?.data ?? [];
  return h(
    "div.data-files",
    res.map((d) => {
      return h(DataFileCard, { data: d });
    })
  );
}

export { DataFilesPage };
