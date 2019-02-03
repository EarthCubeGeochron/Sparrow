import h from 'react-hyperscript'
import cfg from 'site-content/variables'
import React from 'react'
import {Icon} from '@blueprintjs/core'
import { Link } from "react-router-dom"

SiteNav = ->
  <nav className='site-nav'>
    <ul>
      <li><Link className="nav-link bp3-button bp3-minimal" to='/admin/'>Admin</Link></li>
      <li><Link className="nav-link bp3-button bp3-minimal" to='/api-explorer'>API Explorer</Link></li>
    </ul>
  </nav>

SiteTitle = ({subPage})->
  if subPage?
    subPage = h 'span.subpage', [":", h('span.inner', subPage)]
  h 'h1.site-title', [
    h Link, {to: '/'}, [
      h 'span.title', cfg.siteTitle
      h 'span.subtitle', 'Lab Data Interface'
    ]
    subPage
  ]

export {SiteTitle, SiteNav}
