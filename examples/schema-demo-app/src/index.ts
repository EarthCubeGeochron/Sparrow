import h from "@macrostrat/hyper"
import { render } from "react-dom"

const el = document.querySelector(".app")

render(h("div", "Hello, world"), el)