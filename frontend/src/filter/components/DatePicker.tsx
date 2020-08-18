import * as React from "react";
import { useState } from "react";
import { DateRangeInput } from "@blueprintjs/datetime";
import { Card } from "@blueprintjs/core";

export function DatePicker() {
  return (
    <Card>
      <h5>Session Date: </h5>
      <DateRangeInput
        formatDate={(date) => date.toLocaleString()}
        parseDate={(str) => new Date(str)}
      />
    </Card>
  );
}
