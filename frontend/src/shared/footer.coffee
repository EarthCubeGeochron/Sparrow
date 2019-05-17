import h from 'react-hyperscript'
import {Component} from 'react'
import {Frame} from 'sparrow/frame'
import {Markdown} from '@macrostrat/ui-components'
import {InsetText} from 'app/layout'
import footerText from './footer-text.md'

PageFooter = (props)->
  h Frame, {id: 'pageFooter'}, (
    h InsetText, [
      h Markdown, {src: footerText}
    ]
  )

export {PageFooter}
