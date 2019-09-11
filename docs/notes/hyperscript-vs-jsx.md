# Hyperscript syntax
h 'div', [
  h 'h4', "#{data.length} measurements have been linked to their geologic metadata"
  h MapComponent, {markers}
]

# JSX syntax
<div>
  <h4>{"#{data.length} measurements have been linked to their geologic metadata"}</h4>
  <MapComponent markers={markers}></MapComponent>
</div>
