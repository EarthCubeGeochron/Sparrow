import { DateRangeInput } from "@blueprintjs/datetime";
import { Card } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import styles from "./module.styl";

const h = hyperStyled(styles);

/**
 * Component to Pick Dates
 *
 * Needs a Precision chooser
 * Year, Month, Date, Time
 * Different options for each
 *
 */
export function DatePicker(props) {
  const { updateDateRange } = props;

  const handleChange = (e) => {
    if (e[0] != null && e[1] != null) {
      const dates = e.map((date) => date.toISOString().split("T")[0]);
      updateDateRange("date_range", dates);
    }
  };

  return h("div.filter-card", [
    h(Card, [
      h("div", ["Session Date: "]),
      h(DateRangeInput, {
        formatDate: (date) => date.toLocaleString(),
        parseDate: (str) => new Date(str),
        onChange: handleChange,
        popoverProps: { position: "bottom-right" },
        minDate: new Date(1950, 1, 1),
      }),
    ]),
  ]);
}
