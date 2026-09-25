import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import { IntlProvider } from "./i18n/IntlProvider";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("root element not found");
}

createRoot(rootElement).render(
  <StrictMode>
    <IntlProvider>
      <App />
    </IntlProvider>
  </StrictMode>,
);
