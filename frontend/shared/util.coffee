import h from 'react-hyperscript'
import cfg from 'site-content/variables'

SiteTitle = ({subPage})->
  v = null
  if subPage?
    v = " – #{subPage}"

  h 'h1.site-title', [
    h 'a', {href: '/'}, cfg.siteTitle
    h 'span.subtitle', ' Lab Data Interface'
    v
  ]

export {SiteTitle}
