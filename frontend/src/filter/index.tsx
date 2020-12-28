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
  //MapSelector,
} from "./components";
import { useToggle, useAPIResult } from "../map/components/APIResult";
import h from "@macrostrat/hyper";
import { EmabrgoSwitch } from "./components/Embargo";
import { SettingsApplicationsSharp } from "@material-ui/icons";

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
  const { content, params, removeParam } = props;

  const clickChange = () => {
    setOpen(!open);
  };

  return h("div", [
    h("div", { style: { display: "flex" } }, [
      h(Button, { icon: "filter", onClick: clickChange, minimal: true }),
      h(TagContainer, { params, removeParam }),
    ]),
    h(Collapse, { isOpen: open }, [content]),
  ]);
};

const TagContainer = (props) => {
  const [tags, setTags] = useState({});
  const { params, removeParam } = props;
  console.log(tags);

  //console.log(tags);
  useEffect(() => {
    setTags(params);
  }, [params]);

  function objectFilter(obj, predicate) {
    //const { obj, predicate } = props;
    const newObject = Object.fromEntries(Object.entries(obj).filter(predicate));
    return newObject;
  }

  const handleRemove = (key) => {
    removeParam(key);
    const newTags = objectFilter(tags, ([ke, value]) => ke != key);
    setTags(newTags);
  };

  console.log(Object.keys(tags).length);
  if (Object.keys(tags).length != 0) {
    return h("div", [
      Object.entries(tags).map((entry) => {
        const [key, value] = entry;
        return h(Tag, { onRemove: () => handleRemove(key) }, [
          `${key}: ${value}`,
        ]);
      }),
    ]);
  }
  return null;
};

/**
 *
 * Component that will sit at the top of every admin page infinite scroll.
 *
 * It will have a set of filters to choose from and an Apply button
 *
 * Once Apply button is clicked, a params object will created from the values selected
 * and a new get request will be issues. At least thats the idea
 */
function AdminFilter(props) {
  // need a prop that grabs set to create params
  const { createParams, possibleFilters } = props;

  const [params, dispatch] = useReducer(reducer, {});
  const [tags, setTags] = useState({});

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
  };
  const removeParam = (key) => {
    dispatch({ type: "removeSingle", payload: { field: key } });
  };

  const SumbitFilterButton = () => {
    const onSubmit = () => {
      createParams(params);
      setTags(params);
    };

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
    h.if(possibleFilters.includes("embargo"))(EmabrgoSwitch, {
      updateEmbargoFilter: updateParams,
    }),
    h.if(possibleFilters.includes("date_range"))(DatePicker, {
      updateDateRange: updateParams,
    }),
    h.if(possibleFilters.includes("doi_like"))(DoiFilter, {
      updateDoi: updateParams,
    }),
    h(SumbitFilterButton),
  ]);

  return h("div", [
    h(SearchInput),
    h(CollapseableEntity, { content: Content, params: tags, removeParam }),
  ]);
}

export { SampleFilter, AdminFilter };
