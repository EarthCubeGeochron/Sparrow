import h from 'react-hyperscript'
import {Component} from 'react'

import {NonIdealState, Button, Intent} from '@blueprintjs/core'
import {SiteTitle} from 'app/shared/util'
import {AuthContext} from 'app/auth/context'
import {AdminBase} from './base'

class AdminWrapper extends Component
  @contextType: AuthContext
  renderNotLoggedIn: ->
    {requestLoginForm} = @context
    console.log @context
    onClick = ->
      console.log "Clicked"
      requestLoginForm()
    h NonIdealState, {
      title: "Not logged in"
      description: "You must be authenticated to use the administration interface."
      icon: 'blocked-person'
      action: h Button, {onClick}, "Login"
    }

  render: ->
    {login} = @context
    console.log @context
    if not login
      return @renderNotLoggedIn()
    h AdminBase


ProjectPage = ->
  h 'div', [
    h SiteTitle, {subPage: 'Admin'}
    h AdminWrapper
  ]

export {ProjectPage}
