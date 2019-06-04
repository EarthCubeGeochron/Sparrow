import styled from '@emotion/styled'
import h from 'react-hyperscript'
import {Component} from 'react'
import ReactMarkdown from 'react-markdown'
import {Tag, Card, Checkbox, Button
        Intent, InputGroup, NumericInput} from '@blueprintjs/core'
import {DatePicker} from '@blueprintjs/datetime'
import classNames from 'classnames'
import {format} from 'date-fns'

class TernaryCheckbox extends Component
  @defaultProps: {
    onChange: ->
  }
  options: [null, true, false]
  onChange: =>
    {onChange, value} = @props
    ix = @options.indexOf(value)
    newIx = (ix+1)%3
    onChange(@options[newIx])

  render: ->
    {value} = @props
    ix = @options.indexOf(value)
    return h Checkbox, {
      onChange: @onChange
      checked: ix == 1
      indeterminate: ix == 0
    }

class DateInput extends Component
  render: ->
    {onChange} = @props
    h DatePicker, {onChange}

class InputForType extends Component
  render: ->
    {type, value, update, name} = @props
    updateSt = (val)->
      if not val? or val == ""
        cset = {$unset: [name]}
      else
        cset = {[name]: {$set: val}}
      update(cset)

    if type == 'bool'
      return h TernaryCheckbox, {
        onChange: (val)=>
          update {[name]: {$set: val}}
        value
      }
    if type == 'str'
      value ?= ""
      onChange = (evt)->
        updateSt(evt.target.value)
      return h InputGroup, {
        id: "text-input"
        placeholder: "string"
        value
        onChange
      }
    if type == 'int'
      onValueChange = (num, string)->
        updateSt(string)
      value ?= ""
      return h NumericInput, {
        id: "text-input"
        placeholder: "integer"
        value
        onValueChange
      }
    if type == 'date'
      onChange = (v)->
        formattedDate = format(v, "YYYY-MM-DD")
        updateSt(formattedDate)
      return h DateInput, {onChange}
    return null

STag = styled(Tag)"""
  margin-right: 0.3em;
  margin-bottom: 0.2em;
"""

DeleteButton_ = (props)->
  h Button, {icon: 'cross', intent: Intent.DANGER, minimal: true, small: true, props...}

DeleteButton = styled(DeleteButton_)"""
  position: absolute;
  top: 5px;
  right: 5px;
"""

BaseParameter = (props)->
  {name, default: defaultArg,
   description, expand, type,
   value, update
   usage, expanded, className} = props

  className = classNames className, 'argument', {expanded}

  if usage?
    usage = h ReactMarkdown, {source: usage}

  if type == 'boolean'
    type = 'bool'
  if type == 'datetime'
    type = 'date'

  attrs = [
    h STag, type
  ]

  if description? and description.startsWith("Column")
    description = null
    intent = Intent.SUCCESS
    attrs.push h Tag, {intent}, "column"

  if defaultArg?
    attrs.push h Tag, "default: #{defaultArg}"

  if expand? and not expanded
    onClick = =>
      expand(name)

  details = null
  if expanded
    details = h 'div.details', [
      usage
      h InputForType, {type, value, update, name}
    ]

  deleteButton = null
  if value?
    deleteButton = h DeleteButton, {
      onClick: ->
        update {$unset: [name]}
    }

  h Card, {
    interactive: not expanded,
    key: name,
    className,
    onClick
  }, [
    h 'div.top', [
      h 'h5.name', name
      h 'div.attributes', attrs
    ]
    h('p.description', description) if description?
    details
    deleteButton
  ]

Parameter = styled(BaseParameter)"""
  margin-bottom: 1em;
  margin-right: 1em;
  transition: width 0.5s;
  position: relative;
  flex-grow: #{(p)->if p.type == 'string' then '2' else '1'};
"""

export {Parameter}
