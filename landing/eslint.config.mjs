import nextVitals from 'eslint-config-next/core-web-vitals'
import nextTs from 'eslint-config-next/typescript'

const config = [
  ...nextVitals,
  ...nextTs,
  {
    files: ['scripts/**'],
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
    },
  },
]

export default config
