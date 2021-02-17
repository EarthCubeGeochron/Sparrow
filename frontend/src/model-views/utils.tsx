import { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import hyper from "@macrostrat/hyper";
import styles from "./main.styl";
import { useModelURL } from "~/util";

const h = hyper.styled(styles);

export function ModelCard(props) {
  const { content, id, model, link = true, onClick = () => {} } = props;

  const [clicked, setClicked] = useState();

  useEffect(() => {
    const list = window.location.pathname.split("/");
    if (list.length > 3) {
      setClicked(list[3]); //list[3] will be the id
    }
  }, [window.location.pathname]);

  const to = useModelURL(`/${model}/${id}`);

  const classname = clicked
    ? clicked == `${id}`
      ? "model-card.clicked"
      : "model-card"
    : "model-card";
  if (link) {
    return h(Link, { to, style: { textDecoration: "none" } }, [
      h(`div.${classname}`, [content]),
    ]);
  } else {
    return h("div", [
      h(
        `div.${classname}`,
        {
          onClick,
        },
        [content]
      ),
    ]);
  }
}
