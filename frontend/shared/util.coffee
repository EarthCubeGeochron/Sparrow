import h from 'react-hyperscript'
import cfg from '../config'

SiteTitle = ({subPage})->
  v = null
  if subPage?
    v = " – #{subPage}"

  h 'h1', [
    h 'a', {href: '/'}, cfg.siteTitle
    v
  ]

export {SiteTitle}
