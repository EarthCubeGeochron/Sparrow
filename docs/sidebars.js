module.exports = {
  someSidebar: {
    CHECK_THIS_OUT: ["live-code"],
    Guides: [
      "motivation-and-design",
      "getting-started",
      "server-configuration",
      "sparrow-on-windows",
      "datascience/dataSci",
      "schema-imp",
    ],
    Documentation: [
      "introduction",
      "command-line-interface",
      {
        type: "category",
        label: "Frontend",
        items: [
          "frontend/local-dev",
          "frontend/frames",
          "frontend/data-input-form",
        ],
      },
    ],
  },
};

/*
To access subfolders in the docs directory:
just add the name of the folder before the id separated by /

ex)
  docs->
    -> subfolder-name ->
        -> id.mdx

  ["subfolder-name/id"]


To create subfolders in sidebar:
someSidebar: {
    Guides: [
      'guides', {
        type: "category",
        label: "Example Subcategory",
        items: ["id1", "id2", ....]
      },
      "other ids"...,
      ]
}
*/
