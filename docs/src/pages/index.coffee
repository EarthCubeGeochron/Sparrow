import { Link } from "gatsby"
import h from "react-hyperscript"
import Layout from "../components/layout"
import Image from "../components/image"
import SEO from "../components/seo"
import md from '../text/home.mdx'

IndexPage = ->
  h Layout, [
    h SEO, {title: "Home",  keywords: ['gatsby', 'application', 'react']}
    h 'div.index-top', [
      h 'div.tagline', null, "An open-source laboratory information management system focused on geochronology."
      h 'div.image', style: { width: '500px', marginBottom: '1.45rem' }, [
        h Image
      ]
    ]
    h 'div.page-content', [
      h md
    ]
  ]

export default IndexPage
