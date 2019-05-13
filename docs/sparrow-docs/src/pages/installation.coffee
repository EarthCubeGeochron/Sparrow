import React from "react"
import { Link } from "gatsby"
import h from "react-hyperscript"
import Layout from "../components/layout"
import Image from "../components/image"
import SEO from "../components/seo"
import md from '../text/installation.mdx'

InstallationPage = ->
  h Layout, [
    h md
  ]

export default InstallationPage
