import React, { useState } from "react";
import h from "@macrostrat/hyper";
import { InputGroup } from "@blueprintjs/core";

export function SearchInput(props) {
  const { rightElement } = props;
  const [text, setText] = useState("");

  const handleChange = (e) => {
    setText(e.target.value);
  };

  return h(InputGroup, {
    leftIcon: "search",
    placeholder: "Search for anything...",
    value: text,
    onChange: handleChange,
    rightElement,
  });
}
