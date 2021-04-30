import { TermCard, CompositeTermCard } from "@earthdata/schema-linker";
import h from "@macrostrat/hyper";
import d1 from "./lab-data.yaml";
import d2 from "./output-data.yaml";
import "@blueprintjs/core/lib/css/blueprint.css";
import "./main.styl";

function TermList(props) {
  const { data, children } = props;
  return h("div.term-list", [
    data.map((d) => h(TermCard, { data: d })),
    children,
  ]);
}

export default function () {
  return h("div.schema-linker-ui", [
    h(TermList, { data: d1 }),
    h(TermList, { data: d2 }),
  ]);
}
