/** @type {import('next').NextConfig} */
const admonitions = require("remark-admonitions");
const codeblocks = require("remark-code-blocks");
const RevisionInfoWebpack = require("@macrostrat/revision-info-webpack");
const withMDX = require("@next/mdx")({
  options: {
    remarkPlugins: [admonitions, codeblocks],
    rehypePlugins: [],
  },
});

const GITHUB_LINK = "https://github.com/EarthCubeGeochron/Sparrow";

let baseConfig = {
  reactStrictMode: true,
  pageExtensions: ["mdx", "ts", "tsx"],
  env: {
    //...RevisionInfoWebpack(null, GITHUB_LINK),
  },
  typescript: {
    // !! WARN !!
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    // !! WARN !!
    ignoreBuildErrors: true,
  },
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
  async rewrites() {
    return [
      {
        source: "/images/:path*",
        destination: "https://sparrow-data.org/images/:path*", // Proxy to Backend
      },
      {
        source: "/media/:path*",
        destination: "https://sparrow-data.org/media/:path*", // Proxy to Backend
      },
    ];
  },
};

module.exports = withMDX(baseConfig);
