import {Component, createElement} from 'react'
import styled from '@emotion/styled'
import h from 'react-hyperscript'
import {Card, Colors} from '@blueprintjs/core'

GreyCard = styled.div"""
  background-color: #{Colors.LIGHT_GRAY4};
  border-radius: 5px;
  margin: 5px;
  padding: 5px 10px;
  flex-grow: 1;
  max-width: 15em;
  .location-name {
    color: #{Colors.RED1};
  }
  h4 {
    margin-top: 0em;
    margin-bottom: 0em;
  }
"""

Material = styled.div"""font-style: italic"""

SampleCard = (props)->
  {material, sample_id, name, location_name} = props
  if material?
    material = h Material, material

  h GreyCard, {className: 'sample'}, [
    h 'h4.name', name
    h 'div.location-name', location_name
    material
  ]

export {SampleCard}
