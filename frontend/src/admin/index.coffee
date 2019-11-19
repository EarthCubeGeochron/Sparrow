import {hyperStyled, classed} from '@macrostrat/hyper'
import {Component, useContext} from 'react'
import {NonIdealState, Intent,
        Button, ButtonGroup, Icon, Callout} from '@blueprintjs/core'
import {Switch} from 'react-router-dom'
import {ErrorBoundaryRoute as Route} from 'app/util/route'
import classNames from 'classnames'
import T from 'prop-types'

import {
  LinkButton,
  LinkCard
} from '@macrostrat/ui-components'
import {Frame} from 'app/frame'
import {AuthContext} from 'app/auth/context'
import {ProjectListComponent, ProjectComponent} from './project'
import {SessionListComponent} from './session-list-component'
import {SessionComponent} from './session-component'
import {SampleMain} from './sample'

import {NavButton, MinimalNavbar} from 'app/components/navbar'
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

CatalogNavLinks = ({base, rest...})->
  base ?= '/catalog'
  h [
    h NavButton, {to: base+'/project'}, "Projects"
    h NavButton, {to: base+'/sample'}, "Samples"
    h NavButton, {to: base+'/session'}, "Sessions"
  ]

CatalogNavbar = ({base, rest...})->
  # A standalone navbar for the admin panel, can be enabled by default
  h 'div.minimal-navbar', {rest..., subtitle: 'Admin'}, [
    h 'h4', "Admin"
    h HomeButton, {to: base, exact: true}
    h CatalogNavLinks, {base}
  ]

SessionMatch = ({match})->
  {id} = match.params
  h SessionComponent, {id}

ProjectMatch = ({match})->
  {id} = match.params
  h ProjectComponent, {id}

LoginButton = (props)->
  {requestLoginForm: onClick} = useContext(AuthContext)
  h(Button, {onClick, className: 'login-button', props...}, "Login")

LoginRequired = (props)->
  {requestLoginForm: onClick, rest...} = props
  h NonIdealState, {
    title: "Not logged in"
    description: "You must be authenticated to use the administration interface."
    icon: 'blocked-person'
    action: h(LoginButton)
    rest...
  }

LoginSuggest = ->
  {login, requestLoginForm} = useContext(AuthContext)
  return null if login
  h Callout, {
    title: "Not logged in"
    icon: 'blocked-person',
    intent: 'warning'
    className: 'login-callout'
  }, [
    h 'p', 'Embargoed data and management tools are hidden.'
    h LoginButton, {intent: 'warning', minimal: true}
  ]

AdminMain = (props)->
  h Frame, {id: 'adminBase', props...}, [
    h 'h1', "Catalog"
    h 'div.catalog-index', [
      h InsetText, "The lab's data catalog can be browsed using several entrypoints:"
      h LinkCard, {to: "/project"}, (
        h 'h2', "Projects"
      )
      h LinkCard, {to: "/sample"}, (
        h 'h2', "Samples"
      )
      h LinkCard, {to: "/session"}, (
        h 'h2', "Sessions"
      )
    ]
  ]

CatalogBody = ({base})->
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
      path: base+"/project/:id"
      component: ProjectMatch
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

Catalog = ({base})->
  h 'div.catalog', [
    h LoginSuggest
    h CatalogBody, {base}
  ]

class Admin extends Component
  # A login-required version of the catalog
  @contextType: AuthContext
  @propTypes: {
    base: T.string.isRequired
  }
  render: ->
    {base} = @props
    {login, requestLoginForm} = @context
    if not login
      return h LoginRequired, {requestLoginForm}

    h 'div.admin', [
      h CatalogBody, {base}
    ]

export {Catalog, CatalogNavLinks}
