import { Link } from "gatsby"
import h from "react-hyperscript"
import Layout from "../components/layout"
import Image from "../components/image"
import SEO from "../components/seo"
import md from '../text/home.mdx'
import introText from './intro-text.mdx'

IndexPage = ->
  h Layout, [
    h SEO, {title: "Home",  keywords: ['gatsby', 'application', 'react']}
    h 'div.index-top', [
      h 'div.intro-text', null, h(introText)
      h 'div', style: { maxWidth: '500px', marginBottom: '1.45rem' }, (
        h Image
      )
    ]
    h md
  ]

export default IndexPage
