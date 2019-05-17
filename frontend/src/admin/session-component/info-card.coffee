import h from 'react-hyperscript'
import {Card} from '@blueprintjs/core'
import {LinkCard} from '@macrostrat/ui-components'
import {parse,format} from 'date-fns'

Sample = (props)->
  h 'div.sample', [
    h 'h5.info', 'Sample'
    h 'div.sample-id', props.id
    h 'div.target', props.target
  ]

Instrument = ({instrument_name})->
  return null unless instrument_name?
  h 'div.instrument', [
    h 'h5.small-info', 'Instrument'
    h 'div',instrument_name
  ]

Technique = ({technique})->
  return null unless technique?
  h 'div.technique', [
    h 'h5.small-info', 'Technique'
    h 'div', technique
  ]

MeasurementGroup = ({measurement_group_id})->
  return null unless measurement_group?
  h 'div.group', [
    h 'h5.small-info', 'Group'
    h 'div', measurement_group_id
  ]

SessionInfoComponent = (props)->
  {id, sample_id, target} = props
  date = parse(props.date)
  console.log props

  h 'div', [
    h 'div.top', [
      h 'h4.date', format(date, 'dddd, MMMM Do, YYYY')
      h 'div.expander'
    ]
    h 'div.session-info', [
      h Sample, {id: sample_id, target}
      h 'div.project', [
        h 'h5.info', 'Project'
        h 'div', null, props.project_name or "—"
      ]
      h Instrument, props
      h Technique, props
      h MeasurementGroup, props
    ]
  ]

SessionInfoLink = (props)->
  {id} = props
  h LinkCard, {
    to: "/admin/session/#{id}"
    key: id,
    className: 'session-info-card'
  }, (
    h SessionInfoComponent, props
  )

SessionInfoCard = (props)->
  {id} = props
  h Card, {
    key: id,
    className: 'session-info-card'
  }, (
    h SessionInfoComponent, props
  )


export {SessionInfoComponent, SessionInfoLink, SessionInfoCard}
