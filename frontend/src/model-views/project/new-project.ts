import { hyperStyled } from "@macrostrat/hyper";
import { useReducer, useState, createContext, useContext } from "react";
import { Button, Dialog, Tooltip } from "@blueprintjs/core";
import { AddSampleCard } from "../sample/detail-card";
import { AdminPage } from "../../admin/AdminPage";
import { AdminFilter } from "../../filter";
import {
  SampleAddList,
  PublicationAddList,
  ResearcherAddList,
} from "../../admin/infinite-scroll";
import { APIHelpers } from "@macrostrat/ui-components";
import { ModelEditableText, EmbargoDatePick } from "./editor";
import {
  ProjectSamples,
  ProjectPublications,
  ProjectResearchers,
} from "./page";
import {
  NewProjectNewPub,
  NewProjNewSample,
  NewProjNewResearcher,
  AddCard,
  SampleAdd,
  PubAdd,
  ResearcherAdd,
} from "../new-model";
import { MinimalNavbar } from "~/components";
import { APIV2Context } from "../../api-v2";
import { Link } from "react-router-dom";
import { useModelURL } from "~/util/router";
import axios from "axios";
import styles from "./project-form.styl";

const h = hyperStyled(styles);

export const ProjectFormContext = createContext({});

function objectFilter(obj, predicate) {
  //const { obj, predicate } = props;
  const newObject = Object.fromEntries(Object.entries(obj).filter(predicate));
  return newObject;
}

const projectReducer = (state, action) => {
  switch (action.type) {
    case "embargo_date":
      return {
        ...state,
        embargo_date: action.payload.embargo_date,
      };
    case "name":
      return {
        ...state,
        name: action.payload.name,
      };
    case "description":
      return {
        ...state,
        description: action.payload.description,
      };
    case "tags":
      return {
        ...state,
        tags: action.payload.tags,
      };
    case "add_sample":
      const currentS = [...state.sample_collection];
      const newCol = [...currentS, ...action.payload.sample_collection];
      return {
        ...state,
        sample_collection: newCol,
      };
    case "remove_sample":
      const currentSa = [...state.sample_collection];
      const remove_id = action.payload.sample_id;
      const samples = currentSa.filter((el) => el.id != remove_id);
      return {
        ...state,
        sample_collection: samples,
      };
    case "add_pub":
      const currentP = [...state.publication_collection];
      const newColP = [...currentP, ...action.payload.publication_collection];
      return {
        ...state,
        publication_collection: newColP,
      };
    case "remove_pub":
      const currentPu = [...state.publication_collection];
      const removeP_id = action.payload.pub_id;
      const pubs = currentPu.filter((el) => el.id != removeP_id);
      return {
        ...state,
        publication_collection: pubs,
      };
    case "add_researcher":
      const currentR = [...state.researcher_collection];
      const newColR = [...currentR, ...action.payload.researcher_collection];
      return {
        ...state,
        researcher_collection: newColR,
      };
    case "remove_res":
      const currentRes = [...state.researcher_collection];
      const removeRes_id = action.payload.res_id;
      const researchers = currentRes.filter((el) => el.id != removeRes_id);
      return {
        ...state,
        researcher_collection: researchers,
      };
    case "filter-list":
      return {
        ...state,
        filter_list: action.payload.filter_list,
      };
    default:
      throw new Error("What does this mean?");
  }
};

/**
 * Form for creating a new Project
 *
 * Fields for entry:
 *      Name: String
 *      Descriptions: String
 *      Embargo Until?: Date Picker
 *      Tags: string
 *      Publication: Collection adder, need a filterer for adding existing pubs and making a new one
 *      Researcher: Collection, probably
 *      Samples: Collection, need filter for adding existing samples and making a new one
 *
 *
 * @param props
 */
export function NewProjectFormMain() {
  const [edit, setEdit] = useState(false);
  const { project, dispatch } = useContext(ProjectFormContext);
  console.log(project);
  const { buildURL } = APIHelpers(useContext(APIV2Context));

  async function postData() {
    const route = buildURL("/models/project", {});

    const projectPost = [
      {
        name: project.name,
        description: project.description,
        sample: project.sample_collection,
        publication: project.publication_collection,
        researcher: project.researcher_collection,
      },
    ];
    console.log(route);
    console.log(projectPost);

    const response = await axios.post(route, projectPost).then((response) => {
      return response;
    });
    const { data } = response;
    console.log(data);
  }

  const NewProjectNavBar = (props) => {
    return h(MinimalNavbar, { className: "project-editor-navbar" }, [
      h("h4", props.header),
      h(EmbargoDate),
    ]);
  };

  const ProjectDescription = () => {
    const [description, setDescription] = useState(project.description);
    const onConfirm = () => {
      dispatch({ type: "description", payload: { description } });
    };
    const onChange = (value) => {
      setDescription(value);
    };
    return h("div", [
      h(ModelEditableText, {
        is: "p",
        field: "description",
        placeholder: "Give your project a description...",
        editOn: true,
        onChange,
        value: description,
        multiline: true,
        onConfirm,
      }),
    ]);
  };

  const SampleAddProj = () => {
    const onClickDelete = (id) => {
      console.log(id);
      dispatch({ type: "remove_sample", payload: { sample_id: id } });
    };
    const onClickList = () => {
      dispatch({
        type: "filter-list",
        payload: { filter_list: "sample" },
      });
    };

    return h(SampleAdd, {
      onClickDelete,
      onClickList,
      data: project.sample_collection,
      rightElement: h(NewProjNewSample),
    });
  };

  // this should look like normal project page
  const PubAddProj = () => {
    const onClickDelete = (id) => {
      dispatch({ type: "remove_pub", payload: { pub_id: id } });
      console.log("Remove", id);
    };
    const onClickList = () => {
      dispatch({ type: "filter-list", payload: { filter_list: "pub" } });
    };

    return h(PubAdd, {
      data: project.publication_collection,
      onClickDelete,
      onClickList,
      rightElement: h(NewProjectNewPub),
    });
  };

  const ResearcherAddProj = () => {
    const onClickDelete = (id) => {
      dispatch({ type: "remove_res", payload: { res_id: id } });
      console.log(id);
    };
    const onClickList = () => {
      dispatch({ type: "filter-list", payload: { filter_list: "res" } });
    };
    return h(ResearcherAdd, {
      onClickDelete,
      onClickList,
      data: project.researcher_collection,
      rightElement: h(NewProjNewResearcher),
    });
  };

  const EmbargoDate = () => {
    const onChange = (date) => {
      dispatch({ type: "embargo_date", payload: { embargo_date: date } });
    };
    const embargo_date = project.embargo_date;
    return h("div", [h(EmbargoDatePick, { onChange, embargo_date })]);
  };

  const SubmitDialog = (props) => {
    const { open, changeOpen, goToProject } = props;

    const url = useModelURL(`/project`);
    return h(Dialog, { isOpen: open }, [
      h(Link, { to: url }, [
        h(Button, { intent: "success", onClick: goToProject }, [
          "Create New Project",
        ]),
      ]),
      h(Button, { intent: "danger", onClick: changeOpen }, ["Cancel"]),
    ]);
  };

  const SubmitButton = () => {
    const [open, setOpen] = useState(false);

    const changeOpen = () => {
      setOpen(!open);
    };

    const goToProject = () => {
      postData();
    };

    return h("div", [
      h(SubmitDialog, { open, changeOpen, goToProject }),
      h(
        Button,
        {
          onClick: changeOpen,
          intent: "primary",
        },
        ["Done"]
      ),
    ]);
  };

  const ProjectName = () => {
    const [name, setName] = useState(project.name); // This is to make it look like it's real time edi
    const onChange = (e) => {
      setName(e);
    };
    const onConfirm = () => {
      dispatch({ type: "name", payload: { name } });
    };
    return h(ModelEditableText, {
      is: "h3",
      field: "name",
      placeholder: "Name Your Project",
      id: "name-text",
      editOn: true,
      onChange,
      value: name,
      multiline: true,
      onConfirm,
    });
  };

  return h("div", [
    h(NewProjectNavBar, { header: "Create New Project" }),
    h("div", [h(ProjectName), h(ProjectDescription)]),
    h(ResearcherAddProj),
    h(PubAddProj),
    h(SampleAddProj),
    h(SubmitButton),
  ]);
}

export function SampleFilterList(props) {
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
    listComponent: h(SampleAddList, {
      params,
      componentProps: {
        link: false,
        context: ProjectFormContext,
      },
    }),
    createParams,
    possibleFilters,
    initParams: params || {},
  });
}

function PublicationFilterList(props) {
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
    listComponent: h(PublicationAddList, {
      params,
      componentProps: {
        link: false,
        context: ProjectFormContext,
      },
    }),
    createParams,
    possibleFilters,
    initParams: params || {},
  });
}

function ResearcherFilterList(props) {
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
    listComponent: h(ResearcherAddList, {
      params,
      componentProps: {
        link: false,
        context: ProjectFormContext,
      },
    }),
    createParams,
    possibleFilters,
    initParams: params || {},
  });
}

const ProjectEditListComponent = () => {
  const { project, dispatch } = useContext(ProjectFormContext);

  return h("div", [
    h.if(project.filter_list == "sample")(SampleFilterList),
    h.if(project.filter_list == "pub")(PublicationFilterList),
    h.if(project.filter_list == "res")(ResearcherFilterList),
  ]);
};

/**
 * Need ability to change the list component based on what editing component, specifically for collections
 * List card's onClick should add card data to the collection
 *
 * In Projects:
 *  Researcher Collection
 *  Sample Collection
 *  Publication Collection
 *
 */
export function NewProjectForm() {
  const [project, dispatch] = useReducer(projectReducer, {
    name: "",
    description: "",
    embargo_date: null,
    sample_collection: [],
    publication_collection: [],
    researcher_collection: [],
    filter_list: "Na",
  });

  return h(ProjectFormContext.Provider, { value: { project, dispatch } }, [
    h(AdminPage, {
      mainPageComponent: h(NewProjectFormMain),
      listComponent: h(ProjectEditListComponent),
    }),
  ]);
}
