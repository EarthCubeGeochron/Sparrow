import h from 'react-hyperscript'
import {StatefulComponent} from '@macrostrat/ui-components'
import {Component, createContext} from 'react'
import {Button} from '@blueprintjs/core'
import {LoginForm} from './login-form'
import './main.styl'

AuthContext = createContext({})

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
      h LoginForm, {isOpen: isLoggingIn, onClose}
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
