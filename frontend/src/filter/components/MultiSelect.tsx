import * as React from "react";
import { useState } from "react";
import { Card, MenuItem } from "@blueprintjs/core";
import { MultiSelect } from "@blueprintjs/select";

/**
This component is a search bar with a drop down menu.
It can set filters or fill forms
*/
export function MultipleSelectFilter({ text }) {
  const [state, setState] = useState({
    items: ["car", "horse", "duck", "goose"],
    selectedItems: [],
    isItemSelected: false,
  });

  const itemRenderer = (item, itemProps) => {
    console.log(itemProps);
    const isSelected = state.selectedItems.includes(item);
    return (
      <MenuItem
        text={item}
        onClick={itemProps.handleClick}
        active={isSelected}
      ></MenuItem>
    );
  };

  const itemSelect = (item) => {
    let newlist = [...state.selectedItems, item];
    setState({ ...state, selectedItems: newlist });
    return item;
  };

  const tagRenderer = () => state.selectedItems;

  return (
    <Card>
      <div style={{ display: "flex" }}>
        <h5>{text}</h5>
        <div style={{ marginTop: 10, marginLeft: 10 }}>
          <MultiSelect
            noResults={<MenuItem disabled={true} text="No results." />}
            fill={true}
            items={state.items}
            itemRenderer={itemRenderer}
            onItemSelect={itemSelect}
            tagRenderer={tagRenderer}
            selectedItems={state.selectedItems}
          ></MultiSelect>
        </div>
      </div>
    </Card>
  );
}
