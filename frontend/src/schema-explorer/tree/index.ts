import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { Card, Button } from "@blueprintjs/core";
import { SchemaExplorerContext } from "../context";
import React, { useContext, useEffect } from "react";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

interface LabelProps {
  fieldName: string;
  description?: string;
  nullable?: boolean;
  required?: boolean;
  read_only?: boolean;
  type?: string;
  link?: string;
  onClick?: () => void;
}

function typeClassName(props) {
  const { type, nullable, read_only, required, link } = props;
  let opts = {
    String: "string",
    Decimal: "decimal",
    Integer: "integer",
    Boolean: "boolean",
    DateTime: "string",
    Geometry: "geom"
  };
  let className: string = "default";
  Object.entries(opts).map(([key, value], i) => {
    if (key == type) {
      className = value;
    } else if (read_only) {
      className = "read-only";
    } else if (link) {
      className = "type-schema";
    }
  });
  console.log(className);
  return className;
}

function TreeLegend() {
  return h(Card, { className: "legend-card" }, [
    h("h3", "Legend"),
    h("div.legend-field", [
      h("div.read-only", "Read-Only"),
      h("div.legend", ": handled automatically on import")
    ]),
    h("div.legend-field", [
      h("div.required", "*"),
      h("div.legend", ": required field to import model")
    ])
  ]);
}

function NodeLabel(props: LabelProps) {
  const { state, runAction } = useContext(SchemaExplorerContext);
  let type = props.type;
  let classname = typeClassName(props);
  if (props.required) {
    type += "*";
  }

  const onClick = () => {
    let model: string;
    Object.entries(state.possibleModels).map(([key, value], i) => {
      if (props.link.search(value) > -1) {
        console.log(key, value, props.link);
        model = key;
      }
    });
    runAction({ type: "switch-model", payload: { model: model } });
  };

  const Description = () => {
    return h("div.description", props.description);
  };
  if (props.link != null) {
    return h("div", [
      h("div", { className: "node-label" }, [
        h("h3", [props.fieldName]),
        h.if(props.type != null)(
          Button,
          {
            minimal: true,
            className: classname,
            onClick: () => onClick()
          },
          [type]
        )
      ]),
      h.if(props.description != null)(Description)
    ]);
  }

  return h("div", [
    h("div", { className: "node-label" }, [
      h("h3", [props.fieldName]),
      h.if(props.type != null)(`div.${classname}`, [type])
    ]),
    h(Description)
  ]);
}

interface TreeProps extends LabelProps {
  defaultCollapsed?: boolean;
  onSelect?: () => void;
}

interface TreeState {
  collapsed: boolean;
}

function Tree({
  defaultCollapsed = true,
  onSelect = () => {},
  fieldName = "",
  link = null,
  ...rest
}: TreeProps) {
  const [state, setState] = React.useState<TreeState>({
    collapsed: defaultCollapsed
  });

  useEffect(() => {
    setState({ collapsed: true });
  }, [fieldName]);

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

  const handleClick = () => {
    onSelect();
    let tempState = { ...state };
    tempState["collapsed"] = !tempState["collapsed"];
    setState(tempState);
  };

  let containerClassName = "tree-view_children";
  if (state.collapsed) {
    containerClassName += " tree-view_children-collapsed";
  }
  let iconName = state.collapsed ? "caret-right" : "caret-down";

  const arrow = () => {
    return h(Button, { icon: iconName, onClick: handleClick, minimal: true });
  };

  return h(Card, { className: `tree-view` }, [
    h("div", { className: "tree-view_item" }, [
      h.if(link != null)(arrow),
      h.if(link == null)("div.placeholder"),
      h(NodeLabel, {
        fieldName: fieldName,
        link,
        ...rest,
        onClick: handleClick
      })
    ]),
    h(`div.${containerClassName}`, [
      state.collapsed
        ? null
        : Object.entries(data).map(([key, value], i) => {
            let link_: string;
            if (value["link"]) {
              link_ = value["link"];
            }
            return h(Tree, {
              key: i,
              fieldName: key,
              link: link_,
              defaultCollapsed: true,
              ...value
            });
          })
    ])
  ]);
}

export { Tree, TreeProps, TreeLegend };
