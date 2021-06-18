import { useState } from "react";
import { TagBody, tagBody } from "~/components";
import { Suggest } from "@blueprintjs/select";
import { Button, Popover, MenuDivider } from "@blueprintjs/core";
import { useAPIv2Result } from "~/api-v2";
import { hyperStyled } from "@macrostrat/hyper";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

interface tagContainer {
  tags: tagBody[];
  isEditing: boolean;
  onChange: (e) => void;
  onClickDelete: (e) => void;
}

export function TagContainer(props) {
  const { tags, isEditing, onChange, onClickDelete }: tagContainer = props;

  if (tags) {
    return h("div.tag-container", [
      tags.map((tag) => {
        const { name, description, color, id } = tag;
        return h(TagBody, {
          name,
          description,
          color,
          id,
          isEditing,
          onClickDelete,
        });
      }),
      h.if(isEditing)(
        Popover,
        {
          content: h(TagSelect, { tags, onChange }),
          position: "bottom",
          minimal: true,
        },
        [
          h(
            Button,
            {
              icon: "add",
              intent: "success",
              minimal: true,
            },
            ["Add a Tag"]
          ),
        ]
      ),
    ]);
  } else {
    return h("div");
  }
}

export function TagSelect(props) {
  const { tags, onChange }: tagContainer = props;

  // use the tags from tag container to show only tags that don't exist on model
  const allTags = useAPIv2Result("/tags/tag", { all: true });
  if (allTags == null) return null;

  const currentIds = tags.map((tag) => tag.id);

  const tagSet = allTags.data.filter((tag) => !currentIds.includes(tag.id));

  const itemRenderer = (item, itemProps) => {
    const { name, description, color, id } = item;
    return h(
      "div",
      {
        onClick: itemProps.handleClick,
        style: { marginBottom: "5px", cursor: "pointer" },
      },
      [
        h(TagBody, { name, description, color, id, disabled: true }),
        h(MenuDivider),
      ]
    );
  };

  const itemPredicate = (query, item) => {
    return item.name.toLowerCase().indexOf(query.toLowerCase()) >= 0;
  };

  const onItemSelect = (item) => {
    onChange(item);
  };

  return h("div", [
    h(Suggest, {
      inputValueRenderer: (item) => item.name,
      items: tagSet,
      popoverProps: {
        minimal: true,
        popoverClassName: "my-suggest",
      },
      onItemSelect,
      itemRenderer,
      itemPredicate,
      closeOnSelect: true,
    }),
  ]);
}
