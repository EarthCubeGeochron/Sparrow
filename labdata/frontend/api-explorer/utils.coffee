import h from 'react-hyperscript'
import {Button, Intent} from '@blueprintjs/core'

nullIfError = (fn)-> ->
  # Returns null if the function returns an
  # error...useful for creating React component trees
  try
    return fn.apply(@, arguments)
  catch error
    console.log "Ignored '#{error}'', returning null"
    return null

Argument = (props)->
  {name, type, default: defaultArg, description} = props
  console.log name, type
  h 'div.argument.bp3-card.bp3-interactive', {key: name}, [
    h 'h5.name', [
      name+" "
      h 'span.type.bp3-code', type
    ]
    h('p.description', description) if description?
    h('p.default', "Default: #{defaultArg}") if defaultArg?
  ]

JSONToggle = ({showJSON, onChange})->
  return [
    h Button, {
      rightIcon: 'list',
      minimal: true,
      key: 'hide-json'
      intent: if not showJSON then Intent.PRIMARY else null
      onClick: -> onChange {showJSON: false}
    }, 'Summary'
    h Button, {
      rightIcon: 'code',
      minimal: true,
      key: 'show-json'
      intent: if showJSON then Intent.PRIMARY else null
      onClick: -> onChange {showJSON: true}
    }, 'JSON'
  ]

export {nullIfError, Argument, JSONToggle}
