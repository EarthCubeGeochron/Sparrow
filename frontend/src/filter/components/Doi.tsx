import { InputGroup, Card } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function DoiFilter(props) {
  const { dispatch } = props;

  const handleChange = (e) => {
    dispatch({ type: "set-doi-like", doi: e.target.value });
  };

  return h("div.filter-card", [
    h(Card, [
      h("div", ["Search for DOI:", h(InputGroup, { onChange: handleChange })]),
    ]),
  ]);
}
