import js from '@eslint/js'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'
import { globalIgnores } from 'eslint/config'
import pluginVue from 'eslint-plugin-vue'

export default defineConfigWithVueTs(
  globalIgnores([
    '**/dist/**',
    '**/coverage/**',
    '**/playwright-report/**',
    '**/test-results/**',
    '**/node_modules/**',
  ]),

  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },

  js.configs.recommended,
  pluginVue.configs['flat/recommended'],
  vueTsConfigs.recommendedTypeChecked,

  {
    name: 'app/rules',
    rules: {
      // Multi-word component names add noise for view components named after routes.
      'vue/multi-word-component-names': 'off',
      // Redundant under TypeScript, and actively wrong with `exactOptionalPropertyTypes`:
      // an optional prop typed `string | undefined` must be *absent* from withDefaults, not
      // defaulted to `undefined`. The type system already states the contract.
      'vue/require-default-prop': 'off',
      // Prop order and attribute order keep large SFCs scannable.
      'vue/attributes-order': 'error',
      'vue/component-api-style': ['error', ['script-setup']],
      'vue/define-macros-order': ['error', { order: ['defineProps', 'defineEmits'] }],
      'vue/no-unused-refs': 'error',
      // Unused variables are an error, except deliberately ignored args prefixed with _.
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      // `any` defeats the point of the strict tsconfig.
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/consistent-type-imports': [
        'error',
        { prefer: 'type-imports', fixStyle: 'inline-type-imports' },
      ],
      // Floating promises are the most common source of silent failures in Vue apps.
      '@typescript-eslint/no-floating-promises': 'error',
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      eqeqeq: ['error', 'always', { null: 'ignore' }],
    },
  },

  {
    name: 'app/node-scripts',
    files: ['*.config.ts', 'e2e/**/*.ts', 'scripts/**/*.mjs'],
    languageOptions: {
      globals: { console: 'readonly', process: 'readonly' },
    },
    rules: {
      // Config, e2e and build scripts legitimately read process.env and print to stdout —
      // for a CLI check, the console output *is* the interface.
      'no-console': 'off',
    },
  },

  skipFormatting,
)
