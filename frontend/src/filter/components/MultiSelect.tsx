import * as React from "react";
import { Card } from "@blueprintjs/core";
import h from "@macrostrat/hyper";
import { useAPIResult } from "@macrostrat/ui-components";
import { MultipleSelectFilter } from "~/components";

export function GeologicFormationSelector() {
  const [searchText, setSearchText] = React.useState("b");
  const [stratNames, setStratNames] = React.useState([]);
  const MacGeoFormationUrl = `https://macrostrat.org/api/v2/defs/strat_names`;

  const geologicFormations = useAPIResult(MacGeoFormationUrl, {
    strat_name_like: searchText,
  });

  React.useEffect(() => {
    if (geologicFormations !== null) {
      setStratNames(
        geologicFormations.success.data
          .map((item) => item.strat_name)
          .slice(0, 10)
      );
    }
  }, [geologicFormations]);

  const searchBySelectQuery = (query) => {
    setSearchText(query);
  };
  return h(Card, [
    h("div", [
      h("h5", ["Geololgic Formation:"]),
      h(MultipleSelectFilter, {
        items: stratNames,
        sendQuery: searchBySelectQuery,
      }),
    ]),
  ]);
}
