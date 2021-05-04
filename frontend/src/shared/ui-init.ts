// Should import this in styles
import "./ui-main.styl";
//import "core-js/stable";
import "regenerator-runtime/runtime";
import "@macrostrat/ui-components/lib/esm/index.css";
import { FocusStyleManager } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";

FocusStyleManager.onlyShowFocusOnTabs();
