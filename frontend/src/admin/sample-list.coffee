import {Component} from 'react'
import h from 'react-hyperscript'
import {PagedAPIView} from '@macrostrat/ui-components'
import {SampleCard} from './sample/detail-card'

class SampleList extends Component
  render: ->
    h PagedAPIView, {
      route: '/sample_data'
      perPage: 10
      topPagination: true
    }, (data)=>
      h 'div', null, data.map (d)->h(SampleCard, d)

export {SampleList}
