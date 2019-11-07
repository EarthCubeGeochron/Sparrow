import h from 'react-hyperscript'
import {Component} from 'react'
import {Button} from '@blueprintjs/core'
import {LoginForm} from './login-form'
import {AuthProvider, AuthContext} from './context'
import './main.styl'

class AuthStatus extends Component
  @contextType: AuthContext
  render: ->
    {requestLoginForm, username} = @context
    {className, large, rest...} = @props
    large ?= true

    text = 'Not logged in'
    icon = 'blocked-person'
    if username?
      text = username
      icon = 'person'
    h 'div.auth-status', {className}, [
      h LoginForm
      h Button, {
        minimal: true,
        large
        icon,
        onClick: requestLoginForm}, text
    ]

export * from './login-form'
export {AuthProvider, AuthStatus}
