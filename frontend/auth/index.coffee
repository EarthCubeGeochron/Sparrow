import h from 'react-hyperscript'
import {StatefulComponent} from '@macrostrat/ui-components'
import {Component, createContext} from 'react'
import {Button, Dialog, Classes, Intent} from '@blueprintjs/core'
import {LoginForm} from './login-form'
import './main.styl'

AuthContext = createContext({})


class LoginDialog extends Component
  render: ->
    {isOpen, onClose} = @props
    title = "Login"
    h Dialog, {isOpen, title, onClose}, [
      h 'div', {className: Classes.DIALOG_BODY}, [
        h LoginForm
      ]
      h 'div', {className: Classes.DIALOG_FOOTER}, [
        h 'div', {className: Classes.DIALOG_FOOTER_ACTIONS}, [
          h Button, {intent: Intent.SUCCESS, large: true}, 'Login'
        ]
      ]
    ]

class AuthProvider extends StatefulComponent
  constructor: ->
    super arguments...
    @state = {
      logged_in: false
      isLoggingIn: false
    }

  login: =>
    @setState {isLoggingIn: true}

  render: =>
    {isLoggingIn, rest...} = @state
    value = {rest..., login: @login}
    onClose = => @setState {isLoggingIn: false}
    h AuthContext.Provider, {value}, [
      h LoginDialog, {isOpen: isLoggingIn, onClose}
      h 'div', null, @props.children
    ]

class AuthStatus extends Component
  @contextType: AuthContext
  render: ->
    {login, logged_in} = @context
    h 'div.auth-status', [
      h Button, {
        minimal: true, large: true,
        icon: 'blocked-person',
        onClick: login}, 'Not logged in'
    ]

export * from './login-form'
export {AuthProvider, AuthStatus}
