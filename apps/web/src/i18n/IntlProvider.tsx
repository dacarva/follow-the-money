import type { ReactNode } from "react";
import { IntlProvider as ReactIntlProvider } from "react-intl";

import messages from "./es-CO.json";

const LOCALE = "es-CO";

export function IntlProvider({ children }: { children: ReactNode }) {
  return (
    <ReactIntlProvider
      locale={LOCALE}
      defaultLocale={LOCALE}
      messages={messages}
    >
      {children}
    </ReactIntlProvider>
  );
}
