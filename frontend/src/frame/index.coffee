import {StatefulComponent} from '@macrostrat/ui-components'
import {Component, createContext} from 'react'
import {ErrorBoundary} from '../util'
import T from 'prop-types'

FrameContext = createContext({})

class FrameProvider extends StatefulComponent
  @propTypes: {
    overrides: T.objectOf(node)
  }
  @defaultProps: {overrides: {}}
  constructor: (props)->
    @state = {registry: {}}
  render: ->
    {register: @register, getContent: @getContent}
    h FrameContext.Provider, {value}, @props.children

  getElement: (id)->
    {overrides} = @props
    return overrides[id] or null

class Frame extends Component
  @contextType: FrameContext
  @propTypes: {
    id: T.string.isRequired
    iface: T.object
    children: T.element
    rest: T.object
  }
  render: ->
    {id, iface, children, rest} = @props
    el = @context.getElement(id)
    child = if el? then el else children
    h ErrorBoundary, null, h(child, rest)

export {FrameProvider, Frame}
