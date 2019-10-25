import {Component, createElement} from 'react'
import h from 'react-hyperscript'
import {Card, Colors, Callout} from '@blueprintjs/core'
import styled from '@emotion/styled'
import T from 'prop-types'
import {FilterListComponent} from '../components/filter-list'
import {LinkCard, APIResultView} from '@macrostrat/ui-components'

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

ProjectCard = (props)->
  {id, name, description} = props
  h 'div.project', [
    h 'h3', name
    h 'p.description', description
    h ProjectPublications, {data: props.publications}
    h ProjectResearchers, {data: props.researchers}
    h ProjectSamples, {data: props.samples}
  ]

ProjectInfoLink = (props)->
  {id} = props
  h LinkCard, {
    to: "/catalog/project/#{id}"
    key: id,
    className: 'project-info-card'
  }, [
    h ProjectCard, props
  ]

ProjectListComponent = ->
  route = '/project'
  filterFields = {
    'name': "Name"
    'description': "Description"
  }

  h 'div.data-view.projects', [
      h Callout, {
        icon: 'info-sign',
        title: "Projects"
      }, "This page lists projects of related samples, measurements, and publications.
          Projects can be imported into Sparrow or defined using the managment interface."
    h FilterListComponent, {
      route,
      filterFields,
      itemComponent: ProjectInfoLink
    }
  ]


ProjectComponent = (props)->
  {id} = props
  return null unless id?

  h 'div.data-view.project', [
    h APIResultView, {
      route: "/project"
      params: {id}
    }, (data)=>
      res = data[0]
      {sample_name, id, rest...} = res
      h(ProjectCard, res)
  ]

ProjectComponent.propTypes = {
  id: T.number
}


export {ProjectListComponent, ProjectComponent}
