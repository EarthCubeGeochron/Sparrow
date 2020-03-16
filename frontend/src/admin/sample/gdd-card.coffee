import h from 'react-hyperscript'
import styled from '@emotion/styled'
import {Component} from 'react'
import {Callout, Icon, Card, NonIdealState} from '@blueprintjs/core'
import {CollapsePanel, APIResultView,
        LinkCard} from '@macrostrat/ui-components'
import './gdd-card.styl'

Snippet = ({html})->
  __html = html
  console.log __html
  h 'p.snippet', {dangerouslySetInnerHTML: {__html}}

SnippetResult = (props)->
  {title, pubname, publisher, coverDate,
   authors, highlight, URL} = props
  h LinkCard, {href: URL, target: '_blank', className: 'snippet-result'}, [
    h 'h2.title', title
    h 'h3.authors', authors
    h 'h3.pub-info', [
      h 'span.pubname', pubname
      " — "
      h 'span.publisher', publisher
    ]
    h 'h4.date', coverDate
    h 'div.snippets', highlight.map (d)->
      h Snippet, {html: d}
  ]

SnippetList = (props)=>
  {items} = props
  if items.length == 0
    return h NonIdealState, {
      icon: 'search'
      title: "No results found"
    }
  return h 'div.snippet-list', null, items.map (d)->
    h SnippetResult, d

ResultsPanel = styled.div"""
  display: flex;
  flex-direction: row;
  margin: 0 -0.5em;
  &>div {
    margin: 0 0.5em;
  }
  .snippet-list {
    margin: 0.5em 0.5em;
  }
"""

InfoCallout = styled(Callout)"""
  width: 20em;
"""

class GeoDeepDiveCard extends Component
  render: ->
    {sample_name} = @props
    route = 'https://geodeepdive.org/api/v1/snippets'
    params = {term: sample_name}
    h CollapsePanel, {title: "GeoDeepDive results", storageID: 'gdd-results'}, (
      h ResultsPanel, [
        h InfoCallout, {
          icon: 'book'
          title: 'Snippets containing sample name'
        }, [
          h 'p', "The GeoDeepDive API can be used to aid
                  the linking of sample names to their containing
                  publications"
        ]
        h APIResultView, {route, params}, (res)=>
          {success: {data}} = res
          h SnippetList, {items: data}
      ]
    )


export {GeoDeepDiveCard}
