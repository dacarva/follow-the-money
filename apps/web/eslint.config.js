import js from "@eslint/js";
import formatjs from "eslint-plugin-formatjs";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist", "node_modules"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    plugins: {
      react,
      "react-hooks": reactHooks,
      formatjs,
    },
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
    },
    settings: {
      react: { version: "detect" },
    },
    rules: {
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      ...formatjs.configs.recommended.rules,
      "react/react-in-jsx-scope": "off",
      // Literal strings are errors in JSX children and props (aria-label,
      // placeholder, title...). Only FormattedMessage may take literal props,
      // because its id/defaultMessage/description are the catalog entry.
      "react/jsx-no-literals": [
        "error",
        {
          noStrings: true,
          ignoreProps: false,
          allowedStrings: [],
          elementOverrides: {
            FormattedMessage: { ignoreProps: true },
          },
        },
      ],
    },
  },
  {
    files: ["**/*.test.{ts,tsx}", "src/test/**/*.{ts,tsx}", "*.config.{ts,js}"],
    rules: {
      "react/jsx-no-literals": "off",
    },
  },
);
