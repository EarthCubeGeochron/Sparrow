import h from 'react-hyperscript'
import {Component} from 'react'
import {Callout} from '@blueprintjs/core'

class SessionManagerComponent extends Component
  render: ->
    h 'div.data-view#sessions', [
      h Callout, {
        icon: 'info-sign', title: "Analytical session data"
      }, "This view is the core data view for laboratory analytical data"
    ]

export {SessionManagerComponent}
