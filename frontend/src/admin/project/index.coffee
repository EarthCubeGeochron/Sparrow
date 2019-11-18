import {Component, createElement, useContext} from 'react'
import {hyperStyled} from '@macrostrat/hyper'
import {Card, Colors, Callout, EditableText, Intent, Switch} from '@blueprintjs/core'
import styled from '@emotion/styled'
import T from 'prop-types'
import {useAuth} from '../../auth'
import {FilterListComponent} from '../../components/filter-list'
import {
  LinkCard, APIResultView,
  ModelEditor, ModelEditorContext, ModelEditButton
} from '@macrostrat/ui-components'
import {ProjectMap} from './map'

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

ModelEditableText = (props)->
  el = props.is or 'div'
  {multiline, field, placeholder, rest...} = props
  placeholder ?= "Add a "+field
  delete rest.is
  {data, actions, isEditing} = useContext(ModelEditorContext)

  # Show text with primary intent if changes have been made
  intent = if actions.hasChanges(field) then Intent.SUCCESS else null

  h el, rest, [
    h.if(isEditing) EditableText, {
      multiline
      placeholder
      intent
      onChange: actions.onChange(field)
      value: data[field]
    }
    h.if(not isEditing) 'span', data[field]
  ]

EmbargoEditor = (props)->
  {data, actions, isEditing} = useContext(ModelEditorContext)
  return null unless isEditing
  h Switch, {
    checked: not data.embargo_date?
    large: true
    label: "Public"
    onChange: (evt)->
      {checked} = evt.target
      val = if checked then null else "indefinite"
      actions.updateState {data: {embargo_date: {$set: val}}}
  }

EditableProjectDetails = (props)->
  {project} = props
  {login} = useAuth()

  h ModelEditor, {data: project, isEditing: login}, [
    h ModelEditableText, {is: 'h3', field: 'name', multiline: true}
    h ModelEditableText, {is: 'p', field: 'description', multiline: true}
    h EmbargoEditor
  ]

ProjectPage = (props)->
  {project} = props
  {samples} = project
  h 'div', [
    h EditableProjectDetails, {project}
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
