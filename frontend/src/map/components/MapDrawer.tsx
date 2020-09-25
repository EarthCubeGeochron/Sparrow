import { useState } from "react";
import { Editor, EditingMode, DrawRectangleMode } from "react-map-gl-draw";
import h from "@macrostrat/hyper";
import { Select } from "@blueprintjs/select";

const MODES = [
  {
    id: "drawRectanlge",
    text: "Draw a Reactangle",
    handler: DrawRectangleMode,
  },
  { id: "editing", text: "Edit Feature", handler: EditingMode },
];

interface Drawer {
  modeId: number;
  modeHandler: any; //function
}
export function MapDrawer() {
  const initialState: Drawer = {
    modeId: null,
    modeHandler: null,
  };
  const [state, setState] = useState(initialState);

  const modeSwitcher = () => {
    return h(Select);
  };
  return h(Editor, { mode: state.modeHandler });
}
