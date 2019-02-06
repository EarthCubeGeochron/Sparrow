import h from 'react-hyperscript'
import {Component} from 'react'
import {Navbar, Button, ButtonGroup, Icon} from '@blueprintjs/core'
import {NavLink, Route, Switch} from 'react-router-dom'
import cfg from 'site-content/variables'
import classNames from 'classnames'

import {ProjectListComponent} from './project-component'
import {SessionListComponent} from './session-list-component'
import {AgeChartComponent} from './age-component'
import {SessionComponent} from './session-component'

LinkButton = (props)->
  {to, className, children, rest...} = props
  className = classNames className, "link-button", "bp3-button", "bp3-minimal"
  activeClassName = classNames className, "bp3-active"
  h NavLink, {to, className, activeClassName, rest...}, children

AdminNavbar = ({base})->
  h Navbar, [
    h Navbar.Group, [
      h Navbar.Heading, [
        h 'h1.site-title', [
          h NavLink, {to: '/'}, "#{cfg.siteTitle}"
          ":"
          h 'span.subtitle', "Admin"
        ]
      ]
      h Navbar.Divider
      h LinkButton, {to: base, exact: true}, h(Icon, {icon: 'home'})
      h LinkButton, {to: base+'/session'}, "Data"
      h LinkButton, {to: base+'/project'}, "Projects"
    ]
  ]

SessionMatch = ({match})->
  {id} = match.params
  h SessionComponent, {id}

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
          component: SessionListComponent
        }
        h Route, {
          path: base+"/project"
          component: ProjectListComponent
        }
        h Route, {
          path: base+"/session/:id"
          component: SessionMatch
        }
        h Route, {
          path: base
          component: AgeChartComponent
          exact: true
        }
      ]
    ]

export {AdminBase}
