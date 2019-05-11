import React from "react"
import { Link } from "gatsby"
import h from "react-hyperscript"
import Layout from "../components/layout"
import Image from "../components/image"
import SEO from "../components/seo"
import md from './home.mdx'

IndexPage = ->
  h Layout, [
    h SEO, {title: "Home",  keywords: ['gatsby', 'application', 'react']}
    h 'div', null, (
      h 'p', "Sparrow is a laboratory information management system focused on geochronology."
    )
    h 'div', style: { maxWidth: '400px', marginBottom: '1.45rem' }, (
      h Image
    )
    h md
    h Link, {to: "/page-2/"}, "Go to page 2"
  ]

export default IndexPage
