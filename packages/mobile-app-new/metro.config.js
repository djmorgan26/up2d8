const {getDefaultConfig, mergeConfig} = require('@react-native/metro-config');
const path = require('path');

/**
 * Metro configuration
 * https://reactnative.dev/docs/metro
 *
 * @type {import('metro-config').MetroConfig}
 */

const config = {
  projectRoot: __dirname,
  watchFolders: [
    path.resolve(__dirname, '../../node_modules'),
    path.resolve(__dirname, '../shared-types'),
    path.resolve(__dirname, '../shared-api'),
    path.resolve(__dirname, '../shared-theme'),
    path.resolve(__dirname, '../shared-utils'),
  ],
  resolver: {
    nodeModulesPaths: [
      path.resolve(__dirname, 'node_modules'),
      path.resolve(__dirname, '../../node_modules'),
    ],
    extraNodeModules: {
      '@up2d8/shared-types': path.resolve(__dirname, '../shared-types/src'),
      '@up2d8/shared-api': path.resolve(__dirname, '../shared-api/src'),
      '@up2d8/shared-theme': path.resolve(__dirname, '../shared-theme/src'),
      '@up2d8/shared-utils': path.resolve(__dirname, '../shared-utils/src'),
    },
  },
  transformer: {
    getTransformOptions: async () => ({
      transform: {
        experimentalImportSupport: false,
        inlineRequires: true,
      },
    }),
  },
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);
