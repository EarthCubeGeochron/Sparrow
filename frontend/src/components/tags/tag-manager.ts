import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { TagBody } from "./tag-body";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function TagManager() {
  const tag = {
    name: "example",
    description: "example description for tag",
    color: "#09FA05",
  };

  return h("div", [
    h(TagBody, {
      name: tag.name,
      description: tag.description,
      color: tag.color,
    }),
  ]);
}

export { TagManager };
