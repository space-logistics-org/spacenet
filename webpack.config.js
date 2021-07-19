const path = require('path');

const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MomentLocalesPlugin = require('moment-locales-webpack-plugin');
const MomentTimezoneDataPlugin = require('moment-timezone-data-webpack-plugin');

module.exports = {
  context: __dirname,
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js'
  },
  mode: 'production',
  module: {
      rules: [{
          test: /\.css$/,
          use: [ 'style-loader', 'css-loader' ]
      }, {
          test: /\.(png|gif|jpg|jpeg)$/,
          use: [{
              loader: 'file-loader',
              options: {
                name: '[name].[ext]',
                outputPath: './images/',
                publicPath: './images'
              }
          }]
      }, {
          test: /\.(ico)$/,
          use: [{
              loader: 'file-loader',
              options: {
                name: '[name].[ext]',
                outputPath: './',
                publicPath: './'
              }
          }]
      }, {
          test: /\.(xml|io)$/,
          use: [{
              loader: 'file-loader',
              options: {
                name: '[name].[ext]',
                outputPath: './files/',
                publicPath: './files'
              }
          }]
      }, {
          test: /.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
          use: [{
              loader: 'file-loader',
              options: {
                name: '[name].[ext]',
                outputPath: './fonts/',
                publicPath: './fonts'
              }
          }]
      }]
  },
  plugins: [
      new HtmlWebpackPlugin({
          template: 'src/index.html'
      }),
      new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery'
      }),
      new MomentLocalesPlugin(),
      new MomentTimezoneDataPlugin({
          matchZones: 'Etc/UTC'
      })
  ]
};
