import {Component, createElement} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {PagedAPIView} from '@macrostrat/ui-components'
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

Sample = (props)->
  {material_data} = props
  material = null
  if material_data?
    material = h 'span.material', material_data[0].description

  h 'div.sample', [
    h 'span.name', props.id
    material
  ]

ProjectSamples = ({data})->
  content = [ h 'p', 'No samples' ]
  if data?
    content = data.map (d)->
      h Sample, d
  h 'div.samples', [
    h 'h4', 'Samples'
    content...
  ]

ProjectComponent = (props)->
  {id, title, description} = props
  h 'div.project.bp3-card', {key: id}, [
    h 'h3', title
    h 'p.description', description
    h ProjectPublications, {data: props.publications}
    h ProjectResearchers, {data: props.researchers}
    h ProjectSamples, {data: props.samples}
  ]

class ProjectListComponent extends Component
  @defaultProps: {
    apiEndpoint: '/api/v1/project'
  }

  render: ->
    {apiEndpoint} = @props
    return h 'div.data-view.projects', [
      h 'h2', 'Projects'
      h PagedAPIView, {route: apiEndpoint, perPage: 5}, (data)=>
        h 'div', null, data.map (d)-> h(ProjectComponent, d)
    ]

export {ProjectListComponent}
