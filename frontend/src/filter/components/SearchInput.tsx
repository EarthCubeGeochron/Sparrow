import React, { useState } from "react";
import h from "@macrostrat/hyper";
import { InputGroup, Button } from "@blueprintjs/core";

export function SearchInput(props) {
  const { dispatch } = props;
  const [search, setSearch] = useState("");
  const handleChange = (e) => {
    setSearch(e.target.value);
  };

  const onSubmit = (e) => {
    e.preventDefault();
    dispatch({ type: "set-search", search });
    setSearch("");
  };

  return h("form", { onSubmit }, [
    h(InputGroup, {
      leftElement: h(Button, {
        icon: "filter",
        onClick: () => dispatch({ type: "toggle-open" }),
        minimal: true,
      }),
      placeholder: "Search for anything...",
      value: search,
      onChange: handleChange,
      rightElement: h(Button, {
        icon: "search",
        onClick: onSubmit,
        minimal: true,
        type: "submit",
      }),
    }),
  ]);
}
