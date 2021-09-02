/** @type {import('next').NextConfig} */
const RevisionInfoWebpack = require("@macrostrat/revision-info-webpack");
const withMDX = require("@next/mdx")();

const GITHUB_LINK = "https://github.com/EarthCubeGeochron/Sparrow";

module.exports = withMDX({
  reactStrictMode: true,
  pageExtensions: ["mdx", "ts", "tsx"],
  env: {
    ...RevisionInfoWebpack(null, GITHUB_LINK),
  },
});
