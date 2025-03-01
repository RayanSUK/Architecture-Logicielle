
# Table des matières

- [Introduction](#introduction)
- [Prérequis](#prérequis)
- [1ère partie : utilisation de SQLAlchemy](#1ère-partie--utilisation-de-sqlalchemy)
  - [Présentation](#présentation)
  - [Prérequis](#prérequis-1)
  - [Comparaison avec exemples concrets](#comparaison-avec-exemples-concrets)
  - [Remarque](#remarque)
- [2ème partie : Application Flask](#2ème-partie--application-flask)
  - [Présentation](#présentation-1)
  - [Prérequis](#prérequis-2)
  - [Lancement de l’application](#lancement-de-lapplication)

# Introduction

Ce compte rendu porte sur l’évolution d’une application en deux étapes majeures.
Dans la première partie, nous verrons la transition de SQLite avec des requêtes SQL brutes vers SQLAlchemy Core. L’objectif est d’améliorer la gestion des données en rendant le code plus structuré, lisible et maintenable.
Dans la seconde partie, nous intégrerons Flask pour transformer notre projet en une application web. Nous verrons comment utiliser Flask pour créer une interface permettant d’interagir avec la base de données et gérer les fonctionnalités de l’application de manière dynamique.
Pour à bien le projet, nous utiliserons 3 fichier qui sont :
- `models.py` → Gestion des données (base de données et SQLAlchemy Core).
- `services.py` → Application web Flask + CLI pour la base de données.
- `views.py` → Interface CLI + application web Flask

# Prérequis

Avant de commencer, certains outils et bibliothèques sont nécessaires pour exécuter le projet initial. Les commandes à exécuter dans le terminal sont :

```bash
pip install pdm
```

Cette commande installe PDM (Python Dependency Manager) qui est un outil permettant de gérer les dépendances et l’environnement du projet.

```bash
python -m pdm
```

Cela permet de vérifier que PDM est bien installé et fonctionnel sur votre machine.

```bash
python -m pdm install
```

Après avoir extrait le dossier du projet et naviguer dedans jusqu'au niveau src, cette commande installe toutes les dépendances définies pour le projet notamment Click et d’autres bibliothèques nécessaires.

```bash
python -m pdm run archilog
```

Cette commande exécute le projet Archilog dans l’environnement PDM et affiche les fonctions disponibles (opération crud).

Il est possible de rencontrer des erreurs durant l’installation. Voici celles que nous avons rencontrées :
- absence d’interpréteur Python nécessitant une sélection manuelle
- le fichier `pyproject.toml` mal configuré (la distribution)
- problème avec le terminal (favoriser le terminal git Bash)

# 1ère partie : utilisation de SQLAlchemy

## Présentation

SQLAlchemy est une bibliothèque Python permettant d’interagir avec une base de données de manière plus structurée et flexible. Contrairement à l’utilisation de requêtes SQL brutes avec SQLite, SQLAlchemy offre une interface plus abstraite qui facilite la gestion des tables et des requêtes.

## Prérequis

Avant de commencer, il faut installer SQLAlchemy avec la commande :

```bash
python -m pdm add sqlalchemy
```

Cette commande permet d’installer SQLAlchemy, qui sera utilisé pour gérer la base de données de manière plus structurée et flexible.

## Comparaison avec exemples concrets

Dans notre projet, nous avons remplacé les requêtes SQL brutes par SQLAlchemy Core, ce qui nous permet de structurer les données de manière plus propre et efficace. Voici deux exemples :

### Création de la table

Avec SQLite, nous utilisions `sqlite3.connect()` et des requêtes SQL brutes pour créer la table :

```python
con = sqlite3.connect('BaseDeDonne')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS produit (id, name, categorie, prix)")
```

Avec SQLAlchemy, nous utilisons `create_engine()` et `Table()` pour définir les colonnes et leurs propriétés de manière plus lisible :

```python
engine = create_engine("sqlite:///data.db", echo=True)
metadata = MetaData()
tableTest = Table(
   "users",
   metadata,
   Column("id", Uuid, primary_key=True, default=uuid.uuid4),
   Column("name", String, nullable=False),
   Column("amount", Float, nullable=False),
   Column("category", String, nullable=False)
)
```

### Mise à jour d’une entrée

Avant avec SQLite, nous utilisions `cur.execute("UPDATE produit SET ...")` pour modifier les données :

```python
def update(id: str, name: str, categorie: str, montant: str):
    cur.execute("SELECT * FROM produit WHERE id = ?", (id,))
    produit = cur.fetchone()

    if produit:
        cur.execute("UPDATE produit SET name = ?, categorie = ?, prix = ? WHERE id = ?",
                    (name, categorie, montant, id))
        con.commit()

        if cur.rowcount > 0:
            click.echo(f"Produit avec ID '{id}' mis à jour avec succès !")
        else:
            click.echo(f"Aucun produit avec l'ID '{id}' trouvé.")
    else:
        click.echo(f"Aucun produit avec l'ID '{id}' trouvé.")
```

Avec SQLAlchemy, nous utilisons `tableTest.update().where(tableTest.c.id == id)`, ce qui rend la requête plus sécurisée et adaptable :

```python
def update_entry(id: uuid.UUID, name: str, amount: float, category: str | None) -> None:
   stmt = tableTest.update().where(tableTest.c.id == id)
   with engine.begin() as con:
       con.execute(stmt)
```

## Remarque

Pour bien afficher nos tables dans notre terminal, nous utiliserons la bibliothèque `tabulate`.
Dans le terminal, il faut exécuter la commande suivante :

```bash
python -m pdm add tabulate
```

Il faudra ensuite l’importer dans notre fichier `views.py` (celui qui se charge des lignes de commande) et l’implémenter dans les fonctions `get_all` et `get`, qui se chargent d’afficher les tables.
De plus, un texte au début est généré par SQLAlchemy en mode logging, ce qui ne nous intéresse pas. Pour le désactiver, il faudra modifier cette commande dans `models.py` en désactivant l’écho :

```python
engine = create_engine("sqlite:///data.db", echo=True)
```

# 2ème partie : Application Flask

## Présentation

Flask est un framework web léger en Python, conçu pour créer rapidement des applications web. Il permet de gérer des routes, d'afficher des pages HTML et de traiter des requêtes facilement. Grâce à Flask, nous pouvons structurer notre application tout en gardant une grande flexibilité.

Dans ce projet, l'objectif est de transposer les fonctionnalités que nous avons créées dans le terminal (comme les opérations CRUD - créer, lire, mettre à jour, supprimer) dans une interface web. Grâce à Flask et à son moteur de templates Jinja, nous pouvons afficher les résultats de manière dynamique sur les pages HTML de notre application.

## Prérequis

Avant de démarrer, il faut installer Flask avec les commandes :

```bash
pip install flask
python -m pdm add flask
```

Ensuite, il faudra créer un dossier `templates` qui contiendra les fichiers HTML de l’application. Ce dossier est essentiel car Flask recherche automatiquement les fichiers HTML à l’intérieur pour afficher les pages web.
Dans `templates/`, nous ajouterons les fichiers `index`, `add` et `delete.html`.
Nous devons également ajouter du code dans `views.py` pour gérer les routes et afficher les pages.

## Lancement de l’application

Une fois Flask installé, l’application peut être démarrée avec la commande :

```bash
pdm run flask --app archilog.views --debug run
```

Ensuite, on peut y accéder via [http://localhost:5000](http://localhost:5000).
