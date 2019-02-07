import h from 'react-hyperscript'
import {Component} from 'react'
import {Breadcrumbs} from '@blueprintjs/core'
import {Link} from 'react-router-dom'

import {GeoDeepDiveCard} from './gdd-card'
import {SessionInfoCard} from './info-card'
import {APIResultView} from '@macrostrat/ui-components'

class SessionComponent extends Component
  render: ->
    {id} = @props

    breadCrumbs = [
      { text: h(Link, {to: '/admin/session'}, "Analytical Sessions") },
      { icon: "document", text: h('code.session-id', id) }
    ]

    h 'div.data-view#session', [
      h Breadcrumbs, {items: breadCrumbs}
      h APIResultView, {
        route: "/session"
        params: {id}
      }, (data)=>
        res = data[0]
        {sample_id} = res
        h 'div', [
          h SessionInfoCard, res
          h Button, {icon: 'file', intent: Intent.PRIMARY}, "Get data file"
          h GeoDeepDiveCard, {sample_id}
        ]
    ]

export {SessionComponent}
