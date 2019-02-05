import h from 'react-hyperscript'
import {Component} from 'react'
import {Callout, Icon} from '@blueprintjs/core'
import {PagedAPIView} from '@macrostrat/ui-components'
import {parse,format} from 'date-fns'

Sample = (props)->
  h 'div.sample', [
    h 'h5.info', 'Sample'
    h 'div.sample-id', props.id
    h 'div.target', props.target
  ]


SessionComponent = (props)->
  {id, sample_id, target} = props
  console.log props

  date = parse(props.date)

  h 'div.session.bp3-card', {key: id}, [
    h 'h4.date', format(date, 'dddd, MMMM Do, YYYY')
    h 'div.session-info', [
      h Sample, {id: sample_id, target}
      h 'div.project', [
        h 'h5.info', 'Project'
        h 'div', null, props.project_id or "—"
      ]
      h 'div.instrument', [
        h 'h5.small-info', 'Instrument'
        h 'div', props.instrument_name
      ]
      h 'div.technique', [
        h 'h5.small-info', 'Technique'
        h 'div', props.technique
      ]
      h 'div.group', [
        h 'h5.small-info', 'Group'
        h 'div', props.measurement_group_id
      ]
    ]
  ]

class SessionManagerComponent extends Component
  @defaultProps: {
    apiEndpoint: '/api/v1/session'
  }
  render: ->
    {apiEndpoint} = @props

    h 'div.data-view#sessions', [
      h Callout, {
        icon: 'info-sign', title: "Analytical session data"
      }, "This page contains the core data view for laboratory analytical data"
      h PagedAPIView, {className: 'data-frame', route: apiEndpoint, perPage: 10}, (data)->
        h 'div', null, data.map (d)-> h(SessionComponent, d)
    ]

export {SessionManagerComponent}
