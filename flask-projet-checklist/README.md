# 📋 Checklist Pro – Application Flask

## 🎯 Objectif pédagogique

Créer une application web légère avec Flask permettant à un utilisateur :

- de créer ses propres modèles de checklists personnalisées,
- de remplir ces checklists (coche, commentaires...),
- de consulter un historique des checklists remplies.

---

## 🛠️ Fonctionnalités attendues

### 1. Création de modèles de checklist

- Chaque modèle contient :
  - un **nom**
  - une liste d'**items** (ex : "Port du casque", "Feux allumés", ...)

### 2. Remplissage d'une checklist

- L'utilisateur coche les éléments réalisés
- Il peut ajouter un **commentaire libre**, mais ce n'est pas obligatoire
- La saisie est horodatée et enregistrée

### 3. Historique

- Liste chronologique des checklists remplies
- Affichage :
  - Label de l'item avec le statut de validation : ✅ (si coché) / ❌ (si non coché)
  - Date + nom du modèle
  - Commentaire éventuel

---

## 📁 Structure minimale imposée

```plaintext
/
├── app.py
├── data/
│   ├── templates.json       # modèles de checklists
│   └── history.json         # historique rempli
├── templates/
│   ├── ...                  # les templates (vues)
└── README.md
```

---

## ⚙️ Contraintes techniques

- ⚙️ **Flask** uniquement (pas Django, ni framework full-stack pour le moment)
- 🧠 Pas de base de données dans la première version : on travaille avec des fichiers `.json`
- 📄 Fichiers de données lisibles (pas de binaire)
- 💡 Utilisez un kit UI pour faire en sorte de rendre le résultat visuellement sympa (e.g. Bootstrap)
- ⛔️ Aucun système de compte / login (public anonyme)

---

## 💡 Extensions possibles (optionnelles)

Si vous souhaitez réaliser des extensions, utilisez les **branches** de Git pour les isoler de la version basique.

- Export PDF d'une checklist remplie
- Statistiques (taux de complétion par modèle)
- Suppression d'un modèle ou d'un historique
- Remplacement des fichiers JSON par une base de données (SQLite ou MySQL).
  - Si SQLite : la base de données doit être stockée dans le dossier `data/`
  - Si MySQL : les fichiers pour créer le modèle de données (instructions `CREATE TABLE...`) doivent être dans le dossier `data/`

---

## 🧪 Évaluation

Pour valider l'exercice, l'application doit :

- fonctionner localement sans erreur,
- permettre la création + remplissage + consultation,
- utiliser correctement les fichiers `templates.json` et `history.json`.

Bonus si :

- le code est bien organisé,
- les templates sont clairs,
- l'UX est fluide.
