import React, { useState } from "react";
import h from "@macrostrat/hyper";
import { InputGroup } from "@blueprintjs/core";

export function SearchInput(props) {
  const { rightElement, updateParams, leftElement, text } = props;

  const handleChange = (e) => {
    updateParams("like", e.target.value);
  };

  return h("form", [
    h(InputGroup, {
      leftElement,
      placeholder: "Search for anything...",
      value: text,
      onChange: handleChange,
      rightElement,
    }),
  ]);
}
