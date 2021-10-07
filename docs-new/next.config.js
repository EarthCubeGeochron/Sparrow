/** @type {import('next').NextConfig} */
const admonitions = require("remark-admonitions");
const codeblocks = require("remark-code-blocks");
const RevisionInfoWebpack = require("@macrostrat/revision-info-webpack");
const withMDX = require("@next/mdx")({
  options: {
    remarkPlugins: [admonitions, codeblocks],
    rehypePlugins: []
  }
});

const GITHUB_LINK = "https://github.com/EarthCubeGeochron/Sparrow";

let baseConfig = {
  reactStrictMode: true,
  pageExtensions: ["mdx", "ts", "tsx"],
  env: {
    ...RevisionInfoWebpack(null, GITHUB_LINK)
  }
};

module.exports = withMDX(baseConfig);
