---
id: frames
title: Frames
sidebar_label: Frames
---

Frames are the main way for a lab to customize the frontend, user interface of sparrow. Sparrow's Frames will render default content, however override content can be provided and the frame will render that instead. Each Frame in the codebase has an unique **id** that corresponds to a specific place on the U.I. Most frames are rendered directly as react elements; however, some (like `mapStyles`) are optional data you can pass for specific U.I enhancements. For instance, `mapStyles` requires an array of objects that list a chosen name and valid mapbox style.

```
mapStyles: [
    {
      name: "Topographic Map",
      style: "mapbox://styles/jczaplewski/cjftzyqhh8o5l2rqu4k68soub",
    },
    {
      name: "Satellite Map",
      style: "mapbox://styles/jczaplewski/cjeycrpxy1yv22rqju6tdl9xb",
    },
  ]
```

To have Sparrow render the frontend plugin in a frame 5 things must happen:

- The [sparrow-config](/docs/getting-started) file must have a set environmental variable for `SPARROW_SITE_CONTENT`
- The frontend plugin must be exported from the directory that corresponds to that environmental variable.
- The plugin is matched to the correct unique text id that corresponds to a valid frame.
- The plugin must be valid and working without errors
- The plugin must be renderable on the browser and exportable from a JS or TS file.
  - javascript, coffeescript, typescript, react, etc

Current unique frame id's include:

- `siteTitle`: Lab name that will appear on Sparrow
- `landingText`: Text to appear on the Homepage of Sparrow, generally a description of the lab
- `landingGraphic`: Other component to be rendered on Hompage of Sparrow, defaults to globe.
- `mapStyles`: Array of objects that have name and mapystyle (valid mapbox style)
- `projectPage`: React element (class or functional component) that is rendered on project page
- `samplePage`: React element (class or functional component) that is rendered on sample page
- `sessionDetails`: React element (class or functional component) that is rendered on session page
- `datafilePage`: React element (class or functional component) that is rendered on project page
- `sampleCardContent`: Content to show on the sample model card
- `projectCardContent`: Content to show on the project model card
- `publicationCardContent`: Content to show on the publication model card
- `researcherCardContent`: Content to show on the researcher model card
- `sessionCardContent` : Content to show on the session model card
- `datafileCardContent`: Content to show on the datafile model card

Most Frames can recieve `props` which will usually be data from the model where the specific Frame is being rendered. [`props`](https://reactjs.org/docs/components-and-props.html) is a fundamental concept in react.

```
samplePage: (props) => {
    const { defaultContent, ...rest } = props;
    return h(MyFrontendPlugin, rest);
  },
```

Here is an example of a component listed in the `SPARROW_SITE_CONTENT` directory with the Frame id of `samplePage`. In the first line the code is taking in `props` which are deconstructed in the second line into `defaultContent` and `...rest`, which will be the rest of the `props` passed besides `defualtContent`. In the third line of the code, `rest` is being passed to `MyFrontendPlugin` so the data can be access in the plugin component.


