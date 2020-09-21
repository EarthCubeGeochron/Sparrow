import * as React from "react";
import h from "@macrostrat/hyper";
import {
  Dialog,
  Button,
  Card,
  FormGroup,
  InputGroup,
  NumericInput,
} from "@blueprintjs/core";
import { useToggle } from "../map/components/APIResult";
import { NormalModuleReplacementPlugin } from "webpack";

/** Form for Editing an Existing Sample */

/**
 * Things to go on an Editing Metadata Form
 * Name
 * Location: coordinates, nearby?
 * Material: Tree?
 * Lithology: Javscript Graph?
 * Formation: Suggestions from MacroStrat
 * Session Date w/time precision
 *
 *
 */

// Need the time precision for a session
// Coordinates can be set by clicking a map
function EditSample() {
  const [open, toggleOpen] = useToggle(false);
  const [state, setState] = React.useState({
    coordinates: { lng: 0, lat: 0 },
    material: "",
    foramtion: "",
    notes: "",
    sessionDate: { year: 0, month: "", day: 0, min: 0, sec: 0 },
  });

  return h("div", [
    h(Button, { minimal: true, onClick: toggleOpen }, ["Edit Sample"]),
    h(
      Dialog,
      { isOpen: open, title: "Edit Sample Data", onClose: toggleOpen },
      [h(Card), [h("h3", ["Form for Editing Sample"])]]
    ),
  ]);
}

export default EditSample;

/** Form component that includes the FormGroup, InputGroup/NumericInput
 * Should have intent changes based on a set min and max value
 *
 * Form Vailidation for text based inputs?
 */

interface MyInput {
  helperText?: string;
  placeholder?: string;
  label?: string;
  onChange: any;
  value: any;
  rightElement?: any;
  leftIcon?: any;
}
export function MyTextInput(props: MyInput) {
  return h("div", [
    h(FormGroup, { labelInfo: props.helperText, label: props.label }),
    [
      h(InputGroup, {
        id: props.label + "-input",
        placeholder: props.placeholder,
        value: props.value,
        onChange: props.onChange,
        intent: "primary",
        leftIcon: props.leftIcon,
        rightElement: props.rightElement,
      }),
    ],
  ]);
}

interface MyInputNum {
  min?: number;
  max?: number;
  helperText?: string;
  placeholder?: string;
  label?: string;
  onChange: any;
  value: any;
  rightElement?: any;
  leftIcon?: any;
}

/** Numeric Input that has intent validation */
export function MyNumericInput(props: MyInputNum) {
  const intent =
    props.value < props.min || props.value > props.max ? "Danger" : null;
  return h("div", [
    h(
      FormGroup,
      {
        labelInfo: props.helperText,
        label: props.label,
        labelFor: props.label + "-input",
      },
      [
        h(NumericInput, {
          id: props.label + "-input",
          placeholder: props.placeholder,
          value: props.value,
          onValueChange: props.onChange,
          intent,
          leftIcon: props.leftIcon,
          rightElement: props.rightElement,
        }),
      ]
    ),
  ]);
}
