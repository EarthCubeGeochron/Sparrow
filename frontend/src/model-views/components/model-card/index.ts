import { Card, Button } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components/src/ext/router-links";
import { hyperStyled } from "@macrostrat/hyper";
import classNames from "classnames";
import { Link } from "react-router-dom";
//@ts-ignore
import styles from "./module.styl";
import React from "react";
import { useModelURL } from "~/util";

const h = hyperStyled(styles);

function RemoveButton({ onClick }) {
  return h(Button, {
    style: {
      position: "absolute",
      top: "0",
      right: "0",
      marginLeft: "5px",
    },
    icon: "small-cross",
    minimal: true,
    intent: "danger",
    onClick,
  });
}

export interface LinkedThroughModel {
  model: string;
  id: string;
}

interface ModelLinkCardProps {
  to: string;
  className?: string;
  children?: React.ReactNode;
  draggable?: boolean;
  styles: React.StyleHTMLAttributes<HTMLElement>;
  linkedThrough: LinkedThroughModel | null;
}

function LinkedThrough(props: { data: LinkedThroughModel }) {
  const { model, id } = props.data;
  return h("div.model-card-link", [
    "Linked through ",
    h(Link, { to: useModelURL(`/${model}/${id}`) }, `${model} ${id}`),
  ]);
}

export const ModelLinkCard = (props: ModelLinkCardProps) => {
  /** A model link card for administration pages */
  const {
    className,
    to,
    linkedThrough,
    isEditing = false,
    children,
    onMouseEnter,
    onMouseLeave,
    draggable = false,
    styles = {},
    onClick,
  } = props;

  const isLink = to != null;
  const indirect = linkedThrough != null;
  const component = isLink && !isEditing ? LinkCard : Card;

  return h("div.model-link-container", [
    h(
      component,
      {
        className: classNames(
          { "indirect-link": indirect },
          "model-card",
          className
        ),
        to,
        onMouseEnter,
        onMouseLeave,
        draggable,
        style: { position: "relative", ...styles },
      },
      [
        h.if(isEditing && linkedThrough == null)(RemoveButton, {
          onClick,
        }),
        children,
      ]
    ),
    h.if(linkedThrough != null)(LinkedThrough, { data: linkedThrough }),
  ]);
};
