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
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: `gatsby-starter-default`,
        short_name: `starter`,
        start_url: `/`,
        background_color: `#663399`,
        theme_color: `#663399`,
        display: `minimal-ui`,
        icon: `src/images/gatsby-icon.png`, // This path is relative to the root of the site.
      },
    },
    // this (optional) plugin enables Progressive Web App + Offline functionality
    // To learn more, visit: https://gatsby.dev/offline
    // `gatsby-plugin-offline`,
  ],
}
