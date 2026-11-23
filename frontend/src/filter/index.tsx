import React, { useState, useReducer, useEffect } from "react";
import { FilterActions, reducer } from "./reducers-filters";
import { Button, Tooltip, Card, Popover, Icon, Tag } from "@blueprintjs/core";
import {
  AgeSlideSelect,
  DatePicker,
  DoiFilter,
  SearchInput,
  GeologicFormationSelector,
  TagFilter,
} from "./components";
import { useToggle } from "~/components";
import { hyperStyled } from "@macrostrat/hyper";
import { EmabrgoSwitch } from "./components/Embargo";
//@ts-ignore
import styles from "./module.styl";
import { MapPolygon } from "./components/MapSelector";
import { urlSearchFromParams } from "../components/infinite-scroll/infinite-api-view";

const h = hyperStyled(styles);

/**
 * This Functional Component is a filter template to be used on different
 * pages. Some of the filters may be hidden depending on what page the user
 * is on, (i.e. a location selector wouldn't be rendered on the MapPanel
 */
interface Filter {
  on_map?: boolean;
}

function SampleFilter({ on_map = false }: Filter) {
  const [open, toggleOpen] = useToggle(false);

  const filterCard = () => {
    return h(Card, [
      h(AgeSlideSelect),
      h(DatePicker, { updateDateRange: () => {} }),
      h(GeologicFormationSelector),
    ]);
  };

  return h("div", [
    h(
      Popover,
      {
        content: h(filterCard),
        minimal: true,
        position: "bottom",
      },
      [
        h(Tooltip, { content: "Choose Multiple Filters" }, [
          h(Button, { onClick: toggleOpen, minimal: true }, [
            h(Icon, { icon: "filter" }),
          ]),
        ]),
      ]
    ),
  ]);
}

const TagContainer = (props) => {
  const [tags, setTags] = useState({});
  const { params, removeParam } = props;

  useEffect(() => {
    setTags(params);
  }, [params]);

  function objectFilter(obj, predicate) {
    const newObject = Object.fromEntries(Object.entries(obj).filter(predicate));
    return newObject;
  }

  const handleRemove = (key) => {
    removeParam(key);
    const newTags = objectFilter(tags, ([ke, value]) => ke != key);
    setTags(newTags);
    urlSearchFromParams(newTags);
  };

  const natLang = {
    geometry: "Map Location",
    date_range: "Date Range",
    doi_like: "doi",
    public: { true: "Public Only", false: "Private Only" },
  };

  if (Object.keys(tags).length != 0) {
    return h("div.tag-container", [
      Object.entries(tags).map((entry) => {
        const [key, value] = entry;
        const name =
          key == "public"
            ? natLang[key][value]
            : key == "search" || key == "like"
            ? value
            : natLang[key];
        return h(
          Tag,
          { onRemove: () => handleRemove(key), className: "tag-individ" },
          [name]
        );
      }),
    ]);
  }
  return null;
};

interface AdminFilterPanelProps {
  runAction: (action: FilterActions) => void;
  possibleFilters: string[];
  onSubmit: () => void;
}

function AdminFilterPanel(props: AdminFilterPanelProps) {
  const { runAction, possibleFilters, onSubmit } = props;
  const SumbitFilterButton = () => {
    return h(
      Button,
      {
        intent: "primary",
        onClick: onSubmit,
      },
      ["Apply Filters"]
    );
  };
  const CancelFilterButton = () => {
    return h(
      Button,
      {
        intent: "danger",
        onClick: () => runAction({ type: "toggle-open" }),
        style: { marginLeft: "10px" },
      },
      ["Cancel"]
    );
  };

  return h(
    "div",
    {
      style: {
        marginTop: "15px",
      },
    },
    [
      h("div", [
        h.if(possibleFilters.includes("public"))(EmabrgoSwitch, {
          dispatch: runAction,
        }),
        h.if(possibleFilters.includes("tag"))(TagFilter, {
          dispatch: runAction,
        }),
        h("div", [
          h.if(possibleFilters.includes("date_range"))(DatePicker, {
            dispatch: runAction,
          }),
        ]),
        h.if(possibleFilters.includes("doi_like"))(DoiFilter, {
          dispatch: runAction,
        }),
        h.if(possibleFilters.includes("geometry"))(MapPolygon, {
          dispatch: runAction,
        }),
        h("div", { style: { margin: "10px", marginLeft: "0px" } }, [
          h(SumbitFilterButton),
          h(CancelFilterButton),
        ]),
      ]),
    ]
  );
}

export interface AdminFilterProps {
  children: React.ReactChildren;
  possibleFilters: string[];
  initParams: object;
}

function AdminFilter(props: AdminFilterProps) {
  const { possibleFilters } = props;

  const [filterState, dispatch] = useReducer(reducer, {
    params: { ...props.initParams },
    isOpen: false,
  });

  const runAction = (action: FilterActions) => {
    dispatch(action);
  };

  const removeParam = (key) => {
    dispatch({ type: "remove-filter", field: key });
  };

  const onSubmit = () => {
    dispatch({ type: "toggle-open" });
    urlSearchFromParams(filterState);
  };

  return h("div", { style: { position: "relative" } }, [
    h("div.list-component", [
      h(SearchInput, {
        dispatch,
      }),
      h(TagContainer, { params: filterState.params, removeParam }),
    ]),
    h.if(filterState.isOpen)(AdminFilterPanel, {
      onSubmit,
      runAction,
      possibleFilters,
    }),
    h.if(!filterState.isOpen)(React.Fragment, [
      React.Children.map(props.children, (child) =>
        React.cloneElement(child, { params: filterState.params })
      ),
    ]),
  ]);
}

export { SampleFilter, AdminFilter };
