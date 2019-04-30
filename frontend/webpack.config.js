let path = require('path');
let BrowserSyncPlugin = require('browser-sync-webpack-plugin');
const { execSync } = require('child_process');
const { readFileSync } = require('fs');

/* Get configuration from labdata backend. This is used
to centralize configuration and specify the location of frontend
components. It could be removed in favor of an environment variable
if desired. This might be necessary if we want frontend development
to be uncoupled from the backend */

const {SPARROW_CONFIG_JSON} = process.env;
let cfg;
if(SPARROW_CONFIG_JSON) {
  cfg = readFileSync(SPARROW_CONFIG_JSON, 'utf-8');
  console.log(cfg);
} else {
  cfg = execSync("sparrow config").toString('utf-8');
}
cfg = JSON.parse(cfg);

let assetsDir = path.resolve(__dirname, "_assets");
let assetsRoute = '/labs/wiscar/assets';

let bs_cfg = {
  port: 3000,
  host: 'localhost',
  proxy: 'http://0.0.0.0:5000',
  open: false,
  serveStatic: [
    {route: assetsRoute, dir: assetsDir}
  ]
};

if(process.env.CONTAINERIZED) {
  delete bs_cfg.proxy;
  bs_cfg.host = "0.0.0.0";
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
      {test: /\.md$/, use: ["html-loader","markdown-loader"]}
    ]
  },
  resolve: {
    extensions: [".coffee", ".js", ".styl",".css",".html",".md"],
    alias: {
      "app": path.resolve(__dirname, "src/"),
      "site-content": path.resolve(cfg.site_content)
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
  plugins: [ browserSync ]
}
