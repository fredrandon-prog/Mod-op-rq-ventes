# 📱 PhotoRetouch AI - Version Mobile pour Android

**Application de retouche photo locale avec IA pour votre Samsung S23 (et autres appareils Android)**

![Android](https://img.shields.io/badge/Android-34-green) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Kivy](https://img.shields.io/badge/Kivy-2.2.1-orange) ![License](https://img.shields.io/badge/License-MIT-red)

---

## ✨ **Fonctionnalités**

Toutes les fonctionnalités de la version desktop, adaptées pour mobile :

### 🎯 **Retouches de Base**
- ✅ Amélioration automatique (couleurs, contraste, netteté)
- ✅ Amélioration des couleurs
- ✅ Amélioration du contraste
- ✅ Amélioration de la netteté
- ✅ Débruitage

### 🎨 **Traitements Avancés**
- ✅ **Suppression d'arrière-plan** (MediaPipe)
- ✅ **Super-résolution x2** (ESRGAN)
- ✅ **Restauration de vieilles photos**
- ✅ **Correction des yeux rouges**

### 🗑️ **Gommage d'Objets** ⭐
- ✅ Gommage par rectangle
- ✅ Gommage intelligent (détection automatique)
- ✅ 4 méthodes de remplacement : inpainting, flou, couleur, contexte

### 🖌️ **Clone Stamp** ⭐
- ✅ Clone Stamp simple
- ✅ Clone Rectangle
- ✅ Clone avec rotation
- ✅ Pattern Clone
- ✅ Healing Brush

### 🔒 **Sans Censure**
- ✅ **100% Local** - Aucune donnée n'est envoyée sur internet
- ✅ **Sans restriction** - Traite toutes les images sans filtrage
- ✅ **Confidentialité totale** - Vos photos restent sur votre appareil

---

## 📋 **Table des Matières**

1. [Prérequis](#-prérequis)
2. [Installation](#-installation)
3. [Méthode 1: Build avec BeeWare Briefcase (Recommandé)](#-méthode-1-build-avec-beeware-briefcase-recommandé)
4. [Méthode 2: Build avec Buildozer](#-méthode-2-build-avec-buildozer)
5. [Méthode 3: Utilisation avec Termux (Plus Simple)](#-méthode-3-utilisation-avec-termux-plus-simple)
6. [Utilisation de l'APK](#-utilisation-de-lapk)
7. [Dépannage](#-dépannage)
8. [Performances](#-performances)

---

## 📋 **Prérequis**

### Pour le Build (sur PC)
- **Système d'exploitation** : Windows 10/11, macOS, ou Linux
- **Python** : 3.8 ou supérieur
- **Java JDK** : 11 ou supérieur (recommandé: 17)
- **Android SDK** : API 24+ (pour Android 7.0+)
- **Android NDK** : Version 25b recommandée
- **Espace disque** : 10 Go minimum
- **RAM** : 8 Go minimum (16 Go recommandé)

### Pour l'Utilisation (sur Samsung S23)
- **Android** : 14 (API 34) - Votre S23 est compatible !
- **Espace de stockage** : 500 Mo minimum pour l'application
- **Permissions** : Accès au stockage et à la caméra

---

## 🚀 **Installation**

### 1. Installer les dépendances de build

```bash
# Cloner le dépôt
cd photo-retouch-ai-mobile

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Installer Android Studio et les outils

1. **Télécharger Android Studio** : [https://developer.android.com/studio](https://developer.android.com/studio)
2. **Installer Android Studio** et lancer le SDK Manager
3. **Installer les packages suivants** :
   - Android SDK Platform 34 (Android 14)
   - Android SDK Platform-Tools
   - Android SDK Build-Tools 34
   - Android NDK (Side by side) 25b
   - CMake 3.22.1
   - Android Emulator (optionnel)

4. **Configurer les variables d'environnement** :

   **Windows** (ajouter au PATH) :
   ```
   ANDROID_HOME=C:\Users\<votre_utilisateur>\AppData\Local\Android\Sdk
   ANDROID_NDK_HOME=C:\Users\<votre_utilisateur>\AppData\Local\Android\Sdk\ndk\25.2.9519653
   ```

   **Linux/macOS** (ajouter à ~/.bashrc ou ~/.zshrc) :
   ```bash
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_NDK_HOME=$ANDROID_HOME/ndk/25.2.9519653
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
```

---

## 🏗️ **Méthode 1: Build avec BeeWare Briefcase (Recommandé)**

BeeWare Briefcase est la méthode la plus moderne et la plus simple pour créer une APK.

### Étapes :

```bash
# Installer Briefcase
pip install briefcase

# Aller dans le dossier du projet
cd photo-retouch-ai-mobile

# Créer le projet Android
briefcase create android

# Builder l'APK (cela peut prendre 10-30 minutes)
briefcase build android

# L'APK sera générée dans le dossier build/android/app
```

### Commandes utiles :

```bash
# Mettre à jour le projet
briefcase update android

# Exécuter l'application sur un appareil connecté
briefcase run android

# Nettoyer le build
briefcase clean android
```

---

## 🏗️ **Méthode 2: Build avec Buildozer**

Buildozer est une alternative populaire pour créer des APK.

### Étapes :

```bash
# Installer Buildozer
pip install buildozer

# Aller dans le dossier du projet
cd photo-retouch-ai-mobile

# Initialiser Buildozer (si buildozer.spec n'existe pas)
buildozer init

# Builder l'APK (cela peut prendre 30-60 minutes)
buildozer -v android debug

# L'APK sera générée dans le dossier bin
```

### Personnalisation :

Éditez le fichier `buildozer.spec` pour :
- Changer le nom de l'application
- Modifier l'icône
- Ajouter des permissions
- Configurer l'orientation

---

## 📱 **Méthode 3: Utilisation avec Termux (Plus Simple !)**

Si vous ne voulez pas compiler une APK, vous pouvez exécuter l'application directement sur votre Samsung S23 avec **Termux**.

### Étapes :

1. **Installer Termux** depuis F-Droid (pas disponible sur Google Play) :
   - Téléchargez depuis : [https://f-droid.org/en/packages/com.termux/](https://f-droid.org/en/packages/com.termux/)

2. **Mettre à jour Termux** :
   ```bash
   pkg update && pkg upgrade
   ```

3. **Installer les dépendances** :
   ```bash
   pkg install python git clang libjpeg-turbo
   pip install --upgrade pip
   ```

4. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/fredrandon-prog/Mod-op-rq-ventes.git
   cd Mod-op-rq-ventes/photo-retouch-ai
   ```

5. **Installer les dépendances Python** :
   ```bash
   pip install -r requirements.txt
   ```

6. **Exécuter l'application** :
   ```bash
   python -m app.main
   ```

7. **Accéder à l'application** :
   - Termux ouvrira un serveur local
   - Utilisez un navigateur sur votre téléphone pour accéder à `http://localhost:8501`

### Avantages :
- ✅ Pas besoin de compiler
- ✅ Mises à jour faciles
- ✅ Accès à toutes les fonctionnalités

### Inconvénients :
- ❌ Nécessite Termux
- ❌ Interface web (pas native)
- ❌ Moins performant

---

## 📲 **Utilisation de l'APK**

### Installation :

1. **Transférer l'APK** sur votre Samsung S23 :
   - Par câble USB
   - Par Bluetooth
   - Par cloud (Google Drive, etc.)
   - Par email

2. **Installer l'APK** :
   - Activez **Sources inconnues** dans Paramètres > Sécurité
   - Ouvrez le fichier APK et suivez les instructions

3. **Lancer l'application** :
   - Vous trouverez **PhotoRetouch AI** dans votre liste d'applications

### Fonctionnalités :

#### Écran Principal
- **📷 Choisir une Photo** : Sélectionnez une image depuis votre galerie
- **📸 Prendre une Photo** : Utilisez la caméra pour prendre une photo (à implémenter)
- **⚙️ Outils Avancés** : Accédez à tous les outils de retouche

#### Écran d'Édition
- **✨ Amélioration Auto** : Applique une amélioration intelligente
- **🗑️ Gommer** : Supprimez des objets de l'image
- **🖌️ Cloner** : Clonez des parties de l'image
- **💾 Sauvegarder** : Enregistrez l'image modifiée

#### Écran de Gommage
- Sélectionnez une zone rectangulaire à supprimer
- Choisissez la méthode de remplacement (inpainting recommandé)
- Ajustez la position et la taille
- Appliquez le gommage

#### Écran de Clonage
- Définissez le point source (d'où copier)
- Définissez le point cible (où coller)
- Ajustez la taille du pinceau et l'opacité
- Appliquez le clonage

---

## 🔧 **Dépannage**

### Problèmes courants avec Briefcase :

#### 1. Erreur: Java non trouvé
```
Solution: Installez Java JDK 11+ et configurez JAVA_HOME
```

#### 2. Erreur: Android SDK non trouvé
```
Solution: Installez Android Studio et configurez ANDROID_HOME
```

#### 3. Erreur: NDK non trouvé
```
Solution: Installez le NDK via Android Studio ou sdkmanager
```

#### 4. Build très long
```
Solution: C'est normal pour la première compilation. Les compilations suivantes seront plus rapides.
```

#### 5. Erreur de mémoire
```
Solution: Fermez les autres applications et utilisez au moins 16 Go de RAM.
```

### Problèmes courants avec Buildozer :

#### 1. Erreur: Recipe not found
```
Solution: Mettez à jour Buildozer: pip install --upgrade buildozer
```

#### 2. Erreur: NDK download failed
```
Solution: Téléchargez manuellement le NDK et configurez ANDROID_NDK_HOME
```

#### 3. APK trop grosse
```
Solution: Utilisez android.arch = arm64-v8a au lieu de all
```

---

## ⚡ **Performances**

### Sur Samsung S23 (Snapdragon 8 Gen 2, 8/12 Go RAM)

| Fonctionnalité | Temps estimé | Notes |
|---------------|--------------|-------|
| Amélioration automatique | 1-3 secondes | Très rapide |
| Suppression d'arrière-plan | 2-5 secondes | MediaPipe optimisé |
| Gommage par rectangle | 1-2 secondes | Rapide |
| Clone Stamp | 0.5-1 seconde | Instantané |
| Super-résolution x2 | 5-10 secondes | Dépend de la taille |
| Restauration de photo | 3-8 secondes | Complexe |

### Optimisations :
- Les images sont redimensionnées pour s'adapter à l'écran
- Les modèles IA sont optimisés pour mobile
- Le traitement utilise le CPU (pas besoin de GPU)

---

## 📁 **Structure du Projet**

```
photo-retouch-ai-mobile/
├── src/
│   └── photoretouch_ai/
│       ├── __init__.py
│       ├── __main__.py           # Point d'entrée Kivy
│       ├── app/
│       │   ├── __init__.py
│       │   ├── utils.py           # Fonctions utilitaires
│       │   └── processing/       # Modules de traitement
│       │       ├── __init__.py
│       │       ├── background.py
│       │       ├── enhancers.py
│       │       ├── super_resolution.py
│       │       ├── denoise.py
│       │       ├── restore.py
│       │       ├── object_removal.py
│       │       └── clone_stamp.py
│       └── assets/
│           ├── icon.png          # Icône de l'application
│           └── splash.png         # Écran de splash
├── pyproject.toml                # Configuration du projet
├── briefcase.toml                # Configuration Briefcase
├── buildozer.spec                # Configuration Buildozer
├── requirements.txt              # Dépendances Python
├── build_apk.sh                  # Script de build
└── README.md                     # Ce fichier
```

---

## 🎯 **Conseils pour Samsung S23**

1. **Activer le mode développeur** :
   - Allez dans Paramètres > À propos du téléphone
   - Appuyez 7 fois sur "Numéro de version"
   - Activez "Options de développeur"

2. **Activer le débogage USB** :
   - Dans Options de développeur, activez "Débogage USB"
   - Cela permet de tester l'application directement depuis votre PC

3. **Utiliser un câble USB de qualité** :
   - Pour un transfert rapide de l'APK

4. **Libérer de l'espace** :
   - L'application nécessite environ 500 Mo d'espace

5. **Permissions** :
   - Autorisez l'accès au stockage pour sauvegarder les images
   - Autorisez l'accès à la caméra pour prendre des photos

---

## 📚 **Ressources Utiles**

- **BeeWare Briefcase** : [https://beeware.org/project/projects/tools/briefcase/](https://beeware.org/project/projects/tools/briefcase/)
- **Buildozer** : [https://buildozer.readthedocs.io/](https://buildozer.readthedocs.io/)
- **Kivy** : [https://kivy.org/](https://kivy.org/)
- **Android Developer** : [https://developer.android.com/](https://developer.android.com/)
- **Termux** : [https://termux.com/](https://termux.com/)

---

## 🙏 **Remerciements**

- **BeeWare** pour Briefcase
- **Kivy** pour l'interface utilisateur mobile
- **OpenCV** pour le traitement d'images
- **MediaPipe** pour la segmentation
- **ONNX Runtime** pour l'exécution des modèles IA

---

## 📧 **Support**

Pour toute question ou problème :
- Vérifiez la section **Dépannage** ci-dessus
- Consultez les logs de build pour plus de détails
- Ouvrez une **Issue** sur GitHub

---

**Créé avec ❤️ pour les utilisateurs de Samsung S23 et autres appareils Android**

*Dernière mise à jour: Juin 2025*
