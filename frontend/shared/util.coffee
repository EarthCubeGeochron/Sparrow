import h from 'react-hyperscript'
import cfg from 'site-content/variables'
import React from 'react'
import { Link } from "react-router-dom"

SiteNav = ->
  <nav class='site-nav'>
    <ul>
      <li><Link className="nav-link bp3-button bp3-minimal" to='/admin/'>Admin</Link></li>
      <li><Link className="nav-link bp3-button bp3-minimal" to='/api-explorer'>API Explorer</Link></li>
    </ul>
  </nav>

SiteTitle = ({subPage})->
  v = null
  if subPage?
    v = " – #{subPage}"

  h 'h1.site-title', [
    h 'a', {href: '/'}, cfg.siteTitle
    h 'span.subtitle', ' Lab Data Interface'
    v
  ]

export {SiteTitle, SiteNav}
