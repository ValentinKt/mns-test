# Les Design Patterns en Python

Les *design patterns* (ou patrons de conception) sont des solutions éprouvées à des problèmes courants rencontrés lors du développement logiciel. Ils permettent d'améliorer la maintenabilité, la réutilisabilité et la clarté du code.

En Python, l'utilisation des design patterns est facilitée par la flexibilité du langage et ses fonctionnalités orientées objet. Parmi les patterns les plus utilisés, on retrouve le Singleton, le Factory, le Observer ou encore le Decorator.

Adopter les design patterns en Python permet de structurer le code de manière cohérente, de faciliter la collaboration entre développeurs et de résoudre efficacement des problématiques récurrentes dans la conception logicielle.

## Le Singleton
Le *Singleton* est un design pattern qui garantit qu'une classe ne possède qu'une seule instance et fournit un point d'accès global à cette instance. Ce pattern est utile lorsqu'il est nécessaire de contrôler l'accès à une ressource partagée, comme une connexion à une base de données ou un gestionnaire de configuration.

En Python, le Singleton peut être implémenté de différentes manières, par exemple en utilisant une variable de classe, un décorateur ou une métaclasse. Le principe reste le même : lors de la création d'un nouvel objet, on vérifie si une instance existe déjà. Si c'est le cas, on retourne cette instance ; sinon, on en crée une nouvelle.

L'utilisation du Singleton permet d'éviter la duplication d'objets coûteux en ressources et de centraliser la gestion de certaines fonctionnalités. Cependant, il doit être utilisé avec précaution, car il peut introduire des dépendances globales et rendre les tests unitaires plus complexes.

## La Factory
Le *Factory* est un design pattern de création qui permet de déléguer l'instanciation d'objets à une méthode ou une classe dédiée, appelée « fabrique ». Ce pattern est particulièrement utile lorsque le code doit créer des objets dont le type concret n'est pas connu à l'avance ou peut varier selon le contexte.

En Python, le pattern Factory peut être implémenté à l'aide de fonctions ou de classes qui retournent des instances d'autres classes selon certains paramètres. Cela permet de centraliser la logique de création d'objets et de faciliter l'ajout de nouveaux types sans modifier le code client.

L'utilisation du Factory favorise l'extensibilité et la flexibilité du code, en masquant les détails d'implémentation des objets créés. Il est souvent utilisé dans les frameworks, les bibliothèques ou les applications nécessitant une gestion dynamique des types d'objets.

Exemple simple d'implémentation d'une factory en Python :

```python
class Animal:
    def parler(self):
        pass

class Chien(Animal):
    def parler(self):
        return "Wouf!"

class Chat(Animal):
    def parler(self):
        return "Miaou!"

def animal_factory(type_animal):
    if type_animal == "chien":
        return Chien()
    elif type_animal == "chat":
        return Chat()
    else:
        raise ValueError("Type d'animal inconnu")

animal = animal_factory("chien")
print(animal.parler())  # Affiche "Wouf!"
```
## L'Observer
Le *Observer* est un design pattern comportemental qui permet à un objet (appelé « sujet ») de notifier automatiquement un ou plusieurs autres objets (appelés « observateurs ») lorsqu'un changement d'état survient. Ce pattern est particulièrement utile pour implémenter des systèmes de publication/abonnement, des interfaces graphiques ou des architectures réactives.

En Python, le pattern Observer peut être implémenté en utilisant des listes d'observateurs et des méthodes de notification. Lorsqu'un événement se produit dans le sujet, celui-ci parcourt la liste de ses observateurs et appelle une méthode spécifique sur chacun d'eux pour les informer du changement.

L'utilisation du pattern Observer favorise le découplage entre les composants d'une application, car le sujet n'a pas besoin de connaître les détails des observateurs. Cela facilite l'ajout ou la suppression d'observateurs dynamiquement, sans modifier le code du sujet.

Exemple simple d'implémentation de l'Observer en Python :

```python
class Sujet:
    def __init__(self):
        self._observateurs = []

    def ajouter_observateur(self, observateur):
        self._observateurs.append(observateur)

    def notifier(self, message):
        for observateur in self._observateurs:
            observateur.actualiser(message)

class Observateur:
    def actualiser(self, message):
        print(f"Observateur notifié : {message}")

# Utilisation
sujet = Sujet()
obs1 = Observateur()
obs2 = Observateur()

sujet.ajouter_observateur(obs1)
sujet.ajouter_observateur(obs2)

sujet.notifier("Changement d'état détecté")
```
## Le Decorator
Le *Decorator* est un design pattern structurel qui permet d'ajouter dynamiquement des fonctionnalités à un objet sans modifier sa structure d'origine. Ce pattern favorise la composition d'objets plutôt que l'héritage, ce qui rend le code plus flexible et extensible.

En Python, le pattern Decorator peut être implémenté à l'aide de classes ou de fonctions, notamment grâce à la syntaxe des décorateurs (`@decorator`). Il consiste à envelopper un objet dans un autre objet qui ajoute ou modifie son comportement, tout en conservant la même interface.

L'utilisation du Decorator permet d'empiler plusieurs comportements additionnels de manière transparente, sans modifier le code de la classe de base. Ce pattern est particulièrement utile pour ajouter des fonctionnalités transversales comme la journalisation, la validation ou la gestion des accès.

## Exemple d'extension avec le Decorator : Tasse et Tasse avec Sucre

Prenons l'exemple d'une tasse de café à laquelle on peut ajouter dynamiquement des ingrédients, comme du sucre, tout en modifiant le prix. Le pattern Decorator permet d'ajouter ces fonctionnalités sans modifier la classe de base.

```python
class Tasse:
    def description(self):
        return "Tasse de café"

    def prix(self):
        return 2.0

class DecorateurTasse(Tasse):
    def __init__(self, tasse):
        self._tasse = tasse

    def description(self):
        return self._tasse.description()

    def prix(self):
        return self._tasse.prix()

class Sucre(DecorateurTasse):
    def description(self):
        return self._tasse.description() + " avec sucre"

    def prix(self):
        return self._tasse.prix() + 0.2

# Utilisation
tasse_simple = Tasse()
print(tasse_simple.description())  # Tasse de café
print(tasse_simple.prix())         # 2.0

tasse_sucree = Sucre(tasse_simple)
print(tasse_sucree.description())  # Tasse de café avec sucre
print(tasse_sucree.prix())         # 2.2
```

Cet exemple montre comment ajouter dynamiquement des fonctionnalités (ici, du sucre) à une tasse, tout en modifiant son prix, sans changer la classe d'origine.
