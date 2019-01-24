import {Component, createElement} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
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
  h 'div.sample', [
    h 'span.name', props.id
    h 'span.material', props.material_data[0].description
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

class ProjectComponent extends Component
  @defaultProps: {
    apiEndpoint: '/api/v1/project'
  }
  constructor: ->
    super arguments...
    @state = {data: null}
    @getData()

  renderProject: (project)=>
    {id, title, description} = project
    h 'div.project.bp3-card', {key: id}, [
      h 'h3', title
      h 'p.description', description
      h ProjectPublications, {data: project.publications}
      h ProjectResearchers, {data: project.researchers}
      h ProjectSamples, {data: project.samples}
    ]

  render: ->
    {data} = @state
    return null unless data?
    console.log data
    return h 'div.projects', [
      h 'h2', 'Projects'
      h 'div', null, data.map @renderProject
    ]

  getData: ->
    {data} = await get(@props.apiEndpoint)
    @setState {data}

export {ProjectComponent}
