import * as React from "react";
import { useState } from "react";
import h from "@macrostrat/hyper";
import { Suggest } from "@blueprintjs/select";
import { MenuItem, Icon, Menu, Tooltip } from "@blueprintjs/core";

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
  items?: [];
  onCellsChanged?: any;
  defaultValue?: any;
  onCommit?: any;
  row?: any;
  col?: any;
  cell?: any;
  sendQuery?: any;
}

function DataSheetSuggest({
  items,
  defaultValue,
  onCellsChanged,
  onCommit,
  row,
  col,
  cell,
  sendQuery,
}) {
  const [state, setState] = useState({
    selectedItem: [defaultValue],
  });

  console.log(items);
  // Renders Each Item in Item as a MenuItem
  const itemRenderer = (item, itemProps) => {
    const isSelected = state.selectedItem.includes(item);
    const renderItem = item.length > 20 ? item.slice(0, 19) + "..." : item;
    return h(Menu, [
      h(Tooltip, { content: item }, [
        h(MenuItem, {
          labelElement: h.if(isSelected)(Icon, { icon: "tick" }),
          intent: isSelected ? "primary" : null,
          text: renderItem,
          onClick: itemProps.handleClick,
          active: isSelected ? "active" : itemProps.modifiers.active,
        }),
      ]),
    ]);
  };

  const itemSelect = (item) => {
    setState({ ...state, selectedItem: item });
    const changes = [{ cell: cell, row: row, col: col, value: item }];
    console.log(changes);
    onCellsChanged(changes);
    onCommit(defaultValue);
  };

  const filterItem = (query, item) => {
    sendQuery(query);
    return item.toLowerCase().indexOf(query.toLowerCase()) >= 0;
  };
  const itemz = items.length > 50 ? items.slice(0, 50) : items;
  const newItems = itemz.concat(defaultValue);

  return h(Suggest, {
    inputValueRenderer: (item) => item,
    itemRenderer: itemRenderer,
    items: defaultValue ? newItems : itemz,
    onItemSelect: itemSelect,
    itemPredicate: filterItem,
    createNewItemFromQuery: (query) => query,
  });
}

export { DataSheetSuggest };
