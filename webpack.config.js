let path = require('path');
let BrowserSyncPlugin = require('browser-sync-webpack-plugin');

let browserSync = new BrowserSyncPlugin({
  port: 3000,
  host: 'localhost',
  proxy: 'http://127.0.0.1:5000'
});

let jsLoader = {loader: 'babel-loader', options: {presets: ['@babel/preset-env']}};

module.exports = {
  module: {
    rules: [
      {test: /\.js$/, use: [jsLoader]},
      {test: /\.coffee$/, use: [ jsLoader, "coffee-loader" ]},
      {test: /\.styl$/, use: ["css-loader", "stylus-loader"]},
      {test: /\.css$/, use: [ 'css-loader' ]}
    ]
  },
  resolve: {
    extensions: [".coffee", ".js", ".styl",".css"]
  },
  entry: {
    index: './labdata/frontend/index.coffee'
  },
  output: {
    path: path.resolve(__dirname, "_assets"),
    publicPath: "/assets/",
    filename: "[name].js"
  },
  plugins: [ browserSync ]
}
