let path = require('path');
let BrowserSyncPlugin = require('browser-sync-webpack-plugin');
const { execSync } = require('child_process');
const { readFileSync } = require('fs');
const { EnvironmentPlugin } = require('webpack');

process.env['BASE_URL'] = process.env.SPARROW_BASE_URL;

let assetsDir = path.resolve(__dirname, "_assets");
let siteContent = process.env.SPARROW_SITE_CONTENT;

let assetsRoute = path.join(process.env.SPARROW_BASE_URL,'/assets');

let bs_cfg = {
  open: false,
  port: 3000,
  socket: {
    domain: "https://sparrow-data.org/labs/wiscar"
  }
};

if(!process.env.CONTAINERIZED) {
  // This configuration is probably wrong
  bs_cfg.proxy = "http://0.0.0.0:5000"
  bs_cfg.serveStatic = [
    {route: assetsRoute, dir: assetsDir}
  ];
  bs_cfg.server = "./";
}

let browserSync = new BrowserSyncPlugin(bs_cfg);

let jsLoader = {
  loader: 'babel-loader',
  options: {
    presets: ['@babel/preset-env', '@babel/preset-react'],
    plugins: ["emotion"]
  }
};

let fontLoader = {
  loader: 'file-loader',
  options: {name: "fonts/[name].[ext]"}
};

let stylusLoader = {
  loader: 'stylus-relative-loader'
};

module.exports = {
  module: {
    rules: [
      {test: /\.coffee$/, use: [ jsLoader, "coffee-loader" ]},
      {test: /\.(js|jsx)$/, use: [ jsLoader ], exclude: /node_modules/ },
      {test: /\.styl$/, use: ["style-loader", "css-loader", stylusLoader]},
      {test: /\.css$/, use: ["style-loader", 'css-loader' ]},
      {test: /\.(eot|svg|ttf|woff|woff2)$/, use: [fontLoader]},
      {test: /\.md$/, use: ["html-loader","markdown-loader"]},
      {test: /\.html$/, use: ["html-loader"]}
    ]
  },
  devtool: 'source-map',
  resolve: {
    extensions: [".coffee", ".js", ".styl",".css",".html",".md"],
    alias: {
      "app": path.resolve(__dirname, "src/"),
      "sparrow": path.resolve(__dirname, "src/"),
      "plugins": path.resolve(__dirname, "plugins/"),
      "site-content": siteContent
    }
  },
  entry: {
    index: './src/index.coffee'
  },
  output: {
    path: assetsDir,
    publicPath: assetsRoute,
    filename: "[name].js"
  },
  plugins: [
    browserSync,
    new EnvironmentPlugin(['NODE_ENV', 'DEBUG', 'BASE_URL', 'SPARROW_LAB_NAME', 'MAPBOX_API_TOKEN'])
  ]
}
