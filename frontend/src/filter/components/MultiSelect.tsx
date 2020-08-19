import * as React from "react";
import { useState } from "react";
import { Card, MenuItem, ITagProps, Icon } from "@blueprintjs/core";
import {
  MultiSelect,
  ItemPredicate,
  IMultiSelectProps,
} from "@blueprintjs/select";
import { useToggle, useAPIResult } from "../../map/components/APIResult";

/**
This component is a search bar with a drop down menu.
It can set filters or fill forms
*/

export function MultipleSelectFilter({ text, items, sendQuery }) {
  const [state, setState] = useState({
    //items: items,
    selectedItems: [],
    isItemSelected: false,
  });
  //console.log(state.selectedItems);
  const itemRenderer = (item, itemProps) => {
    //console.log(itemProps);
    const isSelected = state.selectedItems.includes(item);
    return (
      <MenuItem
        labelElement={isSelected ? <Icon icon="tick" /> : null}
        intent={isSelected ? "primary" : null}
        text={item}
        onClick={itemProps.handleClick}
        active={isSelected ? "active" : itemProps.modifiers.active}
      ></MenuItem>
    );
  };

  const filterItem = (query, item) => {
    sendQuery(query);
    return item.toLowerCase().indexOf(query.toLowerCase()) >= 0;
  };

  // This function needs to click and add an Item if it hasn't been
  // clicked yet and needs to remove Item from list if it is already
  // checked. We could convert list to a Set and easily use the .delete()
  // function. Or use an index to remove from the list.
  const itemSelect = (item) => {
    if (state.selectedItems.includes(item)) {
      let itemSet = new Set(state.selectedItems);
      itemSet.delete(item);
      let newItemList = [...itemSet];
      setState({ ...state, selectedItems: newItemList });
    } else {
      let newlist = [...state.selectedItems, item];
      setState({ ...state, selectedItems: newlist });
      return item;
    }
  };

  // This function removes the item from the list of Selected items held in state
  const removeTag = () => {
    state.selectedItems.map((item) => {
      setState({
        ...state,
        selectedItems: state.selectedItems.filter((t) => t !== item),
      });
    });
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
            items={items}
            itemRenderer={itemRenderer}
            itemPredicate={filterItem}
            onItemSelect={itemSelect}
            tagRenderer={tagRenderer}
            tagInputProps={{ onRemove: removeTag }}
            selectedItems={state.selectedItems}
          ></MultiSelect>
        </div>
      </div>
    </Card>
  );
}

export function GeologicFormationSelector() {
  const [searchText, setSearchText] = React.useState("");
  const [stratNames, setStratNames] = React.useState([]);
  const MacGeoFormationUrl =
    "https://macrostrat.org/api/v2/defs/strat_names?strat_name_like=" +
    searchText;

  const geologicFormations = useAPIResult(MacGeoFormationUrl);
  //console.log(geologicFormations);

  React.useEffect(() => {
    if (geologicFormations !== null) {
      setStratNames(
        geologicFormations.success.data
          .map((item) => item.strat_name)
          .slice(0, 10)
      );
    }
  }, [geologicFormations]);

  const searchBySelectQuery = (query) => {
    setSearchText(query);
  };
  return (
    <MultipleSelectFilter
      text="Geologic Formation :"
      items={stratNames}
      sendQuery={searchBySelectQuery}
    />
  );
}
