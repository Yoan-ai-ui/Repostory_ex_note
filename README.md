# 🔥 Gestionnaire de Tâches Python

Un système complet de gestion des tâches écrit entièrement en Python, sans dépendances externes.

## ✨ Fonctionnalités

- ➕ **Création de tâches** avec titre, description, priorité et date d'échéance
- 📋 **Listing intelligent** avec filtres et tri automatique
- ✏️  **Modification** des tâches existantes
- ✅ **Gestion des statuts** (En attente, En cours, Terminée, Annulée)
- 🏷️  **Système de tags** pour l'organisation
- ⚠️  **Détection des retards** automatique
- 💾 **Sauvegarde automatique** en JSON
- 📊 **Statistiques détaillées**
- 🎯 **4 niveaux de priorité** (Basse, Normale, Haute, Critique)

## 🚀 Utilisation

### Lancement de l'interface interactive
```bash
python gestionnaire_taches.py
```

### Mode démonstration
```bash
python gestionnaire_taches.py --demo
```

## 📚 Structure du Code

- **Classe `Tache`**: Représente une tâche individuelle avec tous ses attributs
- **Classe `GestionnaireTaches`**: Gère la collection de tâches et les opérations CRUD
- **Énumérations**: `Priorite` et `Statut` pour une gestion typée
- **Interface CLI**: Interface utilisateur complète en ligne de commande

## 🛠️ Exemples d'utilisation programmatique

```python
from gestionnaire_taches import GestionnaireTaches, Priorite, Statut

# Créer un gestionnaire
gestionnaire = GestionnaireTaches()

# Créer une tâche
tache = gestionnaire.creer_tache(
    titre="Apprendre Python",
    description="Suivre un tutoriel complet",
    priorite=Priorite.HAUTE,
    date_echeance="2025-02-01"
)

# Lister toutes les tâches
taches = gestionnaire.lister_taches()

# Filtrer par statut
taches_en_cours = gestionnaire.lister_taches(filtre_statut=Statut.EN_COURS)

# Obtenir des statistiques
stats = gestionnaire.obtenir_statistiques()
```

## 💾 Format de Sauvegarde

Les tâches sont automatiquement sauvegardées dans `taches.json` au format JSON lisible.

## 🎯 Points Forts Techniques

- **Séparation des responsabilités** avec des classes dédiées
- **Gestion d'erreurs** robuste
- **Sérialisation/Désérialisation** JSON automatique
- **Interface CLI** intuitive avec émojis
- **Code documenté** avec docstrings Python
- **Gestion des dates** et détection des retards
- **Système de filtrage** flexible