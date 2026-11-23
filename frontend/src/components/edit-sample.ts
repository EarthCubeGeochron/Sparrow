import h from "@macrostrat/hyper";
import { FormGroup, InputGroup, NumericInput } from "@blueprintjs/core";

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
  minorStepSize: number;
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
 * @param minorStepSize {number}: Minimum stepsize for numeric precision
 *
 */
export function MyNumericInput(props: MyInputNum) {
  const { helperText, ...rest } = props;
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
          ...rest,
        }),
      ]
    ),
  ]);
}
