import * as React from "react";
import { useState } from "react";
import h from "@macrostrat/hyper";
import { Suggest } from "@blueprintjs/select";
import { Card, MenuItem, ITagProps, Icon } from "@blueprintjs/core";

/**
 * This component will be a select-like component from blueprint
 * as the user types it will display a list of the top corresponding matchs
 * this can be used for materials, lithologies, location names, etc
 *
 * /vocabulary_material for materials
 *
 *
 *
 */

interface Suggester {
  items: [];
}

function DataSheetSuggest({ items }: Suggester) {
  const [state, setState] = useState({
    selectedItem: [],
  });

  // Renders Each Item in Item as a MenuItem
  const itemRenderer = (item, itemProps) => {
    const isSelected = state.selectedItem.includes(item);
    return h(MenuItem, {
      labelElement: h.if(isSelected)(Icon, { icon: "tick" }),
      intent: isSelected ? "primary" : null,
      text: item,
      onClick: itemProps.handleClick,
      active: isSelected ? "active" : itemProps.modifiers.active,
    });
  };
  const itemSelect = (item) => {
    setState({ ...state, selectedItem: item });
  };

  const filterItem = (query, item) => {
    return item.toLowerCase().indexOf(query.toLowerCase()) >= 0;
  };
  return h(Suggest, {
    inputValueRenderer: (item) => item,
    itemRenderer: itemRenderer,
    items: items,
    onItemSelect: itemSelect,
    itemPredicate: filterItem,
  });
}

export { DataSheetSuggest };
