import * as React from "react";
import { Button, Tooltip, Collapse, Card } from "@blueprintjs/core";
import { AgeSlideSelect, DatePicker, MultipleSelectFilter } from "./components";
import { useToggle } from "../map/components/APIResult";

const SampleFilter = () => {
  const [open, toggleOpen] = useToggle(false);
  const items = ["car", "horse", "duck", "goose"];

  return (
    <div>
      <Tooltip content="Choose Multiple Filters">
        <Button onClick={toggleOpen} icon="filter"></Button>
      </Tooltip>
      <Collapse isOpen={open}>
        <AgeSlideSelect />
        <DatePicker />
        <MultipleSelectFilter text="Material :" />
        <MultipleSelectFilter text="Geologic Formation :" />
        <MultipleSelectFilter text="Geologic Time Period :" />
      </Collapse>
    </div>
  );
};

export { SampleFilter };
