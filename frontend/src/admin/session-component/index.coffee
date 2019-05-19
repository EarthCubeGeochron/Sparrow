import h from 'react-hyperscript'
import {Component} from 'react'
import {Breadcrumbs, Button, Intent} from '@blueprintjs/core'
import {Link} from 'react-router-dom'
import {Frame} from 'app/frame'

import {GeoDeepDiveCard} from './gdd-card'
import {SessionInfoCard} from './info-card'
import {APIResultView} from '@macrostrat/ui-components'

class SessionComponent extends Component
  render: ->
    {id} = @props
    return null unless id?
    console.log id

    breadCrumbs = [
      { text: h(Link, {to: '/admin/session'}, "Analytical Sessions") },
      { icon: "document", text: h('code.session-id', id) }
    ]

    h 'div.data-view#session', [
      h Breadcrumbs, {items: breadCrumbs}
      h APIResultView, {
        route: "/session"
        params: {id, private: true}
      }, (data)=>
        res = data[0]
        {sample_id} = res
        h 'div', [
          h SessionInfoCard, res
          h Frame, {id: 'sessionDetail', session_id: id}, (
            h 'div', "This is where a session detail component would go"
          )
          h Button, {icon: 'document', intent: Intent.PRIMARY}, "Get data file"
          h GeoDeepDiveCard, {sample_id}
        ]
    ]

export {SessionComponent}
