# Génération des diagrammes

Pour exporter tous les diagrammes Mermaid en PNG et PDF, procédez comme suit :

## Prérequis
- Node.js installé
- Installer mermaid-cli globalement :

```powershell
npm install -g @mermaid-js/mermaid-cli
```

## Génération des exports
Ouvrez PowerShell à la racine du projet et lancez :

```powershell
$files = @("diagramme_cas_utilisation.mmd", "diagramme_classes.mmd", "diagramme_activites.mmd", "diagramme_sequence.mmd", "diagramme_erd.mmd", "diagramme_architecture_microservices.mmd")
foreach ($f in $files) {
  $name = [System.IO.Path]::GetFileNameWithoutExtension($f)
  mmdc -i $f -o "$name.png"
  mmdc -i $f -o "$name.pdf"
}
```

Les fichiers PNG et PDF seront générés dans ce dossier.
