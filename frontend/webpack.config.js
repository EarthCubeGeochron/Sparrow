let path = require("path");
const { EnvironmentPlugin } = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const { symlinkSync } = require("fs");

const environment = process.env.SPARROW_ENV || "production";

const isDev = environment != "production";
const mode = isDev ? "development" : "production";
console.log(`Bundling frontend for ${environment}`);

if (environment == "local-development") {
  // Read .env file from local directory
  require("dotenv").config({ path: "./.env" });
}

//process.env.BASE_URL = process.env.API_BASE_URL || process.env.SPARROW_BASE_URL;
/* BrowserSync allows us to automatically reload the Sparrow frontend in development */

function relativePath(...tokens) {
  return path.resolve(__dirname, ...tokens);
}

const devDomain = `localhost:${process.env.SPARROW_HTTP_PORT || "5002"}`;

let assetsDir =
  process.env.SPARROW_FRONTEND_BUILD_DIR || relativePath("_assets");
let srcRoot = relativePath("src");

let assetsRoute = process.env.BASE_URL || "/";

console.log("Base URL:", assetsRoute);

let fontLoader = {
  loader: "file-loader",
  options: { name: "fonts/[name].[ext]" },
};

// Link site content into frontend cache directory
const siteContent =
  process.env.SPARROW_SITE_CONTENT || relativePath("default-content");
let contentDir = relativePath(".yarn/cache/site-content");
symlinkSync(siteContent, contentDir, "dir");

// Remember that, counterintuitively, loaders load bottom-to-top
const styleRules = [
  {
    test: /\.(styl|css)$/,
    use: "style-loader",
  },
  // CSS compilation supporting local CSS modules
  {
    test: /\.(styl|css)$/,
    oneOf: [
      // Match css modules (.module.(css|styl) files)
      {
        test: /\.?module\.(css|styl)$/,
        use: {
          loader: "css-loader",
          options: {
            /* CSS Module support with local scope by default
       This means that module support needs to be explicitly turned
       off with a `:global` flag
    */
            modules: {
              mode: "local",
              localIdentName: "[path][name]__[local]--[hash:base64:5]",
            },
          },
        },
        exclude: /node_modules/,
      },
      {
        test: /\.(styl|css)$/,
        use: "css-loader",
      },
    ],
  },
  // Fallback for raw CSS and stylus from node_modules
  { test: /\.styl$/, use: "stylus-relative-loader" },
];

let devServer = {
  compress: false,
  port: 3000,
  hot: true,
  // Don't try to open a browser window
  open: false,
  historyApiFallback: true,
};

if (environment != "local-development") {
  // Prepare for docker
  // Make hot-reload listener look for a web server at the same proxy address
  // as the rest of the app.
  devServer = {
    ...devServer,
    webSocketURL: `ws://${devDomain}/ws`,
    // Docker host needs to be able to access the served app
    host: "0.0.0.0",
  };
}

let baseConfig = {
  mode,
  devServer,
  // Might be useful for docker?
  // watchOptions: {
  //   aggregateTimeout: 300,
  //   poll: 1000,
  // },
  // Resolve local PNP modules
  module: {
    rules: [
      ...styleRules,
      { test: /\.coffee$/, use: ["babel-loader", "coffee-loader"] },
      {
        test: /\.(js|jsx|ts|tsx)$/,
        use: "babel-loader",
        exclude: /node_modules/,
      },
      {
        // Rule for 'modern' javascript
        type: "javascript/auto",
        test: /\.mjs$/,
        use: [],
      },
      { test: /\.(eot|svg|ttf|woff|woff2)$/, use: [fontLoader] },
      { test: /\.md$/, use: ["html-loader", "markdown-loader"] },
      { test: /\.html$/, use: ["html-loader"] },
      {
        test: /\.(png|jpe?g|gif)$/i,
        use: [
          {
            loader: "file-loader",
            options: {
              useRelativePath: true,
            },
          },
        ],
      },
    ],
  },
  devtool: "source-map",
  resolve: {
    // Resolve node modules from Sparrow's own node_modules if not found in plugins
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
      "site-content": contentDir,
      // For node module resolution + hooks
      //react: relativePath("node_modules", "react"),
    },
    // Allow us to resolve site-content plugin directory
    symlinks: false,
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

console.log(`Running frontend at ${devDomain}`);

// if (environment == "development" || environment == "local-development") {
//   baseConfig.watch = true;
// }

module.exports = baseConfig;
