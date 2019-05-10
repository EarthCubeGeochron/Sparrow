import {StatefulComponent} from '@macrostrat/ui-components'
import {Component, createContext} from 'react'
import {ErrorBoundary} from '../util'
import T from 'prop-types'
import h from 'react-hyperscript'

FrameContext = createContext({})

class FrameProvider extends StatefulComponent
  @propTypes: {
    overrides: T.objectOf(T.node)
  }
  @defaultProps: {overrides: {}}
  constructor: (props)->
    super props
    @state = {registry: {}}
  render: ->
    value = {register: @register, getElement: @getElement}
    h FrameContext.Provider, {value}, @props.children

  getElement: (id)=>
    {overrides} = @props
    return overrides[id] or null

class Frame extends Component
  @contextType: FrameContext
  @propTypes: {
    id: T.string.isRequired
    iface: T.object
    children: T.node
    rest: T.object
  }
  render: ->
    {id, iface, children, rest} = @props
    el = @context.getElement(id)
    child = if el? then el else children
    if typeof child is 'function'
      child = child(rest)

    h ErrorBoundary, null, child

export {FrameProvider, Frame}
