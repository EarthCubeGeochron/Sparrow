import h from 'react-hyperscript'
import cfg from 'site-content/variables'
import React from 'react'

SiteNav = ->
  <nav class='site-nav'>
    <ul>
      <li><a class="nav-link bp3-button bp3-minimal" href='/admin/'>Admin</a></li>
      <li><a class="nav-link bp3-button bp3-minimal" href='/api-explorer'>API Explorer</a></li>
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

export {SiteTitle}
