import {hyperStyled, classed} from '@macrostrat/hyper'
import {Component} from 'react'
import {NonIdealState, Intent, Button, ButtonGroup, Icon} from '@blueprintjs/core'
import {Route, Switch} from 'react-router-dom'
import classNames from 'classnames'
import T from 'prop-types'

import {LinkButton} from '@macrostrat/ui-components'
import {Frame} from 'app/frame'
import {AuthContext} from 'app/auth/context'
import {ProjectListComponent} from './project-component'
import {SessionListComponent} from './session-list-component'
import {SessionComponent} from './session-component'
import {SampleMain} from './sample'

import {AppNavbar, NavButton} from 'app/shared/navbar'
import {InsetText} from 'app/layout'
import styled from '@emotion/styled'
import styles from './module.styl'

h = hyperStyled(styles)

HomeButton = (props)->
  h LinkButton, {
    className: "home-link-button"
    icon: "home"
    minimal: true
    props...
  }

AdminNavLinks = ({base, rest...})->
  h [
    h NavButton, {to: base+'/project'}, "Projects"
    h NavButton, {to: base+'/sample'}, "Samples"
    h NavButton, {to: base+'/session'}, "Sessions"
  ]

AdminNavbar = ({base, rest...})->
  # A standalone navbar for the admin panel, can be enabled by default
  h 'div.minimal-navbar', {rest..., subtitle: 'Admin'}, [
    h 'h4', "Admin"
    h HomeButton, {to: base, exact: true}
    h AdminNavLinks, {base}
  ]

SessionMatch = ({match})->
  {id} = match.params
  h SessionComponent, {id}

LoginRequired = (props)->
  {requestLoginForm: onClick, rest...} = props
  h NonIdealState, {
    title: "Not logged in"
    description: "You must be authenticated to use the administration interface."
    icon: 'blocked-person'
    action: h(Button, {onClick}, "Login")
    rest...
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
        path: base+"/sample"
        component: SampleMain
      }
      h Route, {
        path: base
        component: AdminMain
        exact: true
      }
    ]

class Admin extends Component
  # An admin component that is nested
  # and access-controlled beneath the root
  @propTypes: {
    base: T.string.isRequired
  }
  render: ->
    {base} = @props
    h 'div#labdata-admin', [
      h AdminNavbar, {base}
      h AdminBody, {base}
    ]

export {Admin}
