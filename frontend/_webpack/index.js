let path = require("path");
const { EnvironmentPlugin } = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const BrowserSyncPlugin = require("browser-sync-webpack-plugin");

const isDev = process.env.SPARROW_ENV == "development";
const mode = isDev ? "development" : "production";
console.log(`Bundling frontend for ${mode}`);

// Create HTML template configuration
let htmlConfig = {
  title: process.env.SPARROW_LAB_NAME,
  favicon: relativePath("static/img/favicon.png"),
};
if (isDev) {
  htmlConfig.template = relativePath("_webpack/dev-template.ejs");
}

process.env["BASE_URL"] =
  process.env.API_BASE_URL || process.env.SPARROW_BASE_URL;
/* BrowserSync allows us to automatically reload the Sparrow frontend in development */

function relativePath(...tokens) {
  return path.resolve(__dirname, "..", ...tokens);
}

let assetsDir = relativePath("_assets");
let srcRoot = relativePath("src");

let assetsRoute = process.env.SPARROW_BASE_URL || process.env.BASE_URL;

let baseConfig = {
  mode,
  watch: isDev,
  module: {
    rules: require("./loaders"),
  },
  devtool: "source-map",
  resolve: {
    // Resolve node modules from Sparrow's own node_modules if not found in plugins
    modules: ["_local_modules", "node_modules", relativePath("node_modules")],
    extensions: [
      ".ts",
      ".tsx",
      ".coffee",
      ".js",
      ".jsx",
      ".styl",
      ".css",
      ".html",
      ".md",
    ],
    alias: {
      "~": srcRoot,
      app: srcRoot,
      sparrow: srcRoot,
      plugins: relativePath("plugins/"),
      "site-content": process.env.SPARROW_SITE_CONTENT,
      // For node module resolution + hooks
      react: relativePath("node_modules", "react"),
    },
  },
  entry: {
    index: relativePath("src/index.ts"),
  },
  stats: {
    colors: true,
  },
  output: {
    path: assetsDir,
    publicPath: assetsRoute,
    filename: "[name].js",
  },
  // Always split chunks
  // We could turn this off in development if we wanted.
  // https://medium.com/hackernoon/the-100-correct-way-to-split-your-chunks-with-webpack-f8a9df5b7758
  optimization: {
    splitChunks: {
      chunks: "all",
    },
  },
  plugins: [
    new HtmlWebpackPlugin(htmlConfig),
    new EnvironmentPlugin(["BASE_URL", "SPARROW_LAB_NAME", "MAPBOX_API_TOKEN"]),
  ],
};

// Add browserSync plugin if we are in dev mode.
if (isDev) {
  const domain = `localhost:${process.env.SPARROW_HTTP_PORT || "5002"}`;
  console.log(`Running browserSync at ${domain}`);
  let browserSync = new BrowserSyncPlugin({
    open: false,
    logSnippet: false,
    logLevel: "silent",
    socket: {
      domain,
    },
  });

  baseConfig.plugins.push(browserSync);
}

module.exports = baseConfig;
