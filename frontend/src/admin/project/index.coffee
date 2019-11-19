import {Component, createElement, useContext, useState} from 'react'
import {hyperStyled} from '@macrostrat/hyper'
import {
  Card, Colors, Callout,
  EditableText, Intent, Switch
  Alignment, Button, Popover, ButtonGroup
  Menu, MenuItem
} from '@blueprintjs/core'
import styled from '@emotion/styled'
import {put} from 'axios'
import T from 'prop-types'
import {useAuth} from '../../auth'
import {FilterListComponent} from '../../components/filter-list'
import {
  LinkCard, APIResultView,
  ModelEditor, ModelEditorContext, ModelEditButton,
  CancelButton, SaveButton, useModelEditor,
  APIContext
} from '@macrostrat/ui-components'
import {ProjectMap} from './map'
import {MinimalNavbar} from 'app/components/navbar'

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
  {model, actions, isEditing} = useContext(ModelEditorContext)

  # Show text with primary intent if changes have been made
  intent = if actions.hasChanges(field) then Intent.SUCCESS else null

  h el, rest, [
    h.if(isEditing) EditableText, {
      className: "model-edit-text field-#{field}"
      multiline
      placeholder
      intent
      onChange: actions.onChange(field)
      value: model[field]
    }
    h.if(not isEditing) 'span', model[field]
  ]

EmbargoEditor = (props)->
  {login} = useAuth()
  {model, actions, isEditing} = useContext(ModelEditorContext)
  [isOpen, setOpen] = useState(false)
  return null unless login
  h 'div.embargo-editor', [
    h Popover, {
      position: 'bottom',
      isOpen,
      onClose: (evt)=>
        console.log evt
        setOpen(false)
    }, [
      h Button, {
        text: "Public", minimal: true, interactive: false,
        rightIcon: 'lock', intent: Intent.SUCCESS
        onClick: -> setOpen(not isOpen)
      }
      h 'div.embargo-control-panel', [
        h Switch, {
          checked: not model.embargo_date?
          label: "Embargoed"
          alignIndicator: Alignment.RIGHT
          onChange: (evt)->
            {checked} = evt.target
            val = if checked then null else "indefinite"
            actions.updateState {model: {embargo_date: {$set: val}}}
        }
      ]
    ]
  ]

EditStatusButtons = ->
  {isEditing, hasChanges, actions} = useModelEditor()
  changed = hasChanges()
  h [
    h.if(not isEditing) ModelEditButton, "Edit"
    h.if(isEditing) ButtonGroup, [
      h SaveButton, {
        disabled: not changed
        onClick: actions.persistChanges
      }, "Save"
      h CancelButton, {
        intent: if changed then "warning" else "none"
        onClick: actions.toggleEditing
      }, "Done"
    ]
  ]


EditableProjectDetails = (props)->
  {project} = props
  {login} = useAuth()
  {helpers: {buildURL}} = useContext(APIContext)

  h ModelEditor, {
    model: project
    canEdit: login
    persistChanges: (updatedModel, changeset)=>
      {id} = updatedModel
      response = await put(buildURL("/edit/project/#{id}"), changeset)
      {data} = response
      {id, rest...} = data
      return rest
  }, [
    h 'div.project-editor', [
      h.if(login) MinimalNavbar, {className: 'project-editor-navbar'}, [
        h 'h4', "Manage project"
        h EditStatusButtons
        h EmbargoEditor
      ]
      h 'div.project-editor-content', [
        h ModelEditableText, {is: 'h3', field: 'name', multiline: true}
        h ModelEditableText, {is: 'p', field: 'description', multiline: true}
      ]
    ]
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
