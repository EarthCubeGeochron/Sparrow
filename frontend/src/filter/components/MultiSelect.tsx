import * as React from "react";
import { useState } from "react";
import { Card, MenuItem, ITagProps, Icon } from "@blueprintjs/core";
import h from "@macrostrat/hyper";
import {
  MultiSelect,
  ItemPredicate,
  IMultiSelectProps,
} from "@blueprintjs/select";
import { useToggle } from "../../map/components/APIResult";
import { useAPIResult } from "@macrostrat/ui-components";
import axios from "axios";

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
    return h(MenuItem, {
      key: item,
      labelElement: h.if(isSelected)(Icon, { icon: "tick" }),
      intent: isSelected ? "primary" : null,
      text: item,
      onClick: itemProps.handleClick,
      active: isSelected ? "active" : itemProps.modifiers.active,
    });
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

  return h(Card, [
    h("div", { style: { display: "flex" } }, [
      h("h5", [text]),
      h("div", { style: { marginTop: 10, marginLeft: 10 } }, [
        h(MultiSelect, {
          noResults: h(MenuItem, { disabled: true, text: "No Results" }),
          fill: true,
          items: items,
          itemRenderer: itemRenderer,
          itemPredicate: filterItem,
          onItemSelect: itemSelect,
          tagRenderer: tagRenderer,
          tagInputProps: { onRemove: removeTag },
          selectedItems: state.selectedItems,
        }),
      ]),
    ]),
  ]);
}

export function GeologicFormationSelector() {
  const [searchText, setSearchText] = React.useState("b");
  const [stratNames, setStratNames] = React.useState([]);
  const MacGeoFormationUrl = `https://macrostrat.org/api/v2/defs/strat_names`;

  const geologicFormations = useAPIResult(MacGeoFormationUrl, {
    strat_name_like: searchText,
  });
  console.log(geologicFormations);

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
  return h(MultipleSelectFilter, {
    text: "Geologic Formation",
    items: stratNames,
    sendQuery: searchBySelectQuery,
  });
}

export function NoLocalSampleSelector() {
  const [markers, setMarkers] = useState([]);

  interface Sample {
    geometry: object;
    name: string;
  }

  const initialData = useAPIResult<Sample[]>("/sample", { all: true });
  React.useEffect(() => {
    // Set the data back to the initial data
    if (initialData !== null) {
      const markers = initialData.filter((d) => d.geometry == null);
      const names = markers.map((object) => {
        return object.name;
      });
      setMarkers(names);
    }
  }, [initialData]);

  return h(MultipleSelectFilter, {
    text: "Connect Location to Existing Sample",
    items: markers,
    sendQuery: () => null,
  });
}
