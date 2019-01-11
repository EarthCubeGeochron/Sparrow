import {Component, createElement} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import './main.styl'

ProjectPublications = ({data})->
  content = [
    h 'p', 'No publications'
  ]
  if data?
    content = data.map (d)->
      h 'div.publication', d.title
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
