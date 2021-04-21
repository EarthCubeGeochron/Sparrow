import h from "@macrostrat/hyper";
import { Card } from "@blueprintjs/core";
import "./module.styl";

export function CompositeTermCard(props) {
  const { data } = props;
  const { members, ...rest } = data;
  return h(Card, { className: "term-card composite" }, [
    h(CardContent, rest),
    members.map((d) =>
      h("div.sub-term", [
        h.if(d.list ?? false)("p.modifier", "List of"),
        h(TermCard, { data: d }),
      ])
    ),
  ]);
}

function CardContent(props) {
  const { authority, id, description } = props;
  return h("div.card-header", [
    h("div.row", [
      h("h4", id),
      h.if(authority != null)("p.authority", authority),
    ]),
    h.if(description != null)("p.description", description),
  ]);
}

export function TermCard(props) {
  const { data } = props;
  if (data.members != null) {
    return h(CompositeTermCard, { data });
  }

  return h(
    Card,
    { className: "term-card", elevation: 0 },
    h(CardContent, data)
  );
}
