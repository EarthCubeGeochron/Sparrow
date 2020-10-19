import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { Spinner, Card } from "@blueprintjs/core";
import styles from "./module.styl";
const h = hyperStyled(styles);

function TermCard(props) {
  const { data } = props;
  return h(Card, { className: "term-card", elevation: 0 }, [
    h("div.row", [
      h("h4", data.id),
      h.if(data.authority != null)("p.authority", data.authority),
    ]),
    h.if(data.description != null)("p.description", data.description),
  ]);
}

function VocabularyList(props) {
  const { authority, exclude, local = false } = props;

  const params = useAPIv2Result("/vocabulary/parameter", {
    all: true,
    authority,
  });
  if (params == null) return h(Spinner);
  let { data } = params;
  if (exclude != null) data = data.filter((d) => d.authority != exclude);
  if (local)
    data = data.filter((d) => d.authority == null || d.authority == "WiscAr");

  return h("div.list-column", [
    h.if(authority != null)("h2", authority),
    h(
      "div.vocabulary-list",
      data.map((d) => h(TermCard, { data: d }))
    ),
  ]);
}

export function VocabularyPage() {
  return h("div.vocabulary-page", {}, [
    h(VocabularyList, { local: true }),
    h(VocabularyList, { authority: "Sparrow" }),
  ]);
}
