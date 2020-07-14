import content from '/build/schema.html'
import React from 'react'

export const SchemaPage = ()=>{
  return <div className="schema" dangerouslySetInnerHTML={{__html: content}}></div>
}
