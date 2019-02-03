import h from 'react-hyperscript'
import {APIContext, StatefulComponent} from '@macrostrat/ui-components'
import {Component, createContext} from 'react'
import {Button} from '@blueprintjs/core'
import {LoginForm} from './login-form'
import './main.styl'

AuthContext = createContext({})

class AuthProvider extends StatefulComponent
  @contextType: APIContext
  constructor: ->
    super arguments...
    @state = {
      logged_in: false
      username: null
      isLoggingIn: false
      invalidAttempt: false
      credentials: null
    }

  requestLogin: =>
    @setState {isLoggingIn: true}

  login: (data)=>
    {post} = @context
    results = await post '/auth/login', data
    {accessToken, refreshToken, username} = results
    if not results.username?
      @setState {invalidAttempt: true}
      return
    @setState {
      username,
      credentials: {accessToken, refreshToken},
      isLoggingIn: false
      invalidAttempt: false
    }

  render: =>
    {isLoggingIn, invalidAttempt, rest...} = @state
    login = @login
    value = {rest..., login, requestLogin: @requestLogin}
    onClose = => @setState {isLoggingIn: false}
    h AuthContext.Provider, {value}, [
      h LoginForm, {isOpen: isLoggingIn, invalidAttempt, onClose, login}
      h 'div', null, @props.children
    ]

class AuthStatus extends Component
  @contextType: AuthContext
  render: ->
    {requestLogin, username} = @context
    console.log @context
    text = 'Not logged in'
    icon = 'blocked-person'
    if username?
      text = username
      icon = 'person'
    h 'div.auth-status', [
      h Button, {
        minimal: true, large: true,
        icon,
        onClick: requestLogin}, text
    ]

export * from './login-form'
export {AuthProvider, AuthStatus}
