var proxy = require("http-proxy-middleware");

module.exports = {
  siteMetadata: {
    title: "Sparrow",
    description: "A geochronology-focused laboratory information management system",
    author: "Daven Quinn and the EarthCube Geochronology Frontiers team"
  },
  // for development server
  // developMiddleware: app => {
  //   app.use(
  //     "/python-api/",
  //     proxy({
  //       target: "http://127.0.0.1:8001",
  //       pathRewrite: {
  //         "/python-api/": "",
  //       },
  //     })
  //   )
  // },
  plugins: [
    // custom configuration
    `gatsby-mdx`,
    `gatsby-plugin-stylus`,
    `gatsby-plugin-react-helmet`,
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `images`,
        path: `${__dirname}/src/images`,
      },
    },
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        path: `${__dirname}/src/posts`,
        name: "markdown-posts",
      },
    },
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        path: `${__dirname}/src/page-content`,
        name: "markdown-pages",
      },
    },
    {
      resolve: "gatsby-transformer-remark",
      options: {
        plugins: [
          {
            resolve: `gatsby-remark-prismjs`
          }
        ]
      }
    },
    // no configuration
    `gatsby-plugin-coffeescript`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-sharp`,
  ],
}
