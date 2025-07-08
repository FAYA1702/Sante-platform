# Templates de Notification - Plateforme Santé IA

## 1. Notification Email - Alerte IA
**Objet :** Alerte santé critique détectée

**Corps :**
Bonjour {{nom}},

Une alerte critique a été détectée pour votre compte :

- **Date :** {{date}}
- **Type d'alerte :** {{niveau}}
- **Message :** {{message}}

Veuillez vous reconnecter à votre appareil et consulter votre tableau de bord pour plus de détails.

Cordialement,
L’équipe Santé IA

---

## 2. Notification Push - Recommandation
**Titre :** Nouvelle recommandation santé

**Message :**
Bonjour {{nom}}, votre recommandation santé est prête : {{contenu}}.

Ouvrez l’application pour voir tous les détails.

---

## 3. Notification SMS - Alerte IA
**Message SMS :**
Alerte santé ({{niveau}}) : {{message}} à {{date}}. Veuillez vérifier l’app.

---

*Variables disponibles :* `{{nom}}`, `{{date}}`, `{{niveau}}`, `{{message}}`, `{{contenu}}`
