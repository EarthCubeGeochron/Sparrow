import React, { useState } from "react";
import h from "@macrostrat/hyper";
import { InputGroup } from "@blueprintjs/core";

export function SearchInput(props) {
  const { rightElement, updateParams, leftIcon, text } = props;

  const handleChange = (e) => {
    updateParams("like", e.target.value);
  };

  return h("form", [
    h(InputGroup, {
      leftIcon,
      placeholder: "Search for anything...",
      value: text,
      onChange: handleChange,
      rightElement,
    }),
  ]);
}
