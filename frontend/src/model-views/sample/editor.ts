import * as React from "react";
import { useState, useEffect, useContext } from "react";
import { EditNavBar, ModelEditableText } from "../project/editor";
import h from "@macrostrat/hyper";
import {
  ModelEditor,
  ModelEditorContext,
  ModelEditButton,
  CancelButton,
  SaveButton,
  useModelEditor,
  APIContext,
  APIHelpers,
} from "@macrostrat/ui-components";
import { useAuth } from "~/auth";

function SampleEditNavBar() {
  const { isEditing } = useContext(ModelEditorContext);
  console.log(isEditing);
  return h(ModelEditButton, "Edit");
}

function SampleEditing(props) {
  const { sample } = props;
  const { login } = useAuth();
  const { buildURL } = APIHelpers(useContext(APIContext));

  const { isEditing } = useModelEditor();
  console.log(isEditing);

  return h(
    ModelEditor,
    {
      model: sample,
      canEdit: login,
      persistChanges: () => null,
    },
    [h(SampleEditNavBar)]
  );
}

export { SampleEditing };
