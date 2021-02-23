import { Suggest } from "@blueprintjs/select";
import { MenuItem, Icon } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useState, useContext, useEffect } from "react";
import "./test.css";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function MySuggest(props) {
  const { items, onChange, onFilter } = props;
  const [selectedItem, setSelectedItem] = useState("");

  const itemz = [...items];

  const itemRenderer = (item, itemProps) => {
    const isSelected = item == selectedItem;

    return h(MenuItem, {
      key: item,
      labelElement: h.if(isSelected)(Icon, { icon: "tick" }),
      intent: isSelected ? "primary" : null,
      text: item,
      onClick: itemProps.handleClick,
      active: isSelected ? "active" : itemProps.modifiers.active,
    });
  };

  const itemPredicate = (query, item) => {
    onFilter(query);
    return item.toLowerCase().indexOf(query.toLowerCase()) >= 0;
  };

  const onItemSelect = (item) => {
    onChange(item);
    setSelectedItem(item);
  };

  const createNewItemRenderer = (query, itemProps) => {
    return h(MenuItem, {
      icon: "add",
      text: `Create ${query}`,
      onClick: () => onChange(query),
      intent: "success",
    });
  };

  const createNewItemFromQuery = (query) => {
    return query;
  };

  return h("div", [
    h(Suggest, {
      inputValueRenderer: (item) => item,
      items: itemz,
      popoverProps: {
        minimal: true,
        popoverClassName: "my-suggest",
      },
      onItemSelect,
      itemRenderer,
      itemPredicate,
      selectedItem,
      createNewItemRenderer,
      createNewItemFromQuery,
    }),
  ]);
}
