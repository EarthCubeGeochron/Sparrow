import h from "@macrostrat/hyper"
import { render } from "react-dom"
import HelloWorld from "hello-world"

const el = document.querySelector(".app")

render(h("div", null, h(HelloWorld)), el)