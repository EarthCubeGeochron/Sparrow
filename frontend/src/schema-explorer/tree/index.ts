import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import {
  Card,
  Button,
  Spinner,
  Tooltip,
  Icon,
  Collapse
} from "@blueprintjs/core";
import { SchemaExplorerContext } from "../context";
import { Link } from "react-router-dom";
import React, { useContext, useEffect, useState } from "react";
//@ts-ignore
import styles from "./module.styl";
import ReactJson from "react-json-view";

const h = hyperStyled(styles);

interface LabelProps {
  fieldName: string;
  description?: string;
  nullable?: boolean;
  required?: boolean;
  collapsed?: boolean;
  read_only?: boolean;
  type?: string;
  link?: string;
  example?: object;
  onArrowClick?: () => void;
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

function Description(props: LabelProps) {
  return h("div.description", [
    h("div.des-items", props.description),
    h.if(props.read_only)("div.des-items", [
      h("div.read-only", [
        "This datatype is read-only and is handled on the backend"
      ])
    ]),
    h.if(props.required)("div.des-items", [
      h("div.required", ["* this field is required"])
    ]),
    h("div.des-items", [
      h(ReactJson, {
        name: "Example",
        displayDataTypes: false,
        displayObjectSize: false,
        src: props.example
      })
    ])
  ]);
}

/// TODO: Make more like blueprintjs. Specific icons per datatype
// specific icons for required, nullable, read_only etc. Easy for legend
function NodeLabel(props: LabelProps) {
  const { state, runAction } = useContext(SchemaExplorerContext);
  const [open, setOpen] = useState(false);

  const onInfoClick = e => {
    e.stopPropagation();
    setOpen(!open);
  };

  let type = props.type;
  let classname = typeClassName(props);
  if (props.required) {
    type += "*";
  }

  const searchModel = () => {
    let model: string;
    Object.entries(state.possibleModels).map(([key, value], i) => {
      if (props.link.search(value) > -1) {
        model = key;
      }
    });
    return model;
  };

  let iconName = props.collapsed ? "caret-right" : "caret-down";

  const Arrow = () => {
    return h(Icon, {
      icon: iconName
    });
  };

  const LinkButton = () => {
    return h.if(props.type != null)(
      Link,
      { to: `/admin/schema-explorer/${searchModel()}` },
      [
        h(
          Button,
          {
            minimal: true,
            className: classname
          },
          [type]
        )
      ]
    );
  };

  return h("div.node", [
    h("div.node-label", { onClick: props.onArrowClick }, [
      h("div.node-left", [
        props.link != null ? h(Arrow) : h("div.placeholder"),
        h("h4", [props.fieldName])
      ]),
      h("div.node-right", [
        h.if(props.type != null && props.link == null)(`div.${classname}`, [
          type
        ]),
        h.if(props.link != null)(LinkButton),
        h.if(props.description != null)("div.left-icon", [
          h(Button, {
            icon: "more",
            onClick: onInfoClick,
            minimal: true
          })
        ])
      ])
    ]),
    h(Collapse, { isOpen: open }, [h(Description, { ...props })])
  ]);
}

interface TreeProps extends LabelProps {
  json: object;
  defaultCollapsed?: boolean;
  onSelect?: () => void;
}

interface TreeState {
  collapsed: boolean;
}

function Tree({
  defaultCollapsed,
  onSelect = () => {},
  fieldName = "",
  link = null,
  json = {},
  ...rest
}: TreeProps) {
  const [state, setState] = React.useState<TreeState>({
    collapsed: defaultCollapsed
  });

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
  useEffect(() => {
    if (defaultCollapsed == null && data != null) {
      setState({ collapsed: false });
    }
  }, [fieldName, data]);

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

  return h("div", { className: `tree-view` }, [
    h("li", { className: "tree-view_item" }, [
      h(NodeLabel, {
        collapsed: state.collapsed,
        fieldName: fieldName,
        link,
        ...rest,
        onArrowClick: handleClick
      })
    ]),
    h(`div.${containerClassName}`, [
      state.collapsed || data == null
        ? null
        : Object.entries(data).map(([key, value], i) => {
            let link_: string;
            if (value["link"]) {
              link_ = value["link"];
            }
            let newJson = { ...json, ...value.example };
            //TODO: try tp build json object recursively
            console.log("new json", newJson);
            return h(Tree, {
              key: i,
              json: newJson,
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
