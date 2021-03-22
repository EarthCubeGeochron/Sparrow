import { useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { AdminFilter } from "~/filter";
import {
  SampleAddList,
  PublicationAddList,
  ResearcherAddList,
  ProjectListComponent,
  SessionListComponent,
} from "../../../components/infinite-scroll/infinite-scroll";
import {
  EditProjNewPub,
  EditProjNewResearcher,
  EditProjNewSample,
} from "./index";
import { modelEditList } from "../../sample/new-sample";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export function SampleFilterList({ onClick }) {
  const possibleFilters = ["public", "geometry", "date_range"]; //needs to work with "doi_like"

  const [params, setParams] = useState({});

  const createParams = (params) => {
    for (let [key, value] of Object.entries(params)) {
      if (value == null) {
        delete params[key];
      }
    }
    setParams(params);
  };

  return h(AdminFilter, {
    addModelButton: h("div.add-button-top", [
      h(EditProjNewSample, { onSubmit: onClick }),
    ]),
    listComponent: h(SampleAddList, {
      params,
      componentProps: {
        link: false,
        onClick,
      },
    }),
    createParams,
    possibleFilters,
    initParams: params || {},
  });
}

export function PublicationFilterList({ onClick }) {
  const possibleFilters = ["date_range", "doi_like"];

  const [params, setParams] = useState({});

  const createParams = (params) => {
    for (let [key, value] of Object.entries(params)) {
      if (value == null) {
        delete params[key];
      }
    }
    setParams(params);
  };
  return h(AdminFilter, {
    addModelButton: h("div.add-button-top", [
      h(EditProjNewPub, { onSubmit: onClick }),
    ]),

    listComponent: h(PublicationAddList, {
      params,
      componentProps: {
        link: false,
        onClick,
      },
    }),
    createParams,
    possibleFilters,
    initParams: params || {},
  });
}

export function ResearcherFilterList({ onClick }) {
  const possibleFilters = [];
  const [params, setParams] = useState({});

  const createParams = (params) => {
    for (let [key, value] of Object.entries(params)) {
      if (value == null) {
        delete params[key];
      }
    }
    setParams(params);
  };
  return h(AdminFilter, {
    addModelButton: h("div.add-button-top", [
      h(EditProjNewResearcher, { onSubmit: onClick }),
    ]),
    listComponent: h(ResearcherAddList, {
      params,
      componentProps: {
        link: false,
        onClick,
      },
    }),
    createParams,
    possibleFilters,
    initParams: params || {},
  });
}

export function ProjectFilterList({ onClick }) {
  const possibleFilters = ["public", "geometry", "doi_like", "date_range"];
  const [params, setParams] = useState({});

  const createParams = (params) => {
    for (let [key, value] of Object.entries(params)) {
      if (value == null) {
        delete params[key];
      }
    }
    setParams(params);
  };
  return h(AdminFilter, {
    listComponent: h(ProjectListComponent, {
      params,
      componentProps: {
        link: false,
        onClick,
      },
    }),
    createParams,
    possibleFilters,
    initParams: params || {},
  });
}

export function SessionFilterList({ onClick }) {
  const possibleFilters = ["public", "date_range", "geometry"];

  const [params, setParams] = useState({});

  const createParams = (params) => {
    for (let [key, value] of Object.entries(params)) {
      if (value == null) {
        delete params[key];
      }
    }
    setParams(params);
  };

  return h(AdminFilter, {
    listComponent: h(SessionListComponent, {
      params,
      componentProps: {
        link: false,
        onClick,
      },
    }),
    createParams,
    possibleFilters,
    initParams: params || {},
  });
}

export function ModelAddFilterLists(props) {
  const { mainList = "div", listName, onClick } = props;

  return h("div", [
    h.if(listName === modelEditList.MAIN)(mainList),
    h.if(listName === modelEditList.PROJECT)(ProjectFilterList, { onClick }),
    h.if(listName === modelEditList.SAMPLE)(SampleFilterList, { onClick }),
    h.if(listName === modelEditList.SESSION)(SessionFilterList, { onClick }),
    h.if(listName === modelEditList.PUBLICATION)(PublicationFilterList, {
      onClick,
    }),
    h.if(listName === modelEditList.RESEARCHER)(ResearcherFilterList, {
      onClick,
    }),
  ]);
}
