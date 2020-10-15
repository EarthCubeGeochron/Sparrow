module.exports = {
  someSidebar: {
    Guides: [
      "guides",
      "motivation-and-design",
      "getting-started",
      "server-configuration", // not loading
      "sparrow-on-windows",
      "datascience/dataSci",
      "schema-imp", // not loading
    ],
    Documentation: [
      "introduction",
      "command-line-interface",
      "frontend/local-dev",
      "frontend/frames",
    ],
  },
};

/*
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
