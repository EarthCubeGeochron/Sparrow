import h from 'react-hyperscript'
import {Component} from 'react'
import {NonIdealState, Intent, Button, ButtonGroup, Icon} from '@blueprintjs/core'
import {Route, Switch} from 'react-router-dom'
import classNames from 'classnames'

import {AuthContext} from 'app/auth/context'
import {ProjectListComponent} from './project-component'
import {SessionListComponent} from './session-list-component'
import {AgeChartComponent} from './age-component'
import {SessionComponent} from './session-component'
import {AppNavbar, NavButton} from 'app/shared/navbar'

AdminNavbar = ({base, rest...})->
  h AppNavbar, {rest, subtitle: 'Admin'}, [
    h NavButton, {to: base, icon: 'home'}
    h NavButton, {to: base+'/session'}, "Data"
    h NavButton, {to: base+'/project'}, "Projects"
  ]

SessionMatch = ({match})->
  {id} = match.params
  h SessionComponent, {id}

LoginRequired = (props)->
  {requestLoginForm} = props
  onClick = ->
    console.log "Clicked"
    requestLoginForm()
  h NonIdealState, {
    title: "Not logged in"
    description: "You must be authenticated to use the administration interface."
    icon: 'blocked-person'
    action: h Button, {onClick}, "Login"
  }

class AdminBody extends Component
  @contextType: AuthContext
  render: ->
    {login, requestLoginForm} = @context
    if not login
      return h LoginRequired, {requestLoginForm}

    {base} = @props
    # Render main body
    h Switch, [
      h Route, {
        path: base+"/session/:id"
        component: SessionMatch
      }
      h Route, {
        path: base+"/session"
        component: SessionListComponent
      }
      h Route, {
        path: base+"/project"
        component: ProjectListComponent
      }
      h Route, {
        path: base
        component: AgeChartComponent
        exact: true
      }
    ]

class Admin extends Component
  render: ->
    {match} = @props
    base = match.path
    h 'div#labdata-admin', [
      h AdminNavbar, {base}
      h AdminBody, {base}
    ]

export {Admin}
