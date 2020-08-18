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
    selectedItem: [],
    isItemSelected: false,
  });

  const itemRenderer = (item, { modifiers }) => {
    function ClickHandler(item) {
      let List = state.selectedItem;
      let newList = List.concat(item);
      setState({ ...state, selectedItem: newList });
    }
    if (!modifiers.matchesPredicate) {
      return null;
    }
    return (
      <MenuItem
        active={modifiers.active}
        text={item}
        onClick={(item) => ClickHandler(item)}
      ></MenuItem>
    );
  };

  const tagRenderer = (item) => item;

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
            onItemSelect={(item) => item}
            tagRenderer={tagRenderer}
            selectedItems={state.selectedItem}
          ></MultiSelect>
        </div>
      </div>
    </Card>
  );
}
