import h from 'react-hyperscript'
import {Component} from 'react'
import {Callout, Icon, Card} from '@blueprintjs/core'
import {PagedAPIView} from '@macrostrat/ui-components'
import {SessionInfoLink} from './session-component/info-card'

class SessionListComponent extends Component
  @defaultProps: {
    apiEndpoint: '/api/v1/session'
  }
  render: ->
    {apiEndpoint} = @props

    h 'div.data-view#session-list', [
      h Callout, {
        icon: 'info-sign',
        title: "Analytical sessions"
      }, "This page contains the core data view for laboratory analytical data"
      h PagedAPIView, {
        className: 'data-frame'
        route: apiEndpoint
        topPagination: true
        bottomPagination: false
        perPage: 10
      }, (data)->
        h 'div', null, data.map (d)-> h(SessionInfoLink, d)
    ]

export {SessionListComponent}
