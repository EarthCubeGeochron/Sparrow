import h from 'react-hyperscript'
import {Component} from 'react'
import {Navbar, Button, ButtonGroup} from '@blueprintjs/core'
import {NavLink, Route, Switch} from 'react-router-dom'
import cfg from 'site-content/variables'
import classNames from 'classnames'

import {ProjectListComponent} from './project-component'
import {SessionManagerComponent} from './session-component'
import {AgeChartComponent} from './age-component'

LinkButton = (props)->
  {to, className, children} = props
  className = classNames className, "link-button", "bp3-button", "bp3-minimal"
  activeClassName = classNames className, "bp3-active"
  h NavLink, {to, className, activeClassName}, children

AdminNavbar = ({base})->
  h Navbar, [
    h Navbar.Group, [
      h Navbar.Heading, null, (
        h NavLink, {to: base}, "#{cfg.siteTitle} Admin"
      )
      h Navbar.Divider
      h LinkButton, {to: base+'/session'}, "Data"
      h LinkButton, {to: base+'/project'}, "Projects"
    ]
  ]

SessionListComponent = (props)->
  h 'div', "Sessions"

class AdminBase extends Component
  render: ->
    console.log(@props)
    {match} = @props
    base = match.path
    h 'div#labdata-admin', [
      h AdminNavbar, {base}
      h Switch, [
        h Route, {
          path: base+"/session"
          component: SessionManagerComponent
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
    ]

export {AdminBase}
