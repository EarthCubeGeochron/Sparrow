import { hyperStyled } from "@macrostrat/hyper";
import { useReducer, useState, createContext, useContext } from "react";
import { AdminPage } from "~/admin/AdminPage";
import { APIHelpers } from "@macrostrat/ui-components";
import {
  ModelEditableText,
  SampleAdd,
  PubAdd,
  ResearcherAdd,
  SubmitButton,
  EmbargoDatePick,
  PublicationFilterList,
  ResearcherFilterList,
  SampleFilterList,
} from "../components";
import { ProjectAdminContext } from "~/admin/project";
import { MinimalNavbar } from "~/components";
import { APIV2Context } from "../../api-v2";
import axios from "axios";
//@ts-ignore
import styles from "./project-form.styl";

const h = hyperStyled(styles);

export const ProjectFormContext = createContext({});

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
      const remove = action.payload.sample;
      const samples = currentSa.filter((ele) => ele.name != remove.name);
      console.log(samples);
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
      const removeP_title = action.payload.pub_title;
      const pubs = currentPu.filter((el) => el.title != removeP_title);
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
      const removeRes_name = action.payload.res_name;
      const researchers = currentRes.filter((el) => el.name != removeRes_name);
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
  const { project, dispatch } = useContext(ProjectFormContext);
  console.log(project);
  const { buildURL } = APIHelpers(useContext(APIV2Context));

  async function postData() {
    const route = buildURL("/models/project", {});

    const projectPost = {
      name: project.name,
      description: project.description,
      samples: project.sample_collection,
      publications: project.publication_collection,
      researchers: project.researcher_collection,
    };

    const response = await axios.post(route, projectPost).then((response) => {
      return response;
    });
    const { data } = response;
    console.log(data);
    const { id } = data.data;
    const goToRoute = process.env.BASE_URL + `admin/project/${id}`;
    window.location.assign(goToRoute);
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
    const { setListName, changeFunction } = useContext(ProjectAdminContext);

    const onClickDelete = ({ id, name }) => {
      let sample;
      if (id) {
        sample = { id, name };
      } else {
        sample = { name };
      }
      dispatch({ type: "remove_sample", payload: { sample: sample } });
    };

    const onClickSam = (sample) => {
      dispatch({
        type: "add_sample",
        payload: { sample_collection: [sample] },
      });
    };

    const onClickList = () => {
      setListName("sample");
      changeFunction(onClickSam);
    };

    return h(SampleAdd, {
      onClickDelete,
      onClickList,
      data: project.sample_collection,
    });
  };

  // this should look like normal project page
  const PubAddProj = () => {
    const { setListName, changeFunction } = useContext(ProjectAdminContext);

    const onClickDelete = ({ id, title }) => {
      dispatch({ type: "remove_pub", payload: { pub_title: title } });
      console.log("Remove", title);
    };

    const onClickPub = (id, title, doi) => {
      dispatch({
        type: "add_pub",
        payload: {
          publication_collection: [{ id, title, doi }],
        },
      });
    };

    const onClickList = () => {
      setListName("publication");
      changeFunction(onClickPub);
    };

    return h(PubAdd, {
      data: project.publication_collection,
      onClickDelete,
      onClickList,
    });
  };

  const ResearcherAddProj = () => {
    const { setListName, changeFunction } = useContext(ProjectAdminContext);

    const onClickDelete = ({ id, name }) => {
      dispatch({ type: "remove_res", payload: { res_name: name } });
      console.log(id);
    };
    const onClickRes = (id, name) => {
      dispatch({
        type: "add_researcher",
        payload: {
          researcher_collection: [{ id, name }],
        },
      });
    };
    const onClickList = () => {
      setListName("researcher");
      changeFunction(onClickRes);
    };
    return h(ResearcherAdd, {
      onClickDelete,
      onClickList,
      data: project.researcher_collection,
    });
  };

  const EmbargoDate = () => {
    const onChange = (date) => {
      dispatch({ type: "embargo_date", payload: { embargo_date: date } });
    };
    const embargo_date = project.embargo_date;
    return h("div", [h(EmbargoDatePick, { onChange, embargo_date })]);
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
    h(SubmitButton, { postData, modelName: "Project" }),
  ]);
}

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
  });

  return h(ProjectFormContext.Provider, { value: { project, dispatch } }, [
    h(NewProjectFormMain),
  ]);
}
