import h from 'react-hyperscript'
import {Button, Intent} from '@blueprintjs/core'

nullIfError = (fn)-> ->
  # Returns null if the function returns an
  # error...useful for creating React component trees
  try
    return fn.apply(@, arguments)
  catch error
    return null

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

export {nullIfError, JSONToggle}
