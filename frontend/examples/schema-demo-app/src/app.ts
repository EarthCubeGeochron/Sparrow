import { TermCard, CompositeTermCard } from "@earthdata/schema-linker";
import h from "@macrostrat/hyper";
import d1 from "./lab-data.yaml";
import d2 from "./output-data.yaml";
import "@blueprintjs/core/lib/css/blueprint.css";
import "./main.styl";
import LinksDemo from "./links-demo";

function TermList(props) {
  const { data, title, children } = props;
  return h("div.term-list", [
    h.if(title)("h2.term-list-title", title)
    h(
      "div.term-list-data",
      data.map((d) => h(TermCard, { data: d })),
      children
    ),
  ]);
}

export default function () {
  //return h(LinksDemo, { width: 800, height: 400 });
  return h("div.schema-linker-ui", [
    h(TermList, { data: d1, title: "Lab fields" }),
    h("div.workspace", [
      h("h2", "Workspace"),
      h(LinksDemo, { width: 800, height: 500 })
    ])
    h(TermList, { data: d2, title: "Output schemas"}),
  ]);
}
