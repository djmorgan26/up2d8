module.exports = {
  presets: ['module:@react-native/babel-preset'],
  plugins: [
    [
      'module-resolver',
      {
        root: ['./src'],
        extensions: ['.ios.ts', '.android.ts', '.ts', '.ios.tsx', '.android.tsx', '.tsx', '.jsx', '.js', '.json'],
        alias: {
          '@': './src',
          '@components': './src/components',
          '@screens': './src/screens',
          '@navigation': './src/navigation',
          '@hooks': './src/hooks',
          '@context': './src/context',
          '@utils': './src/utils',
          '@theme': './src/theme',
          '@shared/types': '../shared-types/src',
          '@shared/api': '../shared-api/src',
          '@shared/theme': '../shared-theme/src',
          '@shared/utils': '../shared-utils/src',
        },
      },
    ],
    'react-native-reanimated/plugin',
  ],
};
