import { FormattedMessage } from "react-intl";

export function App() {
  return (
    <main>
      <h1>
        <FormattedMessage
          id="app.titulo"
          defaultMessage="Cabos Sueltos"
          description="Título principal del sitio, en el encabezado"
        />
      </h1>
    </main>
  );
}
