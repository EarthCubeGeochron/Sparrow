import * as React from "react";
import { useState } from "react";
import { RangeSlider, Card } from "@blueprintjs/core";
import { useToggle } from "../../map/components/APIResult";

export function AgeSlideSelect() {
  const [range, setRange] = useState([0, 4600]);

  const handleRangeChange = (range) => {
    setRange(range);
  };
  return (
    <Card>
      <h5>Sample Age (Ma): </h5>
      <RangeSlider
        stepSize={10}
        labelStepSize={600}
        max={4600}
        min={0}
        value={range}
        onChange={handleRangeChange}
      ></RangeSlider>
    </Card>
  );
}
