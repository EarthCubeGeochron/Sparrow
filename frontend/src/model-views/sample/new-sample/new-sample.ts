import React, { createContext, useContext, useReducer } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { APIHelpers } from "@macrostrat/ui-components";
import Ax from "axios";
import { APIV2Context } from "~/api-v2";
import { AdminPage } from "~/admin/AdminPage";
import {
  NewSampleMap,
  SampleLocation,
  SampleDepth,
  SampleElevation,
  GeoContext,
  SampleMaterial,
  SampleName,
  SubmitButton,
  EmbargoDatePick,
  ModelAddFilterLists,
  ProjectAdd,
  SessionAdd,
} from "../../components";
import { sampleReducer } from "./reducer";
import { MinimalNavbar } from "~/components";
import {
  modelEditList,
  sample_reducer,
  sampleFormState,
  sampleContext,
} from "./types";
// @ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

const NewSampleFormContext = createContext<Partial<sampleContext>>({});

const NewSampleProjectAdd = () => {
  const { sample, dispatch } = useContext(NewSampleFormContext);

  const onAddProject = (id, name) => {
    dispatch({
      type: sample_reducer.ADD_PROJECT,
      payload: { project: { id, name } },
    });
  };

  const onDeleteProject = ({ id, name }) => {
    dispatch({
      type: sample_reducer.REMOVE_PROJECT,
      payload: { project: { id, name } },
    });
  };

  const onClickList = () => {
    dispatch({
      type: sample_reducer.LIST_NAME,
      payload: { listName: modelEditList.PROJECT },
    });
    dispatch({
      type: sample_reducer.CHANGE_FUNCTION,
      payload: { changeFunction: onAddProject },
    });
  };

  return h(ProjectAdd, {
    onClickDelete: onDeleteProject,
    onClickList,
    data: sample,
    isEditing: true,
  });
};

const NewSampleSessionAdd = () => {
  const { sample, dispatch } = useContext(NewSampleFormContext);

  const onSessionAdd = (id, date, target, technique) => {
    const session = { id, date, target, technique };
    dispatch({ type: sample_reducer.ADD_SESSION, payload: { session } });
  };

  const onClickDelete = ({ session_id: id, date }) => {
    dispatch({
      type: sample_reducer.REMOVE_SESSION,
      payload: { session: { id, date } },
    });
  };

  const onClickList = () => {
    dispatch({
      type: sample_reducer.LIST_NAME,
      payload: { listName: modelEditList.SESSION },
    });
    dispatch({
      type: sample_reducer.CHANGE_FUNCTION,
      payload: { changeFunction: onSessionAdd },
    });
  };

  return h(SessionAdd, {
    onClickDelete,
    onClickList,
    data: sample.session,
    isEditing: true,
  });
};

const EmbargoDate = () => {
  const { sample, dispatch } = useContext(NewSampleFormContext);

  const onChange = (date) => {
    dispatch({ type: sample_reducer.EMBARGO, payload: { embargo_date: date } });
  };
  const embargo_date = sample.embargo_date;
  return h("div", [h(EmbargoDatePick, { onChange, embargo_date })]);
};

const NewSampleNavBar = (props) => {
  return h(MinimalNavbar, { className: "project-editor-navbar" }, [
    h("h4", props.header),
    h(EmbargoDate),
  ]);
};

function NewSamplePageMainComponent({ onSubmit }): React.ReactElement {
  const { sample, dispatch } = useContext(NewSampleFormContext);

  console.log(sample);
  const changeCoordinates = (coords) => {
    console.log(coords);
    dispatch({
      type: sample_reducer.LOCATION,
      payload: { coordinates: coords },
    });
  };

  const changeName = (name) => {
    dispatch({ type: sample_reducer.NAME, payload: { name } });
  };

  const changeDepth = (depth) => {
    dispatch({ type: sample_reducer.DEPTH, payload: { depth } });
  };

  const changeElevation = (elevation) => {
    dispatch({
      type: sample_reducer.ELEVATION,
      payload: { elevation },
    });
  };
  const changeMaterial = (material) => {
    dispatch({
      type: sample_reducer.MATERIAL,
      payload: { material },
    });
  };

  const changeGeoEntity = (geo_entity) => {
    console.log(geo_entity);
    dispatch({
      type: sample_reducer.GEO_ENTITY,
      payload: { geo_entity: geo_entity },
    });
  };

  const deleteGeoEntity = (index) => {
    console.log(index);
    dispatch({
      type: sample_reducer.REMOVE_GEO_ENTITY,
      payload: { index },
    });
  };

  const { sample_geo_entity, location } = sample;
  const {
    coordinates: [longitude, latitude],
  } = location;

  return h("div.drawer-body", [
    h(NewSampleNavBar, { header: "Create new Sample" }),
    h(SampleName, { changeName }),
    h("div.location", [
      h("div", [
        h(SampleLocation, {
          changeCoordinates,
          sample: { longitude, latitude },
        }),
        h(SampleDepth, { sample, changeDepth }),
        h(SampleElevation, { sample, changeElevation }),
      ]),
      h("div.sample-map", [h(NewSampleMap, { changeCoordinates, sample })]),
    ]),
    h(SampleMaterial, { changeMaterial, sample }),
    h("div.metadata-body", [
      h(GeoContext, {
        sample_geo_entity: sample_geo_entity == null ? null : sample_geo_entity,
        changeGeoEntity,
        deleteGeoEntity,
      }),
    ]),
    h(NewSampleProjectAdd),
    h(NewSampleSessionAdd),
    h(SubmitButton, { postData: onSubmit }),
  ]);
}

function NewSampleListComponent(): React.ReactElement {
  const { sample } = useContext(NewSampleFormContext);
  const { listName, changeFunction } = sample;
  return h(ModelAddFilterLists, { listName, onClick: changeFunction });
}

const initialState: sampleFormState = {
  embargo_date: null,
  elevation: null,
  name: null,
  material: null,
  depth: null,
  project: [],
  session: [],
  location: { type: "Point", coordinates: [null, null] },
  sample_geo_entity: [],
  changeFunction: () => {},
  listName: modelEditList.MAIN,
};

export function NewSamplePage() {
  const [sample, dispatch] = useReducer(sampleReducer, initialState);
  const { buildURL } = APIHelpers(useContext(APIV2Context));

  const onSubmit = async () => {
    const route = buildURL("/models/sample");
    const samplePost = { ...sample };
    delete samplePost.changeFunction;
    delete samplePost.listName;
    if (!samplePost.location.coordinates[0]) {
      samplePost.location = null;
    }
    console.log(samplePost);
    const response = await Ax.post(route, samplePost).then((response) => {
      return response;
    });
    console.log(response);
    dispatch({
      type: sample_reducer.LIST_NAME,
      payload: { listName: modelEditList.MAIN },
    });
    const goToRoute = process.env.BASE_URL + "admin/sample";
    console.log(goToRoute);
    //window.location.assign(goToRoute);
  };

  return h(
    NewSampleFormContext.Provider,
    {
      value: {
        sample,
        dispatch,
      },
    },
    [
      h(AdminPage, {
        mainPageComponent: h(NewSamplePageMainComponent, { onSubmit }),
        listComponent: h(NewSampleListComponent),
      }),
    ]
  );
}
