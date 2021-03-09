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
import { MySwitch } from "./misscel";
import { useToggle } from "../map/components/APIResult";

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
  onChange;
  value;
  rightElement?;
  leftIcon?;
}

/**
 * Customizeable Text Input, DOES NOT Support validation, yet
 * @param label{string}: String that will apear on top of Input, generally the name of metadata
 * @param helperText{string}: Text that will appear below input, smaller text, example of valid input.
 * @param placeholder{string}: Optional, text that will appear in input field before typing
 * @param value: Value of the input field (changed by the onChange handler prop)
 * @param onChange: Function that updates some external state that changes the value prop passed
 * @param leftIcon: (Optional)A SVG icon that will appear in the left of the input field.
 * @param rightElement: (Optional)An icon, button or react element that can have additional actions. i.e dropdown menu
 */
export function MyTextInput(props) {
  return h("div", [
    h(FormGroup, { labelInfo: props.helperText, label: props.label }, [
      h(InputGroup, {
        id: props.label + "-input",
        placeholder: props.placeholder,
        value: props.value,
        onChange: props.onChange,
        intent: "primary",
        leftIcon: props.leftIcon,
        rightElement: props.rightElement,
      }),
    ]),
  ]);
}

interface MyInputNum {
  min?: number;
  max?: number;
  helperText?: string;
  placeholder?: string;
  label?: any;
  onChange: any;
  value: any;
  rightElement?: any;
  leftIcon?: any;
  disabled?: boolean;
}

/** Numeric Input that has intent validation
 *
 * @param label{string}: String that will apear on top of Input, generally the name of metadata
 * @param helperText{string}: Text that will appear below input, smaller text, example of valid input.
 * @param placeholder{string}: Optional, text that will appear in input field before typing
 * @param value: Value of the input field (changed by the onChange handler prop)
 * @param onChange: Function that updates some external state that changes the value prop passed
 * @param leftIcon: (Optional)A SVG icon that will appear in the left of the input field.
 * @param rightElement: (Optional)An icon, button or react element that can have additional actions. i.e dropdown menu
 * @param min {number}: The minimum value that can be accepted as a valid data type.
 * @param max {number}: The maximum value that can be accepted as a valid data type.
 *
 */
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
        h.if(!props.disabled)(NumericInput, {
          id: props.label + "-input",
          placeholder: props.placeholder,
          value: props.value,
          onValueChange: props.onChange,
          intent,
          leftIcon: props.leftIcon,
          rightElement: props.rightElement,
          allowNumericCharactersOnly: false,
          clampValueOnBlur: true,
          ...props,
        }),
      ]
    ),
  ]);
}
