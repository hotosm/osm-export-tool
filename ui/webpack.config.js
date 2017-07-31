const path = require("path");

const webpack = require("webpack");
const WriteFilePlugin = require("write-file-webpack-plugin");

const config = {
  entry: [
    "babel-polyfill",
    "react-hot-loader/patch",
    "webpack-dev-server/client?http://localhost:8080",
    "./app/index.js"
  ],
  output: {
    path: path.resolve(__dirname, "static", "ui", "js"),
    filename: "bundle.js",
    publicPath: "/static/ui/js/"
  },
  devtool: "eval",
  module: {
    rules: [
      {
        test: /app\/.*\.jsx?$/,
        exclude: [/node_modules/],
        loader: "babel-loader",
        query: {
          plugins: [
            "react-hot-loader/babel",
            [
              "react-intl",
              {
                messagesDir: "./app/i18n/messages/"
              }
            ]
          ],
          presets: [
            [
              "env",
              {
                modules: false,
                targets: {
                  browsers: ["last 2 versions", "> 5%"]
                },
                useBuiltIns: true
              }
            ],
            "react",
            "stage-2"
          ]
        }
      },
      {
        test: /app.*\.css$/,
        loader: "style-loader"
      },
      {
        test: /app\/styles\/.*\.css$/,
        use: [
          {
            loader: "css-loader",
            options: {
              modules: true
            }
          }
        ]
      },
      {
        test: /app\/css\/.*\.css$/,
        use: [
          {
            loader: "css-loader"
          }
        ]
      },
      {
        test: /\.css$/,
        use: [
          {
            loader: "style-loader"
          },
          {
            loader: "css-loader"
          }
        ],
        include: [/node_modules/]
      },
      {
        test: /\.(png|woff|woff2|eot|ttf|svg)$/,
        use: [
          {
            loader: "url-loader?limit=100000"
          }
        ]
      }
    ]
  },
  plugins: [new webpack.DefinePlugin({
    "process.env": {
      CLIENT_ID: JSON.stringify(process.env.CLIENT_ID),
      EXPORTS_API_URL: JSON.stringify(process.env.EXPORTS_API_URL)
    }
  }), new webpack.NamedModulesPlugin(), new WriteFilePlugin()],
  resolve: {
    extensions: [".js", ".jsx", ".json", ".css"]
  }
};

if (process.env.NODE_ENV === "production") {
  config.entry = ["babel-polyfill", "./app/index.js"];
  config.devtool = "source-map";
  config.plugins = [
    new webpack.NoEmitOnErrorsPlugin(),
    new webpack.DefinePlugin({
      "process.env": {
        CLIENT_ID: JSON.stringify(process.env.CLIENT_ID),
        EXPORTS_API_URL: JSON.stringify(process.env.EXPORTS_API_URL),
        NODE_ENV: JSON.stringify("production")
      }
    }),
    new webpack.optimize.ModuleConcatenationPlugin(),
    new webpack.optimize.UglifyJsPlugin({
      sourceMap: true,
      warnings: true
    })
  ];
}

module.exports = config;
