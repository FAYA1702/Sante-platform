/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_MODE: string;
  // ajoutez d’autres variables si besoin
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
