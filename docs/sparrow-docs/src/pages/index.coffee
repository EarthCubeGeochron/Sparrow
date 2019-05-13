import React from "react"
import { Link } from "gatsby"
import h from "react-hyperscript"
import Layout from "../components/layout"
import Image from "../components/image"
import SEO from "../components/seo"
import md from './home.mdx'
import introText from './intro-text.mdx'

IndexPage = ->
  h Layout, [
    h SEO, {title: "Home",  keywords: ['gatsby', 'application', 'react']}
    h 'div.index-top', [
      h 'div.intro-text', null, h(introText)
      h 'div', style: { maxWidth: '400px', marginBottom: '1.45rem' }, (
        h Image
      )
    ]
    h md
    h Link, {to: "/page-2/"}, "Go to page 2"
  ]

export default IndexPage
