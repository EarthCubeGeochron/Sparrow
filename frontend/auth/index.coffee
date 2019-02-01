import h from 'react-hyperscript'
import {SiteTitle} from 'app/shared/util'
import {StatefulComponent} from '@macrostrat/ui-components'
import {Component, createContext} from 'react'
import {Button} from '@blueprintjs/core'
import './main.styl'

AuthContext = createContext({})

class AuthProvider extends StatefulComponent
  constructor: ->
    super arguments...
    @state = {
      logged_in: false
    }

  login: =>
    @updateState {logged_in: {$set: true}}
  render: =>
    value = {@state..., login: @login}
    h AuthContext.Provider, {value}, @props.children

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

export * from './login-page'
export {AuthStatus}
