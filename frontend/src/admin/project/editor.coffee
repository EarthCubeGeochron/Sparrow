import {useContext, useState} from 'react'
import {hyperStyled} from '@macrostrat/hyper'
import {
  EditableText, Intent, Switch
  Alignment, Button, Popover, ButtonGroup
  Menu, MenuItem
} from '@blueprintjs/core'
import T from 'prop-types'
import {useAuth} from '../../auth'
import {
  ModelEditor, ModelEditorContext, ModelEditButton,
  CancelButton, SaveButton, useModelEditor,
  APIContext
} from '@macrostrat/ui-components'
import {MinimalNavbar} from 'app/components/navbar'

import classNames from 'classnames'
import '../main.styl'
import styles from '../module.styl'
h = hyperStyled(styles)

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
  text = if model.embargo_date? then "Embargoed" else "Public"
  icon = if model.embargo_date? then "lock" else "unlock"
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
        text, minimal: true, interactive: false,
        rightIcon: icon, intent: Intent.SUCCESS
        onClick: -> setOpen(not isOpen)
      }
      h 'div.embargo-control-panel', [
        h Switch, {
          checked: model.embargo_date?
          label: "Embargoed"
          alignIndicator: Alignment.RIGHT
          onChange: (evt)->
            {checked} = evt.target
            val = if checked then "+Infinity" else null
            actions.persistChanges {embargo_date: {$set: val}}
        }
      ]
    ]
  ]

EditStatusButtons = ->
  {isEditing, hasChanges, actions} = useModelEditor()
  changed = hasChanges()
  h 'div.edit-status-controls', [
    h.if(not isEditing) ModelEditButton, {minimal: true}, "Edit"
    h.if(isEditing) ButtonGroup, {minimal: true}, [
      h SaveButton, {
        disabled: not changed
        onClick: -> actions.persistChanges()
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


export {EditableProjectDetails}
