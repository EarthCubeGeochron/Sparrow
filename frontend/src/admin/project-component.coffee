import {Component, createElement} from 'react'
import {hyperStyled} from '@macrostrat/hyper'
import {Card, Colors, Callout} from '@blueprintjs/core'
import styled from '@emotion/styled'
import T from 'prop-types'
import {FilterListComponent} from '../components/filter-list'
import {LinkCard, APIResultView} from '@macrostrat/ui-components'
import {ContextMap, StaticMarker} from 'app/components'
import bbox from '@turf/bbox'
import WebMercatorViewport from 'viewport-mercator-project'

import {SampleCard} from './sample/detail-card'
import './main.styl'
import styles from './module.styl'
h = hyperStyled(styles)

pluralize = (term, arrayOrNumber)->
  count = arrayOrNumber
  if Array.isArray(arrayOrNumber)
    count = arrayOrNumber.length
  if count > 1
    term += "s"
  return term

ProjectMap = (props)->
  {width, height, samples, padding, minExtent} = props
  return null unless samples?
  locatedSamples = samples.filter (d)->d.geometry?
  return null unless locatedSamples.length > 0
  padding ?= 50
  minExtent ?= 0.2 # In degrees
  width ?= 400
  height ?= 300
  vp = new WebMercatorViewport {width, height}
  {samples} = props
  coordinates = locatedSamples
    .map (d)-> d.geometry.coordinates
  return null unless coordinates.length
  feature = {
    type: 'Feature'
    geometry: {
      type: 'MultiPoint',
      coordinates
    }}
  box = bbox(feature)
  bounds = [box.slice(0,2), box.slice(2,4)]
  console.log(bounds)
  res = vp.fitBounds(bounds, {padding, minExtent})
  {latitude, longitude, zoom} = res
  center = [longitude, latitude]

  h ContextMap, {
    className: 'project-context-map'
    center
    zoom
    width
    height
  }, locatedSamples.map (d)->
    [longitude, latitude] = d.geometry.coordinates
    console.log longitude, latitude
    h StaticMarker, {latitude, longitude}

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
  h.if(data?) 'div.publications', [
    h 'h4', 'Publications'
    data.map (d)->
      h Publication, d
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
  h 'div.sample-area', [
    h 'h4', 'Samples'
    h SampleContainer, content
  ]

ProjectCard = (props)->
  {id, name, description, samples, publications} = props
  publications ?= []
  h 'div.project-card', [
    h 'h3', name
    h 'p.description', description
    h.if(samples.length) 'div.content-area', [
      h 'h5', [
        h 'span.count', samples.length
        " "
        pluralize('sample', samples)
      ]
      h 'ul.samples', samples.map (d)->
        h 'li', d.name
    ]
    h.if(publications.length) 'div.content-area', [
      h 'h5', [
        h 'span.count', publications.length
        " "
        pluralize('publication', publications)
      ]
      h 'ul.publications', publications.map (d)->
        h 'li', d.title
    ]
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

ProjectPage = (props)->
  {project} = props
  {samples} = project
  h 'div', [
    h 'h3', project.name
    h 'p.description', project.description
    h ProjectPublications, {data: project.publications}
    h ProjectResearchers, {data: project.researchers}
    h ProjectSamples, {data: project.samples}
    h ProjectMap, {samples}
  ]


ProjectComponent = (props)->
  {id} = props
  return null unless id?

  h 'div.data-view.project', [
    h APIResultView, {
      route: "/project"
      params: {id}
    }, (data)=>
      project = data[0]
      h(ProjectPage, {project})
  ]

ProjectComponent.propTypes = {
  id: T.number
}


export {ProjectListComponent, ProjectComponent}
