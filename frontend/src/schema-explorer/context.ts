import { hyperStyled } from "@macrostrat/hyper";
import { useAPIActions } from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import { createContext, useContext, useEffect, useReducer } from "react";
//@ts-ignore
import styles from "./module.styl";
import { fetchFields, getPossibleModels } from "./fetch";
import { useRouteMatch } from "react-router";

const h = hyperStyled(styles);

///////////////////// Misscel Data Types //////////////////////

type PossModelObj = { name: string; route: string };
type NestedModelNamespaces = { namespace: string[]; route: string };

///////////////////// sync action types ///////////////////////////
type SwitchModel = { type: "switch-model"; payload: { model: string } };
type PossibleModels = {
  type: "possible-models";
  payload: { models: PossModelObj[] };
};
type ModelFields = { type: "model-fields"; payload: { fields: object } };

//////////////////////// async action types //////////////////////
type GetPossibleModels = { type: "get-possible-models" };
type GetModelFields = {
  type: "get-model-fields";
  payload: { model_route: string };
};
type GetModelFromPath = {
  type: "get-model-from-path";
};

///////////////// union types ////////////////////////
type SchemaActions = SwitchModel | PossibleModels | ModelFields;
type AsyncSchemaActions = GetPossibleModels | GetModelFields | GetModelFromPath;

/////////////////// Async Actions /////////////////////
function useSchemaActions(dispatch) {
  const { get } = useAPIActions(APIV2Context);
  return async (action: SchemaActions | AsyncSchemaActions) => {
    switch (action.type) {
      case "get-possible-models": {
        const models = await getPossibleModels(get);
        return dispatch({
          type: "possible-models",
          payload: { models }
        });
      }
      case "get-model-fields": {
        const fields = await fetchFields(action.payload.model_route, get);
        return dispatch({
          type: "model-fields",
          payload: { fields }
        });
      }
      case "get-model-from-path": {
      }
      default:
        return dispatch(action);
    }
  };
}

/////////////// Schema Reducer ///////////////
function schemaExplorerReducer(
  state = schemaExplorerDefaultState,
  action: SchemaActions
) {
  switch (action.type) {
    case "switch-model": {
      let route = state.route;
      if (state.possibleModels) {
        route = state.possibleModels[action.payload.model];
      }
      return {
        ...state,
        model: action.payload.model,
        route
      };
    }
    case "possible-models": {
      return {
        ...state,
        possibleModels: action.payload.models
      };
    }
    case "model-fields": {
      return {
        ...state,
        fields: action.payload.fields
      };
    }
    default:
      console.error("I don't understand");
  }
}

interface schemaState {
  model: string;
  route: string;
  possibleModels: object;
  fields: object;
  modelsToShow: string[];
}

const schemaExplorerDefaultState: schemaState = {
  model: null,
  route: null,
  possibleModels: [],
  fields: {},
  modelsToShow: [
    "project",
    "sample",
    "sample_geo_entity",
    "geo_entity",
    "analysis",
    "datum",
    "data_file",
    "material",
    "instrument",
    "researcher",
    "publication",
    "tag"
  ]
};

interface SchemaCtx {
  state: schemaState;
  runAction(action: SchemaActions | AsyncSchemaActions): Promise<void>;
}

const SchemaExplorerContext = createContext<SchemaCtx>({
  state: schemaExplorerDefaultState,
  async runAction() {}
});

function SchemaExplorerContextProvider(props) {
  const [state, dispatch] = useReducer(
    schemaExplorerReducer,
    schemaExplorerDefaultState
  );

  const runAction = useSchemaActions(dispatch);

  useEffect(() => {
    runAction({ type: "get-possible-models" });
  }, []);

  useEffect(() => {
    runAction({
      type: "get-model-fields",
      payload: { model_route: state.route }
    });
  }, [state.model]);

  return h(
    SchemaExplorerContext.Provider,
    { value: { state, runAction } },
    props.children
  );
}

export { SchemaExplorerContextProvider, SchemaExplorerContext };
