import * as React from "react";
import { Button, Tooltip, Collapse, Card, MenuItem } from "@blueprintjs/core";
import {
  AgeSlideSelect,
  DatePicker,
  MultipleSelectFilter,
  GeologicFormationSelector,
} from "./components";
import { useToggle, useAPIResult } from "../map/components/APIResult";

/**
 * This Functional Component is a filter template to be used on different
 * pages. Some of the filters may be hidden depending on what page the user
 * is on, (i.e. a location selector wouldn't be rendered on the MapPanel
 */
const SampleFilter = () => {
  const [open, toggleOpen] = useToggle(false);

  return (
    <div>
      <Tooltip content="Choose Multiple Filters">
        <Button onClick={toggleOpen} icon="filter"></Button>
      </Tooltip>
      <Collapse isOpen={open}>
        <Card>
          <AgeSlideSelect />
          <DatePicker />
          <GeologicFormationSelector />
          {/* <MultipleSelectFilter text="Material :" items={items} /> */}

          {/* <MultipleSelectFilter text="Geologic Time Period :" items={items} /> */}
        </Card>
      </Collapse>
    </div>
  );
};

export { SampleFilter };
