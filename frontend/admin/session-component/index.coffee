import h from 'react-hyperscript'
import {Component} from 'react'
import {Breadcrumbs} from '@blueprintjs/core'
import {Link} from 'react-router-dom'

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
        route: "/api/v1/session"
        params: {id}
      }, (data)=>
        h SessionInfoCard, data[0]
    ]

export {SessionComponent}
