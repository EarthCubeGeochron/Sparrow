import {Component, createElement} from 'react'
import {hyperStyled} from '@macrostrat/hyper'
import {Card, Colors} from '@blueprintjs/core'
import {LinkCard} from '@macrostrat/ui-components'
import styles from './module.styl'

h = hyperStyled(styles)

SampleCard = (props)->
  {material, id, name, location_name, link} = props
  console.log props
  link ?= true
  component = if link? then LinkCard else Card
  to = "/catalog/sample/#{id}"
  h component, {className: 'sample-card', to}, [
    h 'h4.name', name
    h 'div.location-name', location_name
    h.if(material?) 'div.material', material
  ]

export {SampleCard}
