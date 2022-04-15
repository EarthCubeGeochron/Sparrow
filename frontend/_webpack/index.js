let path = require("path");
const { EnvironmentPlugin } = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const BrowserSyncPlugin = require("browser-sync-webpack-plugin");

const environment = process.env.SPARROW_ENV || "production";

const isDev = environment != "production";
const mode = isDev ? "development" : "production";
console.log(`Bundling frontend for ${environment}`);

if (environment == "local-development") {
  // Read .env file from local directory
  require("dotenv").config({ path: "./.env" });
}

console.log(process.env);

//process.env.BASE_URL = process.env.API_BASE_URL || process.env.SPARROW_BASE_URL;
/* BrowserSync allows us to automatically reload the Sparrow frontend in development */

function relativePath(...tokens) {
  return path.resolve(__dirname, "..", ...tokens);
}

let assetsDir =
  process.env.SPARROW_FRONTEND_BUILD_DIR || relativePath("_assets");
let srcRoot = relativePath("src");

let assetsRoute = process.env.BASE_URL || "/";

let baseConfig = {
  mode,
  devServer: {
    compress: false,
    port: 3000,
    //hot: true,
    open: true,
    historyApiFallback: true,
  },
  module: {
    rules: require("./loaders"),
  },
  devtool: "source-map",
  resolve: {
    // Resolve node modules from Sparrow's own node_modules if not found in plugins
    // modules: [
    //   "packages",
    //   "_local_modules",
    //   "node_modules",
    //   relativePath("node_modules"),
    // ],
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
      sparrow: path.resolve(srcRoot),
      plugins: relativePath("plugins/"),
      "site-content":
        process.env.SPARROW_SITE_CONTENT || relativePath("default-content"),
      // For node module resolution + hooks
      react: relativePath("node_modules", "react"),
    },
    fallback: { path: false, process: false },
  },
  entry: {
    main: "./src/index.ts",
  },
  stats: {
    colors: true,
  },
  output: {
    path: assetsDir,
    publicPath: assetsRoute,
    filename: "[name].js",
    devtoolModuleFilenameTemplate: "file:///[absolute-resource-path]",
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
    new HtmlWebpackPlugin({
      title: process.env.SPARROW_LAB_NAME,
      favicon: relativePath("static/img/favicon.png"),
    }),
    new EnvironmentPlugin([
      "BASE_URL",
      "API_BASE_URL",
      "SPARROW_LAB_NAME",
      "MAPBOX_API_TOKEN",
      "SPARROW_ENV",
    ]),
  ],
};

// Add browserSync plugin if we are in dev mode.
if (environment == "development") {
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

  baseConfig.watch = true;
  baseConfig.plugins.push(browserSync);
}

module.exports = baseConfig;
