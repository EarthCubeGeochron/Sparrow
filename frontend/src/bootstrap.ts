import "./shared/ui-init";
import { createElement } from "react";
import { render } from "react-dom";
import App from "./app";

const el = document.createElement("div");
el.id = "container";
document.body.appendChild(el);

render(createElement(App), el);
