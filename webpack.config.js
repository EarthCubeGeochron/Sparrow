let path = require('path');
let BrowserSyncPlugin = require('browser-sync-webpack-plugin');
const { execSync } = require('child_process');

/* Get configuration from labdata backend. This is used
to centralize configuration and specify the location of frontend
components. It could be removed in favor of an environment variable
if desired. This might be necessary if we want frontend development
to be uncoupled from the backend */
let cfg = JSON.parse(execSync("labdata config").toString('utf-8'));

let assetsDir = path.resolve(__dirname, "_assets")
let assetsRoute = '/assets'

let browserSync = new BrowserSyncPlugin({
  port: 3000,
  host: 'localhost',
  proxy: 'http://127.0.0.1:5000',
  serveStatic: [
    {route: assetsRoute, dir: assetsDir}
  ]
});

let jsLoader = {
  loader: 'babel-loader',
  options: {presets: ['@babel/preset-env', '@babel/preset-react']}
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
      {test: /\.md$/, use: ["html-loader","markdown-loader"]}
    ]
  },
  resolve: {
    extensions: [".coffee", ".js", ".styl",".css",".html",".md"],
    alias: {
      "app": path.resolve(__dirname, "frontend/"),
      "site-content": path.resolve(cfg.site_content)
    }
  },
  entry: {
    index: './frontend/index.coffee',
    'api-explorer': './frontend/api-explorer',
    'dz-samples': './frontend-plugins/dz-samples',
    'admin': './frontend/admin'
  },
  output: {
    path: assetsDir,
    publicPath: assetsRoute,
    filename: "[name].js"
  },
  plugins: [ browserSync ]
}
