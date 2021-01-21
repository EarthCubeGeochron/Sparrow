import { useState, useReducer, useEffect } from "react";
import { reducer } from "./reducers-filters";
import {
  Button,
  Tooltip,
  Card,
  Popover,
  Icon,
  Tag,
  Collapse,
} from "@blueprintjs/core";
import {
  AgeSlideSelect,
  DatePicker,
  DoiFilter,
  SearchInput,
  GeologicFormationSelector,
} from "./components";
import { useToggle, useAPIResult } from "../map/components/APIResult";
import { hyperStyled } from "@macrostrat/hyper";
import { EmabrgoSwitch } from "./components/Embargo";
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
      //h.if(!on_map)(MapSelector),
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

const CollapseableEntity = (props) => {
  const [open, setOpen] = useState(false);
  const { content } = props;

  const clickChange = () => {
    setOpen(!open);
  };

  return h("div", [
    h("div", { style: { display: "flex" } }, [
      h(Popover, { content, position: "bottom", minimal: true }, [
        h(Button, { icon: "filter", onClick: clickChange, minimal: true }),
      ]),
    ]),
  ]);
};

const TagContainer = (props) => {
  const [tags, setTags] = useState({});
  const { params, removeParam, createParams } = props;

  useEffect(() => {
    setTags(params);
  }, [params]);

  useEffect(() => {
    createParams(tags);
  }, [JSON.stringify(tags)]);

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
    public: "public",
  };

  if (Object.keys(tags).length != 0) {
    return h("div", [
      Object.entries(tags).map((entry) => {
        const [key, value] = entry;
        return h(Tag, { onRemove: () => handleRemove(key) }, [
          `${natLang[key]}`,
        ]);
      }),
    ]);
  }
  return null;
};

function AdminFilter(props) {
  // need a prop that grabs set to create params
  const { createParams, possibleFilters, listComponent, initParams } = props;

  const [params, dispatch] = useReducer(reducer, initParams);
  const [tags, setTags] = useState(params);
  const [filterOpen, setFilterOpen] = useState(false);

  const updateParams = (field, data) => {
    if (field == "date_range") {
      dispatch({ type: "date_range", payload: { dates: data } });
    }
    if (field == "public") {
      dispatch({ type: "public", payload: { embargoed: data } });
    }
    if (field == "doi_like") {
      dispatch({ type: "doi_like", payload: { doi_like: data } });
    }
    if (field == "geometry") {
      dispatch({ type: "geometry", payload: { geometry: data } });
    }
  };
  const removeParam = (key) => {
    dispatch({ type: "removeSingle", payload: { field: key } });
  };

  const onSubmit = () => {
    createParams(params);
    setTags(params);
    setFilterOpen(!filterOpen);
    urlSearchFromParams(params);
  };
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

  const Content = h("div", { style: { margin: "10px" } }, [
    h.if(possibleFilters.includes("public"))(EmabrgoSwitch, {
      updateEmbargoFilter: updateParams,
    }),
    h.if(possibleFilters.includes("date_range"))(DatePicker, {
      updateDateRange: updateParams,
    }),
    h.if(possibleFilters.includes("doi_like"))(DoiFilter, {
      updateDoi: updateParams,
    }),
    h.if(possibleFilters.includes("geometry"))(MapPolygon, {
      updateParams,
    }),
    h(SumbitFilterButton),
  ]);

  return h("div", { style: { position: "relative" } }, [
    h("div.listcomponent", [
      h(SearchInput, {
        rightElement: h(Button, {
          icon: "filter",
          onClick: () => setFilterOpen(!filterOpen),
          minimal: true,
        }),
      }),
      h(TagContainer, { params: tags, removeParam, createParams }),
    ]),
    filterOpen ? Content : listComponent,
  ]);
}

export { SampleFilter, AdminFilter };
