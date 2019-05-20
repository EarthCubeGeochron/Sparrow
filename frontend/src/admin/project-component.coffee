import {Component, createElement} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {Card, Colors} from '@blueprintjs/core'
import {PagedAPIView} from '@macrostrat/ui-components'
import styled from '@emotion/styled'
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

SampleCard = styled.div"""
  background-color: #{Colors.LIGHT_GRAY4};
  border-radius: 5px;
  margin: 5px;
  padding: 5px 10px;
  flex-grow: 1;
  max-width: 15em;
  .location-name {
    color: #{Colors.RED1};
  }
  h4 {
    margin-top: 0em;
    margin-bottom: 0em;
  }
"""

Material = styled.div"""font-style: italic"""

Sample = (props)->
  {material, sample_id, location_name} = props
  if material?
    material = h Material, material

  h SampleCard, {className: 'sample'}, [
    h 'h4.name', sample_id
    h 'div.location-name', location_name
    material
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
      h Sample, d
  h 'div.samples', [
    h 'h4', 'Samples'
    h SampleContainer, content
  ]

ProjectComponent = (props)->
  console.log props
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
