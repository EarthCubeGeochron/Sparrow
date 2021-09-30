import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { Button, Switch, Icon, Collapse } from "@blueprintjs/core";
import { SchemaExplorerContext } from "../context";
import { Link } from "react-router-dom";
import React, { useContext, useEffect, useState } from "react";
//@ts-ignore
import styles from "./module.styl";
export * from "./json-tree";
export * from "./tree-legend";
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
  parentData?: any;
  json_?: object;
  onArrowClick?: () => void;
  onChange?: (obj, arr) => void;
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

function Description(props: LabelProps) {
  const { parentData, fieldName } = props;
  const [checked, setChecked] = useState(false);
  let baseExample = parentData[fieldName].example[fieldName];
  let newJSON = checked ? baseExample : props.json_;
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
        name: false,
        displayDataTypes: false,
        displayObjectSize: false,
        src: props.example
      }),
      h.if(props.link != null)(
        Switch,
        {
          checked,
          onChange: () => {
            props.onChange(newJSON, props.fieldName);
            setChecked(!checked);
          }
        },
        ["Show in Schema"]
      )
    ])
  ]);
}

/// TODO: Make more like blueprintjs. Specific icons per datatype
// specific icons for required, nullable, read_only etc. Easy for legend
function NodeLabel(props: LabelProps) {
  const { state } = useContext(SchemaExplorerContext);
  const [open, setOpen] = useState(false);

  if (props.read_only) return null;

  const onInfoClick = e => {
    e.stopPropagation();
    setOpen(!open);
  };

  let type = props.type;
  let fieldName = props.fieldName;
  let classname = typeClassName(props);
  if (props.required) {
    type += "*";
  }

  const modelLink = () => {
    let model: string;
    Object.entries(state.possibleModels).map(([key, value], i) => {
      if (props.link.search(value) > -1) {
        model = key;
      }
    });
    return model;
  };

  const Arrow = () => {
    return h(Icon, {
      icon: props.collapsed ? "caret-right" : "caret-down"
    });
  };

  const LinkButton = () => {
    return h.if(props.type != null)(
      Link,
      {
        to: `/admin/schema-explorer/${modelLink()}`
      },
      [
        h(
          "div",
          {
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
        h("h4", [fieldName]),
        h.if(props.required)("div.required", "*")
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

function createJSON(data) {
  if (data == null) return null;
  let json = {};
  Object.entries(data).map(([key, value], i) => {
    json = { ...json, ...value.example };
  });
  return json;
}

interface TreeProps extends LabelProps {
  defaultCollapsed?: boolean;
  onSelect?: () => void;
  isRoot?: boolean;
  json?: object;
}

interface TreeState {
  collapsed: boolean;
}

function Tree({
  defaultCollapsed,
  onSelect = () => {},
  fieldName = "",
  link = null,
  parentData = null,
  isRoot = true,
  onChange,
  ...rest
}: TreeProps) {
  const [state, setState] = React.useState<TreeState>({
    collapsed: defaultCollapsed
  });

  const [json_, setJSON] = useState({});
  const [changing, setChanging] = useState(false);

  const onChildChange = (newJson, fieldName_) => {
    let j_ = { ...json_ };
    j_[fieldName_] = newJson;
    setJSON(j_);
    setChanging(!changing);
  };

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

  useEffect(() => {
    if (data != null) {
      setJSON(createJSON(data));
      setChanging(!changing);
    }
  }, [data, state.collapsed]);

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

  useEffect(() => {
    if (data != null && isRoot) {
      onChange(json_, fieldName);
    }
  }, [data, state.collapsed, changing]);

  return h("div", { className: "tree-view" }, [
    h("li", { className: "tree-view_item" }, [
      h(NodeLabel, {
        json_,
        collapsed: state.collapsed,
        fieldName: fieldName,
        link,
        onArrowClick: handleClick,
        onChange,
        parentData,
        ...rest
      })
    ]),
    h.if(!state.collapsed)(`div.${containerClassName}`, [
      data == null
        ? null
        : Object.entries(data).map(([key, value], i) => {
            let link_: string;
            if (value["link"]) {
              link_ = value["link"];
            }
            return h(Tree, {
              key: i,
              fieldName: key,
              isRoot: false,
              parentData: data,
              onChange: onChildChange,
              link: link_,
              defaultCollapsed: true,
              ...value
            });
          })
    ])
  ]);
}

export { Tree, TreeProps };
