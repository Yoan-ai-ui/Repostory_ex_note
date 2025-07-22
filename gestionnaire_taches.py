#!/usr/bin/env python3
"""
Gestionnaire de Tâches - Un système complet de gestion des tâches
Auteur: Assistant IA
Date: 2025

Ce fichier contient une implémentation complète d'un gestionnaire de tâches
avec les fonctionnalités suivantes:
- Création, modification et suppression de tâches
- Gestion des priorités et statuts
- Sauvegarde et chargement depuis un fichier JSON
- Interface en ligne de commande
"""

import json
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional
import argparse


class Priorite(Enum):
    """Énumération des niveaux de priorité des tâches"""
    BASSE = 1
    NORMALE = 2
    HAUTE = 3
    CRITIQUE = 4


class Statut(Enum):
    """Énumération des statuts possibles d'une tâche"""
    EN_ATTENTE = "En attente"
    EN_COURS = "En cours"
    TERMINEE = "Terminée"
    ANNULEE = "Annulée"


class Tache:
    """
    Classe représentant une tâche individuelle
    
    Attributes:
        id: Identifiant unique de la tâche
        titre: Titre de la tâche
        description: Description détaillée
        priorite: Niveau de priorité
        statut: Statut actuel
        date_creation: Date de création
        date_echeance: Date d'échéance (optionnelle)
        tags: Liste des tags associés
    """
    
    def __init__(self, id_tache: int, titre: str, description: str = "", 
                 priorite: Priorite = Priorite.NORMALE, date_echeance: Optional[str] = None):
        self.id = id_tache
        self.titre = titre
        self.description = description
        self.priorite = priorite
        self.statut = Statut.EN_ATTENTE
        self.date_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date_echeance = date_echeance
        self.tags = []
    
    def marquer_terminee(self):
        """Marque la tâche comme terminée"""
        self.statut = Statut.TERMINEE
    
    def marquer_en_cours(self):
        """Marque la tâche comme en cours"""
        self.statut = Statut.EN_COURS
    
    def ajouter_tag(self, tag: str):
        """Ajoute un tag à la tâche"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def supprimer_tag(self, tag: str):
        """Supprime un tag de la tâche"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def est_en_retard(self) -> bool:
        """Vérifie si la tâche est en retard"""
        if not self.date_echeance:
            return False
        
        try:
            echeance = datetime.strptime(self.date_echeance, "%Y-%m-%d")
            return datetime.now() > echeance and self.statut != Statut.TERMINEE
        except ValueError:
            return False
    
    def to_dict(self) -> Dict:
        """Convertit la tâche en dictionnaire pour la sérialisation"""
        return {
            'id': self.id,
            'titre': self.titre,
            'description': self.description,
            'priorite': self.priorite.value,
            'statut': self.statut.value,
            'date_creation': self.date_creation,
            'date_echeance': self.date_echeance,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Tache':
        """Crée une tâche à partir d'un dictionnaire"""
        tache = cls(
            id_tache=data['id'],
            titre=data['titre'],
            description=data.get('description', ''),
            priorite=Priorite(data.get('priorite', 2)),
            date_echeance=data.get('date_echeance')
        )
        tache.statut = Statut(data.get('statut', Statut.EN_ATTENTE.value))
        tache.date_creation = data.get('date_creation', tache.date_creation)
        tache.tags = data.get('tags', [])
        return tache
    
    def __str__(self) -> str:
        """Représentation string de la tâche"""
        priorite_str = f"[P{self.priorite.value}]"
        statut_str = f"[{self.statut.value}]"
        retard_str = " ⚠️ EN RETARD" if self.est_en_retard() else ""
        
        return f"{priorite_str} {statut_str} #{self.id}: {self.titre}{retard_str}"


class GestionnaireTaches:
    """
    Gestionnaire principal des tâches
    
    Gère la collection de tâches et les opérations CRUD
    """
    
    def __init__(self, fichier_sauvegarde: str = "taches.json"):
        self.taches: List[Tache] = []
        self.fichier_sauvegarde = fichier_sauvegarde
        self._prochain_id = 1
        self.charger_taches()
    
    def creer_tache(self, titre: str, description: str = "", 
                    priorite: Priorite = Priorite.NORMALE, 
                    date_echeance: Optional[str] = None) -> Tache:
        """Crée une nouvelle tâche"""
        if not titre.strip():
            raise ValueError("Le titre de la tâche ne peut pas être vide")
        
        tache = Tache(self._prochain_id, titre.strip(), description, priorite, date_echeance)
        self.taches.append(tache)
        self._prochain_id += 1
        self.sauvegarder_taches()
        return tache
    
    def obtenir_tache(self, id_tache: int) -> Optional[Tache]:
        """Récupère une tâche par son ID"""
        return next((t for t in self.taches if t.id == id_tache), None)
    
    def modifier_tache(self, id_tache: int, **kwargs) -> bool:
        """Modifie une tâche existante"""
        tache = self.obtenir_tache(id_tache)
        if not tache:
            return False
        
        for attribut, valeur in kwargs.items():
            if hasattr(tache, attribut) and valeur is not None:
                setattr(tache, attribut, valeur)
        
        self.sauvegarder_taches()
        return True
    
    def supprimer_tache(self, id_tache: int) -> bool:
        """Supprime une tâche"""
        tache = self.obtenir_tache(id_tache)
        if tache:
            self.taches.remove(tache)
            self.sauvegarder_taches()
            return True
        return False
    
    def lister_taches(self, filtre_statut: Optional[Statut] = None, 
                     filtre_priorite: Optional[Priorite] = None,
                     filtre_tag: Optional[str] = None) -> List[Tache]:
        """Liste les tâches avec des filtres optionnels"""
        taches_filtrees = self.taches.copy()
        
        if filtre_statut:
            taches_filtrees = [t for t in taches_filtrees if t.statut == filtre_statut]
        
        if filtre_priorite:
            taches_filtrees = [t for t in taches_filtrees if t.priorite == filtre_priorite]
        
        if filtre_tag:
            taches_filtrees = [t for t in taches_filtrees if filtre_tag in t.tags]
        
        # Tri par priorité (décroissante) puis par date de création
        return sorted(taches_filtrees, 
                     key=lambda t: (-t.priorite.value, t.date_creation))
    
    def obtenir_statistiques(self) -> Dict:
        """Retourne des statistiques sur les tâches"""
        total = len(self.taches)
        if total == 0:
            return {"total": 0}
        
        par_statut = {}
        par_priorite = {}
        en_retard = 0
        
        for tache in self.taches:
            # Statistiques par statut
            statut = tache.statut.value
            par_statut[statut] = par_statut.get(statut, 0) + 1
            
            # Statistiques par priorité
            priorite = f"P{tache.priorite.value}"
            par_priorite[priorite] = par_priorite.get(priorite, 0) + 1
            
            # Tâches en retard
            if tache.est_en_retard():
                en_retard += 1
        
        return {
            "total": total,
            "par_statut": par_statut,
            "par_priorite": par_priorite,
            "en_retard": en_retard
        }
    
    def sauvegarder_taches(self):
        """Sauvegarde les tâches dans un fichier JSON"""
        try:
            data = {
                "taches": [tache.to_dict() for tache in self.taches],
                "prochain_id": self._prochain_id
            }
            
            with open(self.fichier_sauvegarde, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
    
    def charger_taches(self):
        """Charge les tâches depuis un fichier JSON"""
        if not os.path.exists(self.fichier_sauvegarde):
            return
        
        try:
            with open(self.fichier_sauvegarde, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.taches = [Tache.from_dict(t) for t in data.get("taches", [])]
            self._prochain_id = data.get("prochain_id", 1)
            
            # Mise à jour de l'ID si nécessaire
            if self.taches:
                max_id = max(t.id for t in self.taches)
                self._prochain_id = max(self._prochain_id, max_id + 1)
        
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            self.taches = []
            self._prochain_id = 1


def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "="*50)
    print("🔥 GESTIONNAIRE DE TÂCHES")
    print("="*50)
    print("1. Créer une tâche")
    print("2. Lister les tâches")
    print("3. Modifier une tâche")
    print("4. Marquer comme terminée")
    print("5. Supprimer une tâche")
    print("6. Afficher les statistiques")
    print("0. Quitter")
    print("-"*50)


def saisir_priorite() -> Priorite:
    """Interface pour saisir la priorité"""
    print("\nNiveaux de priorité:")
    print("1. Basse")
    print("2. Normale")
    print("3. Haute")
    print("4. Critique")
    
    while True:
        try:
            choix = int(input("Priorité (1-4): "))
            return Priorite(choix)
        except (ValueError, KeyError):
            print("Veuillez entrer un nombre entre 1 et 4")


def interface_ligne_commande():
    """Interface en ligne de commande interactive"""
    gestionnaire = GestionnaireTaches()
    
    print("👋 Bienvenue dans le Gestionnaire de Tâches!")
    
    while True:
        afficher_menu()
        
        try:
            choix = input("Votre choix: ").strip()
            
            if choix == "0":
                print("Au revoir! 👋")
                break
            
            elif choix == "1":
                # Créer une tâche
                print("\n➕ CRÉER UNE NOUVELLE TÂCHE")
                titre = input("Titre: ").strip()
                if not titre:
                    print("❌ Le titre ne peut pas être vide")
                    continue
                
                description = input("Description (optionnel): ").strip()
                priorite = saisir_priorite()
                date_echeance = input("Date d'échéance (YYYY-MM-DD, optionnel): ").strip()
                
                if not date_echeance:
                    date_echeance = None
                
                try:
                    tache = gestionnaire.creer_tache(titre, description, priorite, date_echeance)
                    print(f"✅ Tâche créée: {tache}")
                except ValueError as e:
                    print(f"❌ Erreur: {e}")
            
            elif choix == "2":
                # Lister les tâches
                print("\n📋 LISTE DES TÂCHES")
                taches = gestionnaire.lister_taches()
                
                if not taches:
                    print("Aucune tâche trouvée")
                else:
                    for tache in taches:
                        print(f"  {tache}")
                        if tache.description:
                            print(f"    📝 {tache.description}")
                        if tache.tags:
                            print(f"    🏷️  {', '.join(tache.tags)}")
            
            elif choix == "3":
                # Modifier une tâche
                print("\n✏️  MODIFIER UNE TÂCHE")
                try:
                    id_tache = int(input("ID de la tâche à modifier: "))
                    tache = gestionnaire.obtenir_tache(id_tache)
                    
                    if not tache:
                        print("❌ Tâche introuvable")
                        continue
                    
                    print(f"Tâche actuelle: {tache}")
                    nouveau_titre = input(f"Nouveau titre (actuel: {tache.titre}): ").strip()
                    
                    if nouveau_titre:
                        gestionnaire.modifier_tache(id_tache, titre=nouveau_titre)
                        print("✅ Tâche modifiée avec succès")
                    
                except ValueError:
                    print("❌ ID invalide")
            
            elif choix == "4":
                # Marquer comme terminée
                print("\n✅ MARQUER COMME TERMINÉE")
                try:
                    id_tache = int(input("ID de la tâche: "))
                    tache = gestionnaire.obtenir_tache(id_tache)
                    
                    if tache:
                        tache.marquer_terminee()
                        gestionnaire.sauvegarder_taches()
                        print(f"✅ Tâche #{id_tache} marquée comme terminée")
                    else:
                        print("❌ Tâche introuvable")
                
                except ValueError:
                    print("❌ ID invalide")
            
            elif choix == "5":
                # Supprimer une tâche
                print("\n🗑️  SUPPRIMER UNE TÂCHE")
                try:
                    id_tache = int(input("ID de la tâche à supprimer: "))
                    
                    if gestionnaire.supprimer_tache(id_tache):
                        print(f"✅ Tâche #{id_tache} supprimée")
                    else:
                        print("❌ Tâche introuvable")
                
                except ValueError:
                    print("❌ ID invalide")
            
            elif choix == "6":
                # Afficher les statistiques
                print("\n📊 STATISTIQUES")
                stats = gestionnaire.obtenir_statistiques()
                
                if stats["total"] == 0:
                    print("Aucune tâche enregistrée")
                else:
                    print(f"Total des tâches: {stats['total']}")
                    
                    print("\nPar statut:")
                    for statut, count in stats['par_statut'].items():
                        print(f"  {statut}: {count}")
                    
                    print("\nPar priorité:")
                    for priorite, count in stats['par_priorite'].items():
                        print(f"  {priorite}: {count}")
                    
                    if stats['en_retard'] > 0:
                        print(f"\n⚠️  Tâches en retard: {stats['en_retard']}")
            
            else:
                print("❌ Choix invalide")
        
        except KeyboardInterrupt:
            print("\n\nAu revoir! 👋")
            break
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")


def main():
    """Fonction principale avec gestion des arguments en ligne de commande"""
    parser = argparse.ArgumentParser(description="Gestionnaire de Tâches")
    parser.add_argument("--demo", action="store_true", 
                       help="Lance une démonstration avec des tâches d'exemple")
    
    args = parser.parse_args()
    
    if args.demo:
        # Mode démonstration
        print("🚀 Mode démonstration activé!")
        gestionnaire = GestionnaireTaches("demo_taches.json")
        
        # Création de tâches d'exemple
        taches_demo = [
            ("Apprendre Python", "Suivre un tutoriel complet", Priorite.HAUTE, "2025-02-01"),
            ("Faire les courses", "Acheter du pain, lait, oeufs", Priorite.NORMALE, None),
            ("Réunion équipe", "Point hebdomadaire à 14h", Priorite.CRITIQUE, "2025-01-15"),
            ("Lire un livre", "Terminer le livre de science-fiction", Priorite.BASSE, "2025-01-30")
        ]
        
        for titre, desc, priorite, echeance in taches_demo:
            gestionnaire.creer_tache(titre, desc, priorite, echeance)
        
        # Marquer une tâche comme en cours
        gestionnaire.obtenir_tache(1).marquer_en_cours()
        gestionnaire.sauvegarder_taches()
        
        print("✅ Tâches de démonstration créées!")
        
        # Afficher les tâches créées
        print("\n📋 Tâches créées:")
        for tache in gestionnaire.lister_taches():
            print(f"  {tache}")
        
        print("\n📊 Statistiques:")
        stats = gestionnaire.obtenir_statistiques()
        print(f"  Total: {stats['total']} tâches")
        
    else:
        # Mode interface normale
        interface_ligne_commande()


if __name__ == "__main__":
    main()