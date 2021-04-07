import h from "@macrostrat/hyper"
import { Card } from "@blueprintjs/core"
import "./module.styl"

export function TermCard(props) {
  const { data } = props;
  return h(Card, { className: "term-card", elevation: 0 }, [
    h("div.row", [
      h("h4", data.id),
      h.if(data.authority != null)("p.authority", data.authority),
    ]),
    h.if(data.description != null)("p.description", data.description),
  ]);
}