import { hyperStyled } from "@macrostrat/hyper";
import { useRef, useEffect, useState, useCallback, useMemo } from "react";
import useResizeObserver from "use-resize-observer";
import { VariableSizeList as List } from "react-window";
import { parse, strip } from "ansicolor";
import classNames from "classnames";

import styles from "./module.styl";
const h = hyperStyled(styles);

const MessageText = ({ text = "" }) => {
  const { spans } = parse(text);
  return h(
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
  );
};

const Row = ({ data, index, style }) => {
  const lineno = index - 1;
  const text = data[lineno] ?? "";

  return h("div.message", { style }, [
    h.if(lineno >= 0 && lineno < data.length)(
      "span.lineno.dark-gray",
      `${lineno + 1}`
    ),
    h(MessageText, { text }),
  ]);
};

function MessageHistory({ messages, width, height, gutterWidth = 100 }) {
  const ref = useRef<List>();
  const extraLines = 2;
  useEffect(() => {
    ref.current?.scrollToItem(messages.length + extraLines);
  }, [messages.length]);

  const [charSize, setCharSize] = useState(null);
  const charsPerLine = Math.floor(
    (width - gutterWidth) / (charSize?.width ?? 8)
  );
  console.log(charSize, charsPerLine);

  const textMeasureRef = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    if (textMeasureRef.current == null) return;
    setCharSize({
      width: Math.max(textMeasureRef.current.clientWidth / 40, 8),
      height: textMeasureRef.current.clientHeight,
    });
  }, [textMeasureRef]);

  const nChars = useRef([]);
  nChars.current = useMemo(() => {
    if (messages.length == 0) return [];
    const currentLength = nChars.current.length;
    const nextMessages = messages.slice(currentLength, messages.length);
    const addedElements = nextMessages.map((m) => strip(m).length);
    console.log(addedElements, nChars.current);
    nChars.current?.push(...addedElements);
    return nChars.current;
  }, [messages.length]);

  const getItemSize = useCallback(
    (index) => {
      const lineHeight = charSize?.height ?? 18;
      const n = nChars.current[index - 1] ?? 0;
      const nLines = Math.max(Math.ceil(n / charsPerLine), 1);
      return lineHeight * nLines;
    },
    [charSize, charsPerLine]
  );

  if (charSize == null) {
    return h("span.text-measurer", { ref: textMeasureRef }, "A".repeat(40));
  }

  return h(
    List,
    {
      ref,
      height,
      itemCount: messages.length + extraLines,
      itemSize: getItemSize,
      itemData: messages,
      width,
      className: "message-history",
    },
    Row
  );
}

export function LogWindow({ messages }) {
  const ref = useRef<List>();
  const {
    ref: containerRef,
    width = 1,
    height = 1,
  } = useResizeObserver<HTMLDivElement>();

  return h(
    "div.log-window",
    { ref: containerRef },
    h(MessageHistory, { width, height, messages })
  );
}
