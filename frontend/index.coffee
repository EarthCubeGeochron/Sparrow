import '@blueprintjs/core/lib/css/blueprint.css'
import './shared/ui-main.styl'
import ix from 'site-content/index.md'
import {render} from 'react-dom'
import h from 'react-hyperscript'
import {SiteTitle} from './shared/util'
import React from 'react'

SiteNav = ->
  <nav class='site-nav'>
    <ul>
      <li><a class="nav-link bp3-button bp3-minimal" href='/admin/'>Admin</a></li>
      <li><a class="nav-link bp3-button bp3-minimal" href='/api-explorer'>API Explorer</a></li>
      <li><a class="nav-link bp3-button bp3-minimal" href='/dz-samples'>Detrital Zircon Samples</a></li>
    </ul>
  </nav>

App = ->
  h 'div', [
    h SiteTitle
    h SiteNav
    h 'div', {dangerouslySetInnerHTML: {__html: ix}}
  ]

el = document.querySelector("#container")
render(h(App), el)
