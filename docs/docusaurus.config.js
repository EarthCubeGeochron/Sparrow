module.exports = {
  title: 'Sparrow',
  tagline: 'An open-source laboratory information management system focused on geochronology.',
  url: 'https://sparrow-data.org',
  baseUrl: '/',
  favicon: 'img/favicon.png',
  organizationName: 'EarthCubeGeochron', // Usually your GitHub org/user name.
  projectName: 'Sparrow', // Usually your repo name.
  themeConfig: {
    navbar: {
      title: 'Sparrow',
      logo: {
        alt: 'Sparrow logo',
        src: 'img/sparrow-bird-flat.svg',
      },
      links: [
        {
          to: 'docs/index',
          activeBasePath: 'docs',
          label: 'Docs',
          position: 'left',
        },
        {to: 'blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/EarthCubeGeochron/Sparrow',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Index',
              to: 'docs/index.md',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Blog',
              to: 'blog',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/EarthCubeGeochron/Sparrow',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} EarthCube Geochronology Frontiers team.`,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl:
            'https://github.com/EarthCubeGeochron/Sparrow/edit/master/docs/',
        },
        blog: {
          showReadingTime: false,
          // Please change this to your repo.
          editUrl:
            'https://github.com/EarthCubeGeochron/Sparrow/edit/master/docs/blog/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  plugins: [
    require.resolve('./plugins/webpack-extensions.js')
  ]
};
