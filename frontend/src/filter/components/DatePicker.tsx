import * as React from "react";
import { useState } from "react";
import { DateRangeInput } from "@blueprintjs/datetime";
import {
  Card,
  FormGroup,
  InputGroup,
  NumericInput,
  Pre,
} from "@blueprintjs/core";
import h from "@macrostrat/hyper";

/**
 * Component to Pick Dates
 *
 * Needs a Precision chooser
 * Year, Month, Date, Time
 * Different options for each
 *
 */
export function DatePicker() {
  return h(Card, [
    h("h5", ["Session Date: "]),
    h(DateRangeInput, {
      formatDate: (date) => date.toLocaleString(),
      parseDate: (str) => new Date(str),
    }),
  ]);
}
