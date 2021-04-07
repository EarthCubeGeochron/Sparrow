import h from "@macrostrat/hyper"
import { render } from "react-dom"
import {TermCard} from "@earthcube/schema-linker"

const el = document.querySelector(".app")

render(h("div", null, h(TermCard, {data: {id: "test", authority: "You"}})), el)