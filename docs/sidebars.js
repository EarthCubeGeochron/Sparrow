module.exports = {
  someSidebar: {
    //CHECK_THIS_OUT: ["live-code"],
    Guides: [
      "motivation-and-design",
      "getting-started",
      "datascience/data-sci",
      "schema-imp",
      "embargo-mgmt",
    ],
    Resources: ["presentations"],
    Documentation: [
      "introduction",
      {
        type: "category",
        label: "Core application",
        items: [
          "command-line-interface",
          "sparrow-on-windows",
          "backend/server-configuration",
          "backend/environment-vars",
        ],
      },
      {
        type: "category",
        label: "Frontend",
        items: [
          "frontend/local-dev",
          //"frontend/frames",
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
