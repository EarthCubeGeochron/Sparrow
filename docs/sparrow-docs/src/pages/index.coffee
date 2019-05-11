import React from "react"
import { Link } from "gatsby"
import h from "react-hyperscript"
import Layout from "../components/layout"
import Image from "../components/image"
import SEO from "../components/seo"

IndexPage = =>
  h Layout, [
    h SEO, {title: "Home",  keywords: ['gatsby', 'application', 'react']}
    h 'h1', "Hi people"
    h 'p', "Welcome to your new Gatsby site."
    h 'p', "Now go build something great."
    h 'div', style: { maxWidth: '300px', marginBottom: '1.45rem' }, (
      h 'Image'
    )
    h Link, {to: "/page-2/"}, "Go to page 2"
  ]

export default IndexPage
