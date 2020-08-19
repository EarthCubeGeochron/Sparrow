import * as React from "react";
import { Button, Tooltip, Collapse, Card, MenuItem } from "@blueprintjs/core";
import { AgeSlideSelect, DatePicker, MultipleSelectFilter } from "./components";
import { useToggle, useAPIResult } from "../map/components/APIResult";

const SampleFilter = () => {
  const [open, toggleOpen] = useToggle(false);
  const items = ["car", "horse", "duck", "goose"];
  const [searchText, setSearchText] = React.useState("");
  const [stratNames, setStratNames] = React.useState([]);
  console.log(stratNames);

  const MacGeoFormationUrl =
    "https://macrostrat.org/api/v2/defs/strat_names?strat_name_like=" +
    searchText;

  const geologicFormations = useAPIResult(MacGeoFormationUrl);
  console.log(geologicFormations);

  React.useEffect(() => {
    if (geologicFormations !== null) {
      setStratNames(
        geologicFormations.success.data
          .map((item) => item.strat_name)
          .slice(0, 10)
      );
    }
  }, [geologicFormations]);

  // if (geologicFormations !== null) {
  //   const stratNames = geologicFormations.success.data
  //     .map((item) => item.strat_name)
  //     .slice(0, 10);
  //   console.log(stratNames);
  // }

  const searchBySelectQuery = (query) => {
    setSearchText(query);
  };
  return (
    <div>
      {geologicFormations !== null ? (
        <div>
          <Tooltip content="Choose Multiple Filters">
            <Button onClick={toggleOpen} icon="filter"></Button>
          </Tooltip>
          <Collapse isOpen={open}>
            <AgeSlideSelect />
            <DatePicker />
            {/* <MultipleSelectFilter text="Material :" items={items} /> */}
            <MultipleSelectFilter
              text="Geologic Formation :"
              items={stratNames}
              sendQuery={searchBySelectQuery}
            />
            {/* <MultipleSelectFilter text="Geologic Time Period :" items={items} /> */}
          </Collapse>
        </div>
      ) : null}
    </div>
  );
};

export { SampleFilter };
