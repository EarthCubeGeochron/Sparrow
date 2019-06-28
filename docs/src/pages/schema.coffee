import React from "react"
import h from "react-hyperscript"
import Layout from "../components/layout"
import content from '../../build/schema.html'

SchemaPage = ->
  h Layout, [
    h 'div.page-content', [
      h 'div.schema', {dangerouslySetInnerHTML: {__html: content}}
    ]
  ]

export default SchemaPage
