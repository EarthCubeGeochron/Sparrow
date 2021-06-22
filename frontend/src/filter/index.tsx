import { useState, useReducer, useEffect } from "react";
import { reducer } from "./reducers-filters";
import { Button, Tooltip, Card, Popover, Icon, Tag } from "@blueprintjs/core";
import {
  AgeSlideSelect,
  DatePicker,
  DoiFilter,
  SearchInput,
  GeologicFormationSelector,
  TagFilter
} from "./components";
import { useToggle } from "~/components";
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
      h(GeologicFormationSelector)
    ]);
  };

  return h("div", [
    h(
      Popover,
      {
        content: h(filterCard),
        minimal: true,
        position: "bottom"
      },
      [
        h(Tooltip, { content: "Choose Multiple Filters" }, [
          h(Button, { onClick: toggleOpen, minimal: true }, [
            h(Icon, { icon: "filter" })
          ])
        ])
      ]
    )
  ]);
}

const TagContainer = props => {
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

  const handleRemove = key => {
    removeParam(key);
    const newTags = objectFilter(tags, ([ke, value]) => ke != key);
    setTags(newTags);
    urlSearchFromParams(newTags);
  };

  const natLang = {
    geometry: "Map Location",
    date_range: "Date Range",
    doi_like: "doi",
    public: { true: "Public Only", false: "Private Only" }
  };

  if (Object.keys(tags).length != 0) {
    return h("div.tag-container", [
      Object.entries(tags).map(entry => {
        const [key, value] = entry;
        const name =
          key == "public"
            ? natLang[key][value]
            : key == "like"
            ? value
            : natLang[key];
        return h(
          Tag,
          { onRemove: () => handleRemove(key), className: "tag-individ" },
          [name]
        );
      })
    ]);
  }
  return null;
};

function AdminFilter(props) {
  // need a prop that grabs set to create params
  const {
    createParams,
    possibleFilters,
    listComponent,
    initParams,
    dropdown = false,
    addModelButton = null
  } = props;

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
    if (field == "like") {
      dispatch({ type: "like", payload: { like: data } });
    }
  };
  const removeParam = key => {
    dispatch({ type: "removeSingle", payload: { field: key } });
  };

  const onSubmit = () => {
    createParams(params);
    setTags(params);
    setFilterOpen(!filterOpen);
    urlSearchFromParams(params);
  };

  const onSearch = e => {
    e.preventDefault();
    createParams(params);
    setTags(params);
    urlSearchFromParams(params);
  };
  const SumbitFilterButton = () => {
    return h(
      Button,
      {
        intent: "primary",
        onClick: onSubmit
      },
      ["Apply Filters"]
    );
  };
  const CancelFilterButton = () => {
    return h(
      Button,
      {
        intent: "danger",
        onClick: () => setFilterOpen(!filterOpen),
        style: { marginLeft: "10px" }
      },
      ["Cancel"]
    );
  };

  const Content = h(
    "div",
    {
      style: {
        marginTop: "15px"
      }
    },
    [
      h("div", [
        h.if(possibleFilters.includes("public"))(EmabrgoSwitch, {
          updateEmbargoFilter: updateParams
        }),
        h.if(possibleFilters.includes("tag"))(TagFilter, {
          updateParams
        }),
        h("div", [
          h.if(possibleFilters.includes("date_range"))(DatePicker, {
            updateDateRange: updateParams
          })
        ]),
        h.if(possibleFilters.includes("doi_like"))(DoiFilter, {
          updateDoi: updateParams
        }),
        h.if(possibleFilters.includes("geometry"))(MapPolygon, {
          updateParams
        }),
        h("div", { style: { margin: "10px", marginLeft: "0px" } }, [
          h(SumbitFilterButton),
          h(CancelFilterButton)
        ])
      ])
    ]
  );

  const leftElement = () => {
    const [open, setOpen] = useState(false);

    const changeOpen = () => {
      setOpen(!open);
    };

    return h("div", [
      h(
        Popover,
        {
          isOpen: open,
          content: Content,
          minimal: true,
          position: "bottom"
        },
        [
          h(Tooltip, { content: "Choose Multiple Filters" }, [
            h(Button, { minimal: true, onClick: changeOpen }, [
              h(Icon, { icon: "filter" })
            ])
          ])
        ]
      )
    ]);
  };

  // Allow for filters to also be a dropdown menu
  if (dropdown) {
    return Content;
  }

  return h("div", { style: { position: "relative" } }, [
    h("div.list-component", [
      h(SearchInput, {
        leftElement: h(Button, {
          icon: "filter",
          onClick: () => setFilterOpen(!filterOpen),
          minimal: true
        }),
        updateParams,
        rightElement: h(Button, {
          icon: "search",
          onClick: onSearch,
          minimal: true,
          type: "submit"
        }),
        text: params.like || ""
      }),
      h(TagContainer, { params: tags, removeParam, createParams }),
      addModelButton
    ]),
    filterOpen ? Content : listComponent
  ]);
}

export { SampleFilter, AdminFilter };
