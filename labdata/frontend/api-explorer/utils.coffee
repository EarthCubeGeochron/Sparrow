import h from 'react-hyperscript'

nullIfError = (fn)-> ->
  # Returns null if the function returns an
  # error...useful for creating React component trees
  try
    return fn.apply(@, arguments)
  catch error
    console.log "Ignored '#{error}'', returning null"
    return null

Argument = (props)->
  {name, type, default: defaultArg, description} = props
  console.log name, type
  h 'div.argument.bp3-card', {key: name}, [
    h 'h5.name', [
      name+" "
      h 'span.type.bp3-code', type
    ]
    h('p.description', description) if description?
    h('p.default', "Default: #{defaultArg}") if defaultArg?
  ]

export {nullIfError, Argument}
