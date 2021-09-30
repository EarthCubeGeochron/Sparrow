import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { Divider } from "@blueprintjs/core";
//@ts-ignore
import styles from "./module.styl";
import ReactJson from "react-json-view";
import { TreeProps } from "./index";

const h = hyperStyled(styles);

export function JsonTree({
  defaultCollapsed,
  onSelect = () => {},
  fieldName = "",
  link = null,
  json = {},
  ...rest
}: TreeProps) {
  const data = useAPIv2Result(
    link,
    {},
    {
      unwrapResponse: res => {
        if (res.fields) {
          return res.fields;
        }
      }
    }
  );
  if (!data) return h("div");

  let newJson = {};
  Object.entries(data).map(([key, value]) => {
    newJson = { ...newJson, ...value.example };
  });

  const onEdit = edit => {
    return true;
  };

  return h("div", [
    h("h3", ["Example JSON for ", fieldName]),
    h("p", ["Edit the fields and copy to your clipboard!"]),
    h(Divider),
    h(ReactJson, {
      src: json,
      name: fieldName,
      displayDataTypes: false,
      onEdit
    })
  ]);
}
