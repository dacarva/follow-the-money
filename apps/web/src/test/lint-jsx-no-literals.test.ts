import { ESLint } from "eslint";
import { describe, expect, it } from "vitest";

describe("jsx-no-literals lint rule", () => {
  it("fails a literal JSX string", async () => {
    const eslint = new ESLint();
    const [result] = await eslint.lintText(
      "export function Bad() {\n  return <p>Hola</p>;\n}\n",
      { filePath: "src/__fixture_bad.tsx" },
    );

    expect(result.errorCount).toBeGreaterThan(0);
  });

  it("fails a literal string in a prop such as aria-label", async () => {
    const eslint = new ESLint();
    const [result] = await eslint.lintText(
      'export function Bad() {\n  return <button aria-label="Cerrar" />;\n}\n',
      { filePath: "src/__fixture_bad_prop.tsx" },
    );

    expect(result.errorCount).toBeGreaterThan(0);
  });

  it("passes the same text through FormattedMessage", async () => {
    const eslint = new ESLint();
    const [result] = await eslint.lintText(
      'import { FormattedMessage } from "react-intl";\n' +
        "export function Good() {\n" +
        "  return (\n" +
        "    <FormattedMessage\n" +
        '      id="saludo.hola"\n' +
        '      defaultMessage="Hola"\n' +
        '      description="Saludo de bienvenida"\n' +
        "    />\n" +
        "  );\n" +
        "}\n",
      { filePath: "src/__fixture_good.tsx" },
    );

    expect(result.errorCount).toBe(0);
  });
});
