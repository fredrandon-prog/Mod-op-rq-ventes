# Mes Courses — appli Android de liste de courses

Appli Android native (Kotlin) pour préparer ses courses et faire le lien avec l'application Carrefour.

## Fonctionnalités

- **Liste de courses** stockée localement (SQLite) : ajout, coche, suppression, purge des articles cochés
- **Scanner de code-barres** (CameraX + ML Kit) : scanne un produit et récupère son nom via [Open Food Facts](https://world.openfoodfacts.org/)
- **Bouton Carrefour** : ouvre la recherche Carrefour (`carrefour.fr/recherche?q=...`) pour un article, ou pour toute la liste non cochée. Si l'app Carrefour est installée, Android l'ouvre ; sinon le navigateur s'ouvre sur le site.

## Limites connues

- Pas d'ajout automatique au panier Carrefour : Carrefour n'expose pas d'API publique en France (portail développeur réservé aux partenaires/prestataires). L'app ouvre donc Carrefour **sur le bon produit**, l'ajout au panier reste manuel (quelques secondes par article).

## Build

Prérequis : JDK 17, Android SDK (platform 34, build-tools 34).

```bash
./gradlew assembleDebug
# APK : app/build/outputs/apk/debug/app-debug.apk
```

## Installation

Télécharger l'APK depuis les [releases](../../releases), puis l'installer sur le téléphone (autoriser « sources inconnues » / « installer des apps inconnues » dans les paramètres Android).

## Structure

- `app/src/main/java/fr/mescourses/app/MainActivity.kt` — écran principal, liste, appel Open Food Facts, ouverture Carrefour
- `app/src/main/java/fr/mescourses/app/ScannerActivity.kt` — scanner code-barres (CameraX + ML Kit)
- `app/src/main/java/fr/mescourses/app/GroceryDbHelper.kt` — stockage SQLite
