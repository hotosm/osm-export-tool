const path = require('path');

const webpack = require('webpack');

const config = {
  entry: './app/hdx/base.jsx',
  output: {
    path: path.resolve(__dirname, 'static', 'ui', 'js'),
    filename: 'bundle.js'
  },
  devtool: 'eval',
  module: {
    loaders: [
      {
        test: /app\/.*\.jsx?$/,
        exclude: [/node_modules/],
        loader: 'babel-loader',
        query: {
          presets: ['es2015', 'react', 'stage-0']
        }
      },
      {
        test: /app.*\.css$/,
        loader: 'style-loader',
        exclude: [/node_modules/]
      },
      {
        test: /app.*\.css$/,
        loader: 'css-loader',
        query: {
          modules: true,
          localIdentName: '[name]__[local]___[hash:base64:5]'
        },
        exclude: [/node_modules/]
      },
      {
        test: /\.css$/,
        loaders: ['style-loader', 'css-loader'],
        include: [/node_modules/]
      }
    ],
    noParse: /dist\/ol.js/
  },
  resolve: {
    extensions: ['', '.js', '.jsx', '.json', '.css']
  }
};

if (process.NODE_ENV === 'production') {
  config.devtool = 'source-map';
  config.plugins = [
    new webpack.optimize.OccurenceOrderPlugin(),
    new webpack.NoErrorsPlugin(),
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify('production')
      }
    }),
    new webpack.optimize.UglifyJsPlugin()
  ];
}

module.exports = config;
