import {Component} from 'react'
import hyper from '@macrostrat/hyper'
import {Callout} from '@blueprintjs/core'
import {PagedAPIView, LinkCard} from '@macrostrat/ui-components'
import {FilterListComponent} from 'app/components/filter-list'
import {SampleCard} from './detail-card'
import styles from './module.styl'

h = hyper.styled(styles)

SampleListCard = (props)->
  {material, id, name, location_name} = props
  h LinkCard, {
    to: "/catalog/sample/#{id}"
    key: id,
    className: 'sample-list-card'
  }, [
    h 'h4', [
      "Sample "
      h 'span.name', name
    ]
    h 'div.location-name', location_name
    h.if(material?) 'div.material', material
  ]

SampleList = ->
  route = '/sample'
  filterFields = {
    'name': "Sample name"
    'material': "Material"
    'project_name': "Project"
  }

  h 'div.data-view.sample-list', [
    h Callout, {
      icon: 'info-sign',
      title: "Samples"
    }, "This page lists all samples indexed in the laboratory data system."
    h FilterListComponent, {
      route,
      filterFields,
      itemComponent: SampleListCard
    }
  ]

export {SampleList}
