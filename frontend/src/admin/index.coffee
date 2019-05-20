import h from 'react-hyperscript'
import {Component} from 'react'
import {NonIdealState, Intent, Button, ButtonGroup, Icon} from '@blueprintjs/core'
import {Route, Switch} from 'react-router-dom'
import classNames from 'classnames'

import {LinkButton} from '@macrostrat/ui-components'
import {Frame} from 'app/frame'
import {AuthContext} from 'app/auth/context'
import {ProjectListComponent} from './project-component'
import {SessionListComponent} from './session-list-component'
import {SessionComponent} from './session-component'
import {AppNavbar, NavButton} from 'app/shared/navbar'
import {InsetText} from 'app/layout'
import styled from '@emotion/styled'

MinimalNavbar = styled.div"""
display: flex;
flex-direction: row;
align-items: baseline;
margin: 0.5em 0 1em;
padding: 0.3em 1em;
background-color: #f5f8fa;
border-radius: 6px;
vertical-align: baseline;
box-shadow: 0px 1px 0.5px 0px rgba(138,155,168,0.75);

h4 {
  margin: 0;
  padding: 0.1em 1em 0.1em 0.4em;
  color: #5c7080;
  min-width: 5em;
}
"""

HomeButton = styled(LinkButton)"""
margin-right: 1em;
vertical-align: baseline;
baseline-shift: -4px;
"""

AdminNavbar = ({base, rest...})->
  h MinimalNavbar, {rest, subtitle: 'Admin'}, [
    h 'h4', "Admin views"
    #h HomeButton, {to: base, icon: 'home', minimal: true}
    h NavButton, {to: base, exact: true }, "Base"
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

AdminMain = (props)->
  h Frame, {id: 'adminBase', props...}, (
    h InsetText, "An admin base component goes here"
  )

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
        component: AdminMain
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
