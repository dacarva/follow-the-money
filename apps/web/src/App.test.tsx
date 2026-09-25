import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";
import { IntlProvider } from "./i18n/IntlProvider";

describe("App", () => {
  it("renders the catalog title inside main", () => {
    render(
      <IntlProvider>
        <App />
      </IntlProvider>,
    );

    const main = screen.getByRole("main");
    expect(main).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Cabos Sueltos" }),
    ).toBeInTheDocument();
  });
});
