let path = require("path");
let BrowserSyncPlugin = require("browser-sync-webpack-plugin");
const { execSync } = require("child_process");
const { readFileSync } = require("fs");
const { EnvironmentPlugin } = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");

process.env["BASE_URL"] =
  process.env.API_BASE_URL || process.env.SPARROW_BASE_URL;

let assetsDir = path.resolve(__dirname, "_assets");
let siteContent = process.env.SPARROW_SITE_CONTENT;

console.log("Base url:", process.env.BASE_URL);
console.log("Site content:", siteContent);

let assetsRoute = process.env.SPARROW_BASE_URL || process.env.BASE_URL;

console.log(process.env.BASE_URL, process.env.API_BASE_URL);

let bs_cfg = {
  open: false,
  // These don't appear to work?
  logLevel: "silent",
  logSnippet: false,
  single: true,
  // Actual external port
  port: 3000,
  //proxy: "http://backend:5000"
  // socket: {
  //   // Client-side port for socket IO
  //   port: process.env.SPARROW_HTTP_PORT
  // }
  socket: {
    domain: "localhost:5002",
  },
};

// if (!process.env.CONTAINERIZED) {
//   // Configuration for running locally
//   // This configuration is probably wrong
//bs_cfg.serveStatic = [{ route: assetsRoute, dir: assetsDir }];
bs_cfg.server = "./_assets";
//}

let browserSync = new BrowserSyncPlugin(bs_cfg);

let fontLoader = {
  loader: "file-loader",
  options: { name: "fonts/[name].[ext]" },
};

let stylusLoader = {
  loader: "stylus-relative-loader",
};

const cssModuleLoader = {
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
};

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
        use: cssModuleLoader,
        exclude: /node_modules/,
      },
      {
        test: /\.(styl|css)$/,
        use: "css-loader",
      },
    ],
  },
  // Fallback for raw CSS and stylus from node_modules
  { test: /\.styl$/, use: stylusLoader },
];

const babelLoader = {
  loader: "babel-loader",
  // options: {
  //   presets: [
  //     "@babel/preset-env",
  //     "@babel/preset-react",
  //     "@babel/preset-typescript"
  //   ],
  //   plugins: [
  //     "emotion",
  //     "@babel/plugin-proposal-nullish-coalescing-operator",
  //     "@babel/plugin-proposal-optional-chaining",
  //     "@babel/plugin-proposal-class-properties"
  //   ]
  // }
};

module.exports = {
  module: {
    rules: [
      ...styleRules,
      { test: /\.coffee$/, use: [babelLoader, "coffee-loader"] },
      { test: /\.(js|jsx|ts|tsx)$/, use: babelLoader, exclude: /node_modules/ },
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
    // Resolve node modules from local directory if not found in plugins
    modules: ["node_modules", path.resolve(__dirname, "node_modules/")],
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
      "~": path.resolve(__dirname, "src/"),
      app: path.resolve(__dirname, "src/"),
      sparrow: path.resolve(__dirname, "src/"),
      plugins: path.resolve(__dirname, "plugins/"),
      "site-content": siteContent,
    },
  },
  entry: {
    index: "./src/index.ts",
  },
  stats: {
    chunks: false,
  },
  output: {
    path: assetsDir,
    publicPath: assetsRoute,
    filename: "[name].js",
  },
  // Always split chunks
  // We could turn this off in development if we wanted.
  // https://medium.com/hackernoon/the-100-correct-way-to-split-your-chunks-with-webpack-f8a9df5b7758
  //optimization: {
  //splitChunks: {
  //chunks: 'all',
  //},
  //},
  plugins: [
    new HtmlWebpackPlugin({ title: process.env.SPARROW_LAB_NAME }),
    browserSync,
    new EnvironmentPlugin([
      "NODE_ENV",
      "DEBUG",
      "BASE_URL",
      "SPARROW_LAB_NAME",
      "MAPBOX_API_TOKEN",
    ]),
  ],
};
