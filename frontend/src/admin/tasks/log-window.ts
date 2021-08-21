import { hyperStyled } from "@macrostrat/hyper";
import { useRef, useEffect } from "react";
import useResizeObserver from "use-resize-observer";
import { FixedSizeList as List } from "react-window";
import { parse } from "ansicolor";
import classNames from "classnames";

import styles from "./module.styl";
const h = hyperStyled(styles);

const Row = ({ data, index, style }) => {
  const lineno = index - 1;
  const txt = data[lineno] ?? "";
  const spans = parse(txt).spans;

  return h(
    "div.message",
    {
      style: style,
    },
    [
      h.if(lineno >= 0 && lineno < data.length)(
        "span.lineno.dark-gray",
        `${lineno + 1}`
      ),
      h(
        "span.message-text",
        spans.map((d) => {
          const { italic, bold, text, color, bgColor } = d;
          const bg = bgColor?.name != null ? `bg-${bgColor.name}` : null;
          const className = classNames(
            {
              italic,
              bold,
              dim: color?.dim,
              "bg-dim": bgColor?.dim,
            },
            color?.name,
            bg
          );
          return h("span", { className }, text);
        })
      ),
    ]
  );
};

export function LogWindow({ messages }) {
  const ref = useRef<List>();
  const {
    ref: containerRef,
    width = 1,
    height = 1,
  } = useResizeObserver<HTMLDivElement>();
  const extraLines = 2;
  useEffect(() => {
    ref.current?.scrollToItem(messages.length + extraLines);
  }, [messages.length]);

  return h(
    "div.log-window",
    { ref: containerRef },
    h(
      List,
      {
        ref,
        height,
        itemCount: messages.length + extraLines,
        itemSize: 18,
        itemData: messages,
        width,
        className: "message-history",
      },
      Row
    )
  );
}
