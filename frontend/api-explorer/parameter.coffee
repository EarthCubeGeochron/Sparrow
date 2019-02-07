import styled from '@emotion/styled'
import h from 'react-hyperscript'
import ReactMarkdown from 'react-markdown'
import {Tag, Card} from '@blueprintjs/core'

BaseParameter = (props)->
  {name, type, default: defaultArg, description, usage} = props

  if usage?
    usage = h ReactMarkdown, {source: usage}

  if type == 'boolean'
    type = 'bool'

  attrs = [
    h Tag, type
  ]

  if description? and description.startsWith("Column")
    description = null
    attrs.push h Tag, "column"

  if defaultArg?
    attrs.push h Tag, "default: #{defaultArg}"


  el = h Card, {interactive: true, key: name, className: 'argument'}, [
    h 'h5.name', name
    h 'div.attributes', attrs
    h('p.description', description) if description?
    usage
  ]

Parameter = styled(BaseParameter)"""
  max-width: #{(p)->if p.expanded then '40em' else '20em'};
  flex-grow: 1;
"""

export {Parameter}
