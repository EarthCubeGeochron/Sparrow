/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from "react-hyperscript";
import { Button, Intent } from "@blueprintjs/core";

const nullIfError = (fn) =>
  function () {
    // Returns null if the function returns an
    // error...useful for creating React component trees
    try {
      return fn.apply(this, arguments);
    } catch (error) {
      return null;
    }
  };

const JSONToggle = ({ showJSON, onChange }) => [
  h(
    Button,
    {
      rightIcon: "list",
      minimal: true,
      key: "hide-json",
      intent: !showJSON ? Intent.PRIMARY : null,
      onClick() {
        return onChange({ showJSON: false });
      },
    },
    "Summary"
  ),
  h(
    Button,
    {
      rightIcon: "code",
      minimal: true,
      key: "show-json",
      intent: showJSON ? Intent.PRIMARY : null,
      onClick() {
        return onChange({ showJSON: true });
      },
    },
    "JSON"
  ),
];

export { nullIfError, JSONToggle };
