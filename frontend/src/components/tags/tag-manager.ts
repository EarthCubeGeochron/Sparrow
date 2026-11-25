import { useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Button, ButtonGroup, Card, Callout, Spinner } from "@blueprintjs/core";
import { usePostgRESTActions, usePostgRESTResult } from "~/api/postgrest";
import { randomHexColor } from "../misscel";
import { TagBody } from "./tag-body";
import { tagBody } from "./types";
import { TagEditor } from "./tag-creator";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function TagEditButtons(props) {
  const { id, onEdit, isEditing, onDelete } = props;

  const onClickEdit = () => {
    onEdit();
  };
  const onClickDelete = () => {
    onDelete(id);
  };

  return h(ButtonGroup, [
    h(Button, {
      icon: "edit",
      minimal: true,
      intent: "success",
      onClick: onClickEdit,
    }),
    h(Button, {
      icon: "trash",
      minimal: true,
      intent: "danger",
      onClick: onClickDelete,
    }),
  ]);
}

function TagRow(props) {
  const { tag, onCommit } = props;
  const { update, remove } = usePostgRESTActions();
  const [isEditing, setIsEditing] = useState(false);

  const onSubmit = async (editedTag) => {
    const { name, description, color } = editedTag;
    await update("/tag", { id: `eq.${tag.id}` }, { name, description, color });
    setIsEditing(false);
    onCommit();
  };

  const onDelete = async () => {
    await remove("/tag", { id: `eq.${tag.id}` });
    onCommit();
  };

  if (!tag) return null;
  if (isEditing) {
    return h(Card, [
      h(TagEditor, {
        name: tag.name,
        description: tag.description,
        color: tag.color,
        onCancel: () => setIsEditing(false),
        onSubmit,
      }),
    ]);
  }
  return h(
    Card,
    { className: "tag-row", style: { padding: "20px", marginBottom: "1px" } },
    [
      h(TagBody, {
        name: tag.name,
        description: tag.description,
        color: tag.color,
        id: tag.id,
      }),
      h("p", [tag.description]),
      h(TagEditButtons, {
        id: tag.id,
        onEdit: () => {
          setIsEditing(!isEditing);
        },
        isEditing,
        onDelete,
      }),
    ]
  );
}

function TagManager() {
  // Bumped after each write; remounting the list reads it again
  const [version, setVersion] = useState(0);
  const onCommit = () => setVersion((v) => v + 1);

  return h("div", [
    h("div.new-tag-btn", [h(NewTag, { onCommit })]),
    h(TagList, { key: version, onCommit }),
  ]);
}

function TagList({ onCommit }) {
  const tags = usePostgRESTResult("/tag", { order: "name" }, { all: true });
  if (tags == null) return h(Spinner);

  return h(Callout, [
    h("div.manager-header", [tags.length + " Tags"]),
    tags.map((tag) => {
      return h(TagRow, { key: tag["id"], tag, onCommit });
    }),
  ]);
}

function NewTag({ onCommit }) {
  const { insert } = usePostgRESTActions();
  const [open, setOpen] = useState(false);
  const initTag = {
    name: "",
    description: "",
    color: randomHexColor(),
  };

  const onSubmit = async (tag) => {
    const { name, description, color } = tag;
    await insert("/tag", { name, description, color });
    setOpen(false);
    onCommit();
  };
  const onCancel = () => {
    setOpen(!open);
  };

  return h("div", [
    h(
      Button,
      {
        intent: "success",
        onClick: () => setOpen(!open),
        style: { marginBottom: "10px" },
      },
      ["New Tag"]
    ),
    h.if(open)(
      Callout,
      { style: { padding: "15px", marginBottom: "10px", marginTop: "5px" } },
      [
        h(TagEditor, {
          name: initTag.name,
          description: initTag.description,
          color: initTag.color,
          onSubmit,
          onCancel,
        }),
      ]
    ),
  ]);
}

export { TagManager };
