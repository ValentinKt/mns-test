# Migrations de Base de Données pour l'Application Flask

Ce répertoire contient les scripts de migration Alembic pour gérer les modifications du schéma de base de données dans l'application Flask.

## Objectif

Alembic est un outil de migration de base de données léger pour SQLAlchemy. Il vous permet de faire évoluer votre schéma de base de données au fil du temps de manière structurée et organisée. Ces scripts de migration définissent les modifications nécessaires pour mettre à jour le schéma de base de données à une version spécifique.

## Utilisation

Pour appliquer les migrations de base de données, vous devez avoir correctement configuré Alembic dans votre application Flask. Voici un flux de travail de base :

1. **Initialiser Alembic :**
    Si ce n'est pas déjà fait, initialisez Alembic dans votre projet :

    ```bash
    flask db init
    ```

2. **Créer une Migration :**
    Lorsque vous apportez des modifications à vos modèles de base de données, créez un nouveau script de migration :

    ```bash
    flask db migrate -m "Ajoutez un message descriptif sur les modifications"
    ```

    Cela générera un nouveau script de migration dans le répertoire `migrations/versions`.

3. **Appliquer les Migrations :**
    Pour appliquer les migrations et mettre à jour votre schéma de base de données, exécutez :

    ```bash
    flask db upgrade
    ```

    Cela appliquera toutes les migrations en attente dans l'ordre.

4. **Rétrograder les Migrations :**
    Si vous devez revenir à une version précédente du schéma, vous pouvez rétrograder les migrations :

    ```bash
    flask db downgrade <revision>
    ```

    Remplacez `<revision>` par l'ID de révision spécifique auquel vous souhaitez revenir.

## Configuration

La configuration d'Alembic est stockée dans le fichier `alembic.ini` de ce répertoire. Vous pouvez personnaliser la chaîne de connexion à la base de données et d'autres paramètres dans ce fichier.

## Dépendances

Assurez-vous d'avoir installé les dépendances nécessaires, notamment :

* Flask-Migrate
* Alembic
* SQLAlchemy

Vous pouvez les installer avec pip :

```bash
pip install Flask-Migrate Alembic SQLAlchemy
```
