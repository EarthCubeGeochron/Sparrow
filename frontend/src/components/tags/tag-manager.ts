import { useState, useContext } from "react";
import { APIHelpers } from "@macrostrat/ui-components";
import { hyperStyled } from "@macrostrat/hyper";
import { Button, Collapse } from "@blueprintjs/core";
import { useAPIv2Result, APIV2Context } from "~/api-v2";
import { randomHexColor } from "../misscel";
import { TagBody } from "./tag-body";
import { tagBody } from "./types";
import { TagEditor } from "./tag-creator";
//@ts-ignore
import styles from "./module.styl";
import Axios from "axios";

const h = hyperStyled(styles);

function TagEditButtons(props) {
  const { id, onEdit, isEditing, onDelete } = props;

  const onClickEdit = () => {
    onEdit();
  };
  const onClickDelete = () => {
    onDelete(id);
  };

  return h("div", [
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
  const { buildURL } = APIHelpers(useContext(APIV2Context));
  const [isEditing, setIsEditing] = useState(false);

  const onSubmit = async (editedTag) => {
    console.log(editedTag);
    const route = buildURL(`/tags/tag/${tag.id}`);
    const res = await Axios.put(route, editedTag).then((response) => {
      return response;
    });
  };

  const onDelete = async () => {
    const route = buildURL(`/tags/tag/${tag.id}`);
    await Axios.delete(route);
  };

  if (!tag) return null;
  if (isEditing) {
    return h("div.tag-row", [
      h(TagEditor, {
        name: tag.name,
        description: tag.description,
        color: tag.color,
        onCancel: () => setIsEditing(false),
        onSubmit,
      }),
    ]);
  }
  return h("div.tag-row.non-edit", [
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
  ]);
}

function TagManager() {
  const data = useAPIv2Result("/api/v2/tags/tag?all=true");
  if (!data) return null;

  const total_count = data["total_count"];
  const tags = data["data"];

  return h("div", [
    h("div.new-tag-btn", [h(NewTag)]),
    h("div.tag-manager", [
      h("div.manager-header", [total_count + " Tags"]),
      tags.map((tag) => {
        return h(TagRow, { key: tag["id"], tag });
      }),
    ]),
  ]);
}

function NewTag() {
  const { buildURL } = APIHelpers(useContext(APIV2Context));
  const [open, setOpen] = useState(false);
  const initTag = {
    name: "",
    description: "",
    color: randomHexColor(),
  };

  const onSubmit = async (tag) => {
    const url = buildURL("/tags/tag");
    const res = await Axios.post(url, tag).then((response) => {
      return response;
    });
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
      "div.tag-manager",
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
