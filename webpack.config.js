let path = require('path');
let BrowserSyncPlugin = require('browser-sync-webpack-plugin');

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

let jsLoader = {loader: 'babel-loader', options: {presets: ['@babel/preset-env']}};
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
      {test: /\.js$/, use: [jsLoader]},
      {test: /\.coffee$/, use: [ jsLoader, "coffee-loader" ]},
      {test: /\.styl$/, use: ["style-loader", "css-loader", stylusLoader]},
      {test: /\.css$/, use: ["style-loader", 'css-loader' ]},
      {test: /\.(eot|svg|ttf|woff|woff2)$/, use: [fontLoader]}
    ]
  },
  resolve: {
    extensions: [".coffee", ".js", ".styl",".css"]
  },
  entry: {
    index: './labdata/frontend/index.coffee',
    'api-explorer': './labdata/frontend/api-explorer'
  },
  output: {
    path: assetsDir,
    publicPath: assetsRoute,
    filename: "[name].js"
  },
  plugins: [ browserSync ]
}
