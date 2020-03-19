import {Component} from 'react'
import {hyperStyled} from '@macrostrat/hyper'
import {
  Card, Callout
} from '@blueprintjs/core'
import styled from '@emotion/styled'
import T from 'prop-types'
import {FilterListComponent} from '../../components/filter-list'
import {LinkCard, APIResultView} from '@macrostrat/ui-components'
import {ProjectMap} from './map'
import {EditableProjectDetails} from './editor'

import classNames from 'classnames'
import {SampleCard} from '../sample/detail-card'
import '../main.styl'
import styles from '../module.styl'
h = hyperStyled(styles)

pluralize = (term, arrayOrNumber)->
  count = arrayOrNumber
  if Array.isArray(arrayOrNumber)
    count = arrayOrNumber.length
  if count > 1
    term += "s"
  return term

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
  data ?= []
  h [
    h.if(data.length) 'div.publications', [
      h 'h4', 'Publications'
      (data or []).map (d, i)->
        h Publication, {key: i, d...}
    ]
    h.if(not data?) "div.publications", "No publications"
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

ContentArea = ({data, title, className})->
  h 'div.content-area', [
    h 'h5', [
      h 'span.count', data.length
      " "
      pluralize(title, data)
    ]
    h 'ul', {className}, data.map (d)->
      h 'li', d
  ]

ProjectInfoLink = (props)->
  {id, name, description, samples, publications} = props
  publications ?= []
  h LinkCard, {
    to: "/catalog/project/#{id}"
    key: id,
    className: 'project-card'
  }, [
    h 'h3', name
    h 'p.description', description
    h.if(samples.length) ContentArea, {
      className: 'samples'
      data: samples.map (d)->d.name
      title: 'sample'
    }
    h.if(publications.length) ContentArea, {
      className: 'publications'
      data: publications.map (d)->d.title
      title: 'publication'
    }
  ]

ProjectListComponent = ->
  h 'div.data-view.projects', [
      h Callout, {
        icon: 'info-sign',
        title: "Projects"
      }, "This page lists projects of related samples, measurements, and publications.
          Projects can be imported into Sparrow or defined using the managment interface."
    h FilterListComponent, {
      route: '/project',
      filterFields: {
        'name': "Name"
        'description': "Description"
      }
      itemComponent: ProjectInfoLink
    }
  ]

ProjectPage = (props)->
  {project} = props
  {samples} = project
  h 'div.project-page', [
    h EditableProjectDetails, {project}
    h ProjectPublications, {data: project.publications}
    h ProjectResearchers, {data: project.researchers}
    h 'div.flex-row', [
      h ProjectSamples, {data: project.samples}
      h 'div', [
        h 'h4', 'Location'
        h ProjectMap, {samples}
      ]
    ]
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
