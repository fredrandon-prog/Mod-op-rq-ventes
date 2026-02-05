# 📊 Système d'Extraction Automatique des Ventes
## Guide Utilisateur Simple

---

## 🎯 C'est quoi ?

Un système qui **chaque matin automatiquement** extrait les ventes à contrôler.

### Que contient l'extraction ?

La requête sort les **contrats dont la première activation date exactement de J-30**, encore **actifs ou terminés**, avec les spécificités suivantes :

- **Réattribution du vendeur** : Le vendeur est éventuellement réattribué via le `code_partenaire` (pour certains codes partenaires spécifiques : CP, AN, AR, DA, ES, FG, RG)
- **Rattachement au service** : Chaque vendeur est rattaché à son service tel qu'il était à la date de création du contrat
- **Exclusion des API** : Les utilisateurs techniques (contenant "api" dans leur nom) sont automatiquement exclus
- **Exclusions métier** basées sur le souscripteur :
  - Doublons de produit (même souscripteur, même produit)
  - Bascules de contrat ("nouveau contrat" issu d'un ancien)
  - Souscripteurs en situation de fraude ou d'impayés
  - Factures annuelles non payées

Ensuite le système :
1. Génère un fichier CSV avec ces données
2. L'envoie sur SharePoint
3. Garde un historique par semaine et par mois

**Résultat** : Vous avez toujours les données à jour sur SharePoint, sans rien faire !

---

## ⏰ Quand ça tourne ?

**Tous les jours à 6h00 du matin**

Le système traite automatiquement les données **du jour même**.

**Exemple** : 
- Le lundi 3 février à 6h00 → Traite les données du lundi 3 février
- Cherche les contrats qui ont été activés le 4 janvier (30 jours avant le 3 février)

---

## 📁 Fichiers créés sur SharePoint

### Emplacement
```
SharePoint > PRODUCTION > Souscription Adhsion > TEST_SUPPORT_IT
```

### 3 types de fichiers

#### 1️⃣ Fichiers Quotidiens (un par jour)
**Nom** : `ventes_AAAAMMJJ.csv`

**Exemples** :
- `ventes_20250202.csv` → Données du 2 février
- `ventes_20250203.csv` → Données du 3 février
- `ventes_20250204.csv` → Données du 4 février

**Contenu** : Les contrats extraits ce jour-là

---

#### 2️⃣ Fichiers de Semaine (mis à jour chaque jour)
**Nom** : `concat_week.csv`

**Contenu** : Cumul de tous les fichiers de la semaine en cours

**Exemple un jeudi** :
- Contient : lundi + mardi + mercredi + jeudi
- Mis à jour automatiquement chaque matin

**💡 Important** : Ce fichier est remplacé chaque lundi par un nouveau (voir archives)

---

#### 3️⃣ Fichiers de Mois (mis à jour chaque jour)
**Nom** : `concat_month.csv`

**Contenu** : Cumul de tous les fichiers du mois en cours

**Exemple le 15 février** :
- Contient : tous les jours du 1er au 15 février
- Mis à jour automatiquement chaque matin

**💡 Important** : Ce fichier est remplacé chaque 1er du mois par un nouveau (voir archives)

---

## 📦 Archives Automatiques

### Archives Hebdomadaires
**Chaque lundi matin**, le fichier `concat_week.csv` de la semaine précédente est archivé.

**Nom** : `ventes_WSS.csv` (SS = numéro de semaine)

**Exemples** :
- `ventes_W05.csv` → Semaine 5 (début février)
- `ventes_W06.csv` → Semaine 6 (mi-février)

---

### Archives Mensuelles
**Chaque 1er du mois**, le fichier `concat_month.csv` du mois précédent est archivé.

**Nom** : `ventes_AAAAMM.csv`

**Exemples** :
- `ventes_202501.csv` → Janvier 2025
- `ventes_202502.csv` → Février 2025

---

## 🔄 Reprise sur Erreur Automatique

### Le Problème
Que se passe-t-il si le système ne tourne pas pendant quelques jours ?
- Panne de serveur
- Maintenance de la base de données
- Coupure électrique

### La Solution : Rattrapage Automatique

**Le système est intelligent** : au prochain démarrage, il détecte automatiquement les jours manquants et les traite.

---

### 📖 Exemple Concret

**Situation** :
- Dernière exécution réussie : jeudi 30 janvier
- Panne du système du 31 janvier au 2 février (3 jours)
- Redémarrage : lundi 3 février à 6h00

**Ce qui se passe automatiquement** :

```
🔍 Détection des jours manquants
   ↓
📅 31 janvier manquant → Génération ventes_20250131.csv
📅 1er février manquant → Génération ventes_20250201.csv
📅 2 février manquant → Génération ventes_20250202.csv
   ↓
✅ Tous les fichiers sont créés
✅ Les fichiers concat_week.csv et concat_month.csv sont à jour
✅ Aucune donnée perdue !
```

**Résultat** : Comme si le système n'avait jamais eu de panne.

---

## 📊 Exemple de Timeline

### Semaine Normale (sans problème)

| Jour | Heure | Fichier créé | Action |
|------|-------|--------------|--------|
| Lun 3 fév | 6h00 | `ventes_20250202.csv` | Archive semaine précédente → `ventes_W05.csv` |
| Mar 4 fév | 6h00 | `ventes_20250203.csv` | Mise à jour concat_week.csv |
| Mer 5 fév | 6h00 | `ventes_20250204.csv` | Mise à jour concat_week.csv |
| Jeu 6 fév | 6h00 | `ventes_20250205.csv` | Mise à jour concat_week.csv |
| Ven 7 fév | 6h00 | `ventes_20250206.csv` | Mise à jour concat_week.csv |

---

### Semaine Avec Panne (mercredi et jeudi)

| Jour | Heure | Ce qui se passe | Fichiers créés |
|------|-------|-----------------|----------------|
| Lun 3 fév | 6h00 | ✅ Exécution normale | `ventes_20250202.csv` |
| Mar 4 fév | 6h00 | ✅ Exécution normale | `ventes_20250203.csv` |
| Mer 5 fév | - | ❌ PANNE | - |
| Jeu 6 fév | - | ❌ PANNE | - |
| Ven 7 fév | 6h00 | ⚡ **RATTRAPAGE AUTOMATIQUE** | `ventes_20250204.csv` + `ventes_20250205.csv` + `ventes_20250206.csv` |

Le vendredi, 3 fichiers sont créés d'un coup pour rattraper les jours manquants.

---

## 🔍 Comment Vérifier Que Ça Marche ?

### Sur SharePoint

1. Allez sur SharePoint : `PRODUCTION > Souscription Adhsion > TEST_SUPPORT_IT`

2. **Vérifiez chaque matin** :
   - ✅ Un nouveau fichier `ventes_AAAAMMJJ.csv` pour hier
   - ✅ Le fichier `concat_week.csv` a été modifié ce matin
   - ✅ Le fichier `concat_month.csv` a été modifié ce matin

3. **Le lundi matin** :
   - ✅ Un nouveau fichier archive `ventes_WSS.csv` est apparu

4. **Le 1er du mois** :
   - ✅ Un nouveau fichier archive `ventes_AAAAMM.csv` est apparu

---

### Dans les Logs (pour support IT)

Les logs sont dans le dossier : `C:\DEV\requete_ventes_controle\logs\`

**Fichier du jour** : `ventes_AAAAMMJJ.log`

**Ligne importante à chercher** :
```
✅ Exécution terminée avec succès
```

**En cas de reprise** :
```
⚠️ REPRISE SUR ERREUR : 3 jours manquants détectés
   Dates manquantes : 2025-02-01 à 2025-02-03
```

---

## ❓ Questions Fréquentes

### Q : Si je vois qu'un jour manque, que faire ?
**R :** Rien ! Le système va le détecter automatiquement au prochain lancement et rattraper le retard.

### Q : Comment savoir si le système a bien tourné hier ?
**R :** Regardez sur SharePoint si le fichier `ventes_AAAAMMJJ.csv` d'hier existe.

### Q : Combien de temps sont gardées les archives ?
**R :** Toutes les archives restent sur SharePoint indéfiniment. Vous pouvez les consulter quand vous voulez.

### Q : Les fichiers concat sont énormes, c'est normal ?
**R :** Oui ! 
- `concat_week.csv` contient 7 jours maximum → réinitialisé chaque lundi
- `concat_month.csv` contient ~30 jours → réinitialisé chaque 1er du mois

### Q : Que se passe-t-il le week-end ?
**R :** Le système tourne aussi le week-end à 6h00. Chaque jour est traité, même samedi et dimanche.

### Q : Les données sont-elles perdues en cas de panne longue ?
**R :** Non ! Le système peut rattraper jusqu'à plusieurs semaines de retard automatiquement.

---

## 📞 Support

**En cas de problème** :
- Contacter l'équipe Support IT
- Indiquer la date concernée
- Joindre le fichier log du jour si possible

**Fichiers logs** : `C:\DEV\requete_ventes_controle\logs\ventes_AAAAMMJJ.log`

---

## 📅 Calendrier Type d'une Semaine

```
┌─────────────────────────────────────────────────────┐
│                    LUNDI 3 FÉVRIER                  │
├─────────────────────────────────────────────────────┤
│ 6h00 - Archivage semaine précédente                │
│      → ventes_W05.csv créé                          │
│      → Nouveau concat_week.csv vide                 │
│ 6h01 - Traitement données du 2 février             │
│      → ventes_20250202.csv créé                     │
│      → concat_week.csv mis à jour (1 jour)          │
│      → concat_month.csv mis à jour                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                   MARDI 4 FÉVRIER                   │
├─────────────────────────────────────────────────────┤
│ 6h00 - Traitement données du 3 février             │
│      → ventes_20250203.csv créé                     │
│      → concat_week.csv mis à jour (2 jours)         │
│      → concat_month.csv mis à jour                  │
└─────────────────────────────────────────────────────┘

... et ainsi de suite tous les jours
```

---

**Document créé le** : 3 février 2025  
**Version** : 1.0  
**Destiné à** : Équipes métier et support
