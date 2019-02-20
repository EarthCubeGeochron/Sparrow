import h from 'react-hyperscript'
import {Component} from 'react'
import {Navbar, Button, ButtonGroup, Icon} from '@blueprintjs/core'
import {NavLink, Route, Switch} from 'react-router-dom'
import cfg from 'site-content/variables'
import classNames from 'classnames'
import {LinkButton} from '@macrostrat/ui-components'

import {ProjectListComponent} from './project-component'
import {SessionListComponent} from './session-list-component'
import {AgeChartComponent} from './age-component'
import {SessionComponent} from './session-component'
import {AppNavbar} from 'app/shared/navbar'

AdminNavbar = ({base, rest...})->
  h AppNavbar, {rest, subtitle: 'Admin'}, [
    h LinkButton, {to: base, exact: true}, h(Icon, {icon: 'home'})
    h LinkButton, {to: base+'/session'}, "Data"
    h LinkButton, {to: base+'/project'}, "Projects"
  ]

SessionMatch = ({match})->
  {id} = match.params
  h SessionComponent, {id}

class AdminBase extends Component
  render: ->
    {match} = @props
    base = match.path
    h 'div#labdata-admin', [
      h AdminNavbar, {base}
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
    ]

export {AdminBase}
