import styled from '@emotion/styled'
import h from 'react-hyperscript'
import {Component} from 'react'
import ReactMarkdown from 'react-markdown'
import {Tag, Card, Checkbox,
        Intent, InputGroup, NumericInput} from '@blueprintjs/core'
import {DateRangePicker} from '@blueprintjs/datetime'
import classNames from 'classnames'

class StatefulCheckbox extends Component
  constructor: (props)->
    super props
    @state = {ix: 0}
  render: ->
    {ix} = @state
    {onChange, rest...} = @props
    f = =>
      ix = (ix+1)%3
      @setState({ix})
      v = [null, true, false][ix]
      onChange(v)
    return h Checkbox, {
      checked: ix == 1
      indeterminate: ix == 0
      onChange: f
      rest...
    }

class DateInput extends Component
  render: ->
    h DateRangePicker

class InputForType extends Component
  render: ->
    {type, value, update, name} = @props
    updateSt = (val)->
      if val == ""
        cset = {$unset: [name]}
      else
        cset = {[name]: {$set: val}}
      update(cset)

    if type == 'bool'
      opts = [true, false, null]
      ix = opts.indexOf(value)
      onChange = (checked)->
        checked ?= ""
        updateSt(checked)
      indeterminate = not value?
      return h StatefulCheckbox, {
        onChange
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
      return h DateInput, {}
    console.log type
    return null

STag = styled(Tag)"""
  margin-right: 0.3em;
  margin-bottom: 0.2em;
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

  el = h Card, {
    interactive: not expanded ,
    key: name,
    className,
    onClick
  }, [
    h 'h5.name', name
    h 'div.attributes', attrs
    h('p.description', description) if description?
    details
  ]

Parameter = styled(BaseParameter)"""
  margin-bottom: 1em;
  margin-right: 1em;
  transition: width 0.5s;
  flex-grow: #{(p)->if p.type == 'string' then '2' else '1'};
"""

export {Parameter}
