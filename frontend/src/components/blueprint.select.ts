import { Suggest, MultiSelect } from "@blueprintjs/select";
import { MenuItem, Icon } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useEffect, useState } from "react";
import "./select.css";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function MySuggest(props) {
  const {
    items,
    onChange,
    onFilter = () => {},
    initialQuery,
    createNew = true
  } = props;
  const [selectedItem, setSelectedItem] = useState("");
  const [query, setQuery] = useState("");
  console.log(query);

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
    }
  }, [initialQuery]);

  const itemz = [...items];

  const itemRenderer = (item, itemProps) => {
    const isSelected = item == selectedItem;

    return h(MenuItem, {
      key: item,
      labelElement: h.if(isSelected)(Icon, { icon: "tick" }),
      intent: isSelected ? "primary" : null,
      text: item,
      onClick: itemProps.handleClick,
      active: isSelected ? "active" : itemProps.modifiers.active
    });
  };

  const onQueryChange = query => {
    onFilter(query);
  };

  const itemPredicate = (query, item) => {
    return item.toLowerCase().indexOf(query.toLowerCase()) >= 0;
  };

  const onItemSelect = item => {
    onChange(item);
    setSelectedItem(item);
  };

  const createNewItemRenderer = (query, itemProps) => {
    return h(MenuItem, {
      icon: "add",
      text: `Create ${query}`,
      onClick: () => onChange(query),
      intent: "success"
    });
  };

  const createNewItemFromQuery = query => {
    return query;
  };

  return h("div", [
    h(Suggest, {
      inputValueRenderer: item => item,
      items: itemz,
      popoverProps: {
        minimal: true,
        popoverClassName: "my-suggest"
      },
      query,
      onItemSelect,
      onQueryChange,
      itemRenderer,
      itemPredicate,
      selectedItem,
      createNewItemRenderer: createNew ? createNewItemRenderer : null,
      createNewItemFromQuery: createNew ? createNewItemFromQuery : null
    })
  ]);
}

/**
This component is a search bar with a drop down menu.
It can set filters or fill forms
*/

export function MultipleSelectFilter({ items, sendQuery }) {
  const [state, setState] = useState({
    //items: items,
    selectedItems: [],
    isItemSelected: false
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
      active: isSelected ? "active" : itemProps.modifiers.active
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
  const itemSelect = item => {
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
    state.selectedItems.map(item => {
      setState({
        ...state,
        selectedItems: state.selectedItems.filter(t => t !== item)
      });
    });
  };

  const tagRenderer = item => item;

  return h(MultiSelect, {
    noResults: h(MenuItem, { disabled: true, text: "No Results" }),
    fill: true,
    items: items,
    itemRenderer: itemRenderer,
    itemPredicate: filterItem,
    onItemSelect: itemSelect,
    tagRenderer: tagRenderer,
    tagInputProps: { onRemove: removeTag },
    selectedItems: state.selectedItems
  });
}
