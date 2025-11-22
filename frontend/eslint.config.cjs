const { FlatCompat } = require('@eslint/eslintrc')

const compat = new FlatCompat({
    baseDirectory: __dirname,
})

module.exports = [
    ...compat.extends('react-app', 'react-app/jest'),
    {
        rules: {
            semi: ['error', 'never'],
            '@typescript-eslint/semi': ['error', 'never'],
        },
    },
]
