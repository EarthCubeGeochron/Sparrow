import React from "react"
import { Link } from "gatsby"
import h from "react-hyperscript"
import Layout from "../components/layout"
import Image from "../components/image"
import SEO from "../components/seo"
import md from '../../text/installation.mdx'
console.log md

IndexPage = ->
  h Layout, [
    h SEO, {title: "Home",  keywords: ['gatsby', 'application', 'react']}
    h md
    h Link, {to: "/page-2/"}, "Go to page 2"
  ]

export default IndexPage
