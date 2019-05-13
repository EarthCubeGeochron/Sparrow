module.exports = {
  siteMetadata: {
    title: "Sparrow",
    description: "A geochronology-focused laboratory information management system",
    author: "Daven Quinn and the EarthCube Geochronology Frontiers team"
  },
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
        path: `${__dirname}/text`,
        name: "markdown-pages",
      },
    },
    `gatsby-transformer-remark`,
    // no configuration
    `gatsby-plugin-coffeescript`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-sharp`,
  ],
}
