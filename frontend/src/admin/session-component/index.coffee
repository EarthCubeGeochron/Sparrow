import h from 'react-hyperscript'
import {Component} from 'react'
import {Breadcrumbs, Button, AnchorButton, Intent} from '@blueprintjs/core'
import {Link} from 'react-router-dom'
import {Frame} from 'app/frame'

import {SessionInfoCard} from './info-card'
import {SessionDetailPanel} from './detail-panel'
import {APIResultView} from '@macrostrat/ui-components'

class DownloadButton extends Component
  render: ->
    {file_hash, file_type} = @props

    text = "Data file"
    if file_type?
      text = h [
        h 'b', file_type
        " file"
      ]

    href = "#{process.env.BASE_URL}data-file/#{file_hash}"
    h AnchorButton, {href, icon: 'document', intent: Intent.PRIMARY}, text

class SessionComponent extends Component
  render: ->
    {id} = @props
    return null unless id?

    breadCrumbs = [
      { text: h(Link, {to: '/catalog/session'}, "Sessions") },
      { icon: "document", text: h('code.session-id', id) }
    ]

    h 'div.data-view#session', [
      h Breadcrumbs, {items: breadCrumbs}
      h APIResultView, {
        route: "/session"
        params: {id}
      }, (data)=>
        res = data[0]
        {sample_name, id, rest...} = res
        h 'div', [
          h SessionInfoCard, res
          h 'div.data-files', [
            h 'h3', 'Data sources'
            h Frame, {id: 'dataFileDownloadButton', rest...}, (props)=>
              h DownloadButton, props
          ]
          h Frame, {id: 'sessionDetail', session_id: id}, (props)=>
            h SessionDetailPanel, props
        ]
    ]

export {SessionComponent}
