import {Component, createElement} from 'react'
import h from 'react-hyperscript'
import {Card, Colors} from '@blueprintjs/core'
import {PagedAPIView} from '@macrostrat/ui-components'
import styled from '@emotion/styled'

import {SampleCard} from './sample/detail-card'
import './main.styl'

class Publication extends Component
  renderMain: ->
    {doi, title} = @props
    doiAddendum = []
    if doi?
      doiAddendum = [
        " – "
        h 'span.doi-info', [
          h 'span.label', 'DOI:'
          h 'span.doi.bp3-monospace-text', doi
        ]
      ]
    h 'div.publication', [
      h 'span.title', title
      doiAddendum...
    ]

  render: ->
    interior = @renderMain()
    {doi} = @props
    return interior unless doi?
    href = "https://dx.doi.org/#{doi}"
    h 'a.publication', {href, target: "_blank"}, interior

ProjectPublications = ({data})->
  content = [
    h 'p', 'No publications'
  ]
  if data?
    content = data.map (d)->
      h Publication, d
  h 'div.publications', [
    h 'h4', 'Publications'
    content...
  ]

ProjectResearchers = ({data})->
  content = [h 'p', 'No researchers']
  if data?
    content = data.map (d)->
      h 'div.researcher', d.name
  h 'div.researchers', [
    h 'h4', 'Researchers'
    content...
  ]

SampleContainer = styled.div"""
  display: flex;
  flex-flow: row wrap;
  margin: 0 -5px;
"""

ProjectSamples = ({data})->
  content = [ h 'p', 'No samples' ]
  if data?
    content = data.map (d)->
      h SampleCard, d
  h 'div.samples', [
    h 'h4', 'Samples'
    h SampleContainer, content
  ]

ProjectComponent = (props)->
  {id, name, description} = props
  h 'div.project.bp3-card', {key: id}, [
    h 'h3', name
    h 'p.description', description
    h ProjectPublications, {data: props.publications}
    h ProjectResearchers, {data: props.researchers}
    h ProjectSamples, {data: props.samples}
  ]

class ProjectListComponent extends Component
  @defaultProps: {
    apiEndpoint: '/project'
  }

  render: ->
    {apiEndpoint} = @props
    params = {private: true}
    return h 'div.data-view.projects', [
      h 'h2', 'Projects'
      h PagedAPIView, {
        route: apiEndpoint,
        params,
        perPage: 5,
        topPagination: true
      }, (data)=>
        h 'div', null, data.map (d)-> h(ProjectComponent, d)
    ]

export {ProjectListComponent}
