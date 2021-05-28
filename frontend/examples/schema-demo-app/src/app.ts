import { TermCard, CompositeTermCard } from "@earthdata/schema-linker";
import h from "@macrostrat/hyper";
import d1 from "./lab-data.yaml";
import d2 from "./output-data.yaml";
import vocab from "./vocabulary.yaml";
import { useState } from "react";
import {
  DarkModeButton,
  DarkModeProvider,
} from "@macrostrat/ui-components/src/dark-mode";
import { Navbar } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/popover2/lib/css/blueprint-popover2.css";
import { Menu, MenuItem, Button, HTMLSelect } from "@blueprintjs/core";
import { Popover2 } from "@blueprintjs/popover2";
import "./main.styl";
import LinksDemo from "./links-demo";

function TermList(props) {
  const { data, title, children } = props;
  return h("div.term-list", [
    h.if(title)("h2.term-list-title", title),
    h(
      "div.term-list-data",
      data.terms.map((d) => h(TermCard, { data: d })),
      children
    ),
  ]);
}

function SelectMenu({ items, activeItem, onSetItem, prefix = null }) {
  if (items == null) return null;
  const content = h(
    Menu,
    {},
    items.map((d) =>
      h(MenuItem, {
        onClick() {
          onSetItem(d);
        },
        text: d,
      })
    )
  );

  return h(
    Popover2,
    { content },
    h(Button, { minimal: true }, h([prefix, h("b", activeItem)]))
  );
}

const vocabularies = vocab.map((d) => d.name);

const externalVocabs = vocab.filter((d) => !(d.private ?? false));

export default function () {
  //return h(LinksDemo, { width: 800, height: 400 });
  const [activeVocabulary, setActiveVocabulary] = useState(externalVocabs[0]);

  return h(DarkModeProvider, { addBodyClasses: true }, [
    h("div.schema-linker-ui", [
      h(TermList, { data: vocab[0], title: "Lab fields" }),
      h("div.workspace", [
        h("div.navbar", [
          h("h2", "Vocabulary"),
          h(HTMLSelect, {
            options: externalVocabs.map((d) => d.name),
            value: activeVocabulary.name,
            onChange(event) {
              setActiveVocabulary(
                externalVocabs.find((d) => d.name == event.currentTarget.value)
              );
            },
          }),
          h("div.spacer"),
          h(DarkModeButton),
        ]),
        h(LinksDemo, { width: 800, height: 500, vocabulary: activeVocabulary }),
      ]),
      //h(TermList, { data: d2, title: "Output schemas" }),
    ]),
  ]);
}
