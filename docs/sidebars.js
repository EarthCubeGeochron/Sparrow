module.exports = {
  someSidebar: {
    Guides: [
      "guides",
      "getting-started",
      "motivation-and-design",
      "datascience",
      "schema-imp",
      "embargo",
    ],
    Resources: ["presentations", "implementations"],
    Documentation: [
      "introduction",
      {
        type: "category",
        label: "Core application",
        items: [
          "command-line-interface",
          "core/server-configuration",
          "core/extensions",
        ],
      },
      "schema",
      {
        type: "category",
        label: "Frontend",
        items: [
          //"frontend/frames",
          "frontend/data-input-form",
        ],
      },
      "sparrow-on-windows",
      "local-development",
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
