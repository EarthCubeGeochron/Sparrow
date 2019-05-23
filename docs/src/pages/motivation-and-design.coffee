import h from "react-hyperscript"
import Layout from "../components/layout"
import md from "../text/motivation-and-design.mdx"

MotivationPage = ->
  h Layout, [
    h md
  ]

export default MotivationPage
