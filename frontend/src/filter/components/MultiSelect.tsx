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

  const itemRenderer = (item) => {
    return <MenuItem text={item}></MenuItem>;
  };

  const itemSelect = (item) => {
    let list = state.selectedItem;
    let newlist = list.concat(item);
    setState({ ...state, selectedItem: newlist });
    return item;
  };

  const tagRenderer = () => state.selectedItem;

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
            selectedItems={state.selectedItem}
          ></MultiSelect>
        </div>
      </div>
    </Card>
  );
}
