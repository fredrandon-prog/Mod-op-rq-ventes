# 🖼️ PhotoRetouch AI - Application de Retouche Photo Locale avec IA

**Application 100% locale, sans censure, pour retoucher vos photos avec l'intelligence artificielle**

![PhotoRetouch AI](https://img.shields.io/badge/Status-Actif-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![License](https://img.shields.io/badge/License-MIT-orange)

---

## ✨ **Fonctionnalités**

### 🎯 **Retouches Automatiques**
- ✅ **Amélioration automatique** - Correction intelligente des couleurs, contraste et netteté
- ✅ **Équilibrage des couleurs** - Correction des dominantes de couleur
- ✅ **Amélioration du contraste** - CLAHE pour un contraste optimal
- ✅ **Amélioration de la netteté** - Filtre unsharp mask professionnel

### 🎨 **Traitements Avancés**
- ✅ **Suppression d'arrière-plan** - Isolation du sujet en un clic (MediaPipe)
- ✅ **Remplacement d'arrière-plan** - Changez l'arrière-plan de vos photos
- ✅ **Super-résolution** - Agrandissement x2 ou x4 sans perte de qualité (ESRGAN)
- ✅ **Débruitage** - Réduction du bruit et du grain (plusieurs méthodes)
- ✅ **Restauration de vieilles photos** - Correction des couleurs fanées, rayures, flou
- ✅ **Correction des yeux rouges** - Suppression automatique des yeux rouges

### 📸 **Optimisations Spécifiques**
- ✅ **Mode Portrait** - Optimisé pour les photos de personnes
- ✅ **Mode Paysage** - Optimisé pour les photos de paysages
- ✅ **Amélioration des détails** - Mise en valeur des textures

### 🔒 **Sans Censure**
- ✅ **100% Local** - Aucune donnée n'est envoyée sur internet
- ✅ **Sans restriction** - Traite **toutes** les images sans filtrage
- ✅ **Confidentialité totale** - Vos photos restent sur votre machine

---

## 📋 **Table des Matières**

1. [Installation](#-installation)
2. [Utilisation](#-utilisation)
3. [Fonctionnalités Détaillées](#-fonctionnalités-détaillées)
4. [Configuration](#-configuration)
5. [Modèles IA](#-modèles-ia)
6. [Exemples](#-exemples)
7. [Contribution](#-contribution)
8. [Licence](#-licence)

---

## 🚀 **Installation**

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- 2 Go d'espace disque minimum
- 4 Go de RAM recommandés (8 Go pour les grandes images)

### Installation sur Windows/Linux/macOS

```bash
# Cloner le dépôt (si vous l'avez)
git clone https://github.com/votre-utilisateur/photo-retouch-ai.git
cd photo-retouch-ai

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Installation rapide (sans environnement virtuel)

```bash
pip install streamlit opencv-python-headless Pillow numpy onnxruntime mediapipe
```

---

## 🎮 **Utilisation**

### Démarrer l'application

```bash
# Depuis le dossier photo-retouch-ai
streamlit run app/main.py
```

L'application s'ouvrira dans votre navigateur par défaut à l'adresse `http://localhost:8501`.

### Modes Disponibles

#### 1️⃣ **Retouche Simple**
- Glissez-déposez une image
- Sélectionnez une opération
- Ajustez les paramètres
- Appliquez et téléchargez le résultat

#### 2️⃣ **Retouche Avancée**
- Créez un pipeline de traitement
- Appliquez plusieurs opérations successives
- Ajustez les paramètres pour chaque opération
- Idéal pour des résultats professionnels

#### 3️⃣ **Traitement par Lots**
- Traitez plusieurs images en une seule fois
- Appliquez la même opération à toutes les images
- Gain de temps pour les grandes collections

---

## 🔍 **Fonctionnalités Détaillées**

### 🎭 Suppression d'Arrière-Plan

Utilise **MediaPipe Selfie Segmentation** pour isoler automatiquement le sujet de l'image.

**Paramètres:**
- `Seuil` (0.1-0.9) : Sensibilité de la détection
- `Couleur d'arrière-plan` : Couleur pour remplacer l'arrière-plan supprimé

**Exemple d'utilisation:**
```python
from processing.background import remove_background

result = remove_background(image, threshold=0.7, background_color=(0, 0, 0))  # Fond noir
```

### 🌈 Amélioration des Couleurs

Améliore la saturation et l'équilibre des couleurs.

**Paramètres:**
- `Force` (0.1-2.0) : Intensité de l'amélioration

### 📊 Amélioration du Contraste

Utilise **CLAHE** (Contrast Limited Adaptive Histogram Equalization) pour un contraste optimal.

**Paramètres:**
- `Force` (0.1-2.0) : Intensité du contraste

### 🔍 Amélioration de la Netteté

Applique un filtre **unsharp mask** pour des images plus nettes.

**Paramètres:**
- `Force` (0.1-2.0) : Intensité de la netteté

### 🎯 Amélioration Automatique

Combine plusieurs améliorations pour un résultat optimal en un seul clic.

**Paramètres:**
- `Luminosité` (0.1-2.0)
- `Contraste` (0.1-2.0)
- `Saturation` (0.1-2.0)
- `Netteté` (0.1-2.0)
- `Équilibrage automatique` (Oui/Non)

### 🧹 Débruitage

Plusieurs méthodes disponibles :
- **Bilatéral** : Préserve les bords tout en réduisant le bruit
- **Non-Local Means** : Très efficace pour le bruit de haute fréquence
- **Ondelettes** : Pour un débruitage avancé

**Paramètres:**
- `Force` (0.1-1.0) : Intensité du débruitage
- `Méthode` : Choix de l'algorithme

### 🔺 Super-Résolution

Agrandit les images **x2 ou x4** sans perte de qualité.

**Modèles:**
- ESRGAN Tiny (léger, compatible CPU)
- ESRGAN x2, x4 (pour des résultats optimaux)

**Note:** Les modèles ESRGAN nécessitent des fichiers ONNX supplémentaires.

### 🏛️ Restauration de Vieilles Photos

Corrige les défauts des vieilles photos :
- Couleurs fanées
- Rayures et poussière
- Flou
- Contraste faible

**Paramètres:**
- `Force` (0.1-1.0) : Intensité globale
- Options individuelles pour chaque correction

### 👤 Mode Portrait

Optimisation spécifique pour les photos de personnes :
- Équilibrage des couleurs de peau
- Amélioration des détails du visage
- Débruitage doux

### 🌄 Mode Paysage

Optimisation spécifique pour les paysages :
- Amélioration des couleurs du ciel et de la végétation
- Contraste accru
- Netteté des détails

---

## ⚙️ **Configuration**

### Fichier `config.yaml`

```yaml
# Paramètres généraux
app:
  name: "PhotoRetouch AI"
  version: "1.0.0"
  description: "Application de retouche photo locale avec IA"

# Chemins
paths:
  models_dir: "./models"      # Dossier des modèles ONNX
  output_dir: "./output"      # Dossier de sortie
  temp_dir: "./temp"          # Dossier temporaire

# Paramètres des modèles
models:
  background_removal:
    enabled: true
    confidence_threshold: 0.7
  
  super_resolution:
    enabled: true
    scale: 2

# Paramètres de traitement
processing:
  output_quality: 95      # Qualité JPEG (0-100)
  output_format: "JPEG"    # JPEG, PNG, WEBP
  max_size: 4096          # Taille maximale (0 = illimité)
  use_gpu: true           # Utiliser le GPU si disponible
  cpu_threads: 4          # Nombre de threads CPU

# Interface
ui:
  language: "fr"
  theme: "dark"
  preview_size: 800
```

---

## 🤖 **Modèles IA**

### Modèles Intégrés (pas de téléchargement nécessaire)

| Modèle | Technologie | Taille | Fonction |
|--------|-------------|--------|----------|
| Selfie Segmentation | MediaPipe | ~2.5 MB | Suppression d'arrière-plan |

### Modèles Optionnels (nécessitent téléchargement)

| Modèle | Taille | Fonction | Source |
|--------|--------|----------|--------|
| `esrgan_tiny.onnx` | ~5 MB | Super-résolution x2/x4 | [HuggingFace](https://huggingface.co/) |
| `denoise.onnx` | ~3 MB | Débruitage avancé | [HuggingFace](https://huggingface.co/) |
| `restore.onnx` | ~8 MB | Restauration de photos | [HuggingFace](https://huggingface.co/) |

### Comment obtenir les modèles ONNX ?

1. **Téléchargement manuel:**
   - Visitez [HuggingFace Model Hub](https://huggingface.co/models)
   - Recherchez les modèles ESRGAN, denoise, etc.
   - Téléchargez les fichiers `.onnx`
   - Placez-les dans le dossier `models/`

2. **Script de téléchargement (à venir):**
   ```bash
   python scripts/download_models.py
   ```

---

## 📸 **Exemples**

### Exemple 1: Suppression d'arrière-plan

**Avant:**
![Avant](examples/before_background.jpg)

**Après:**
![Après](examples/after_background.jpg)

### Exemple 2: Restauration de vieille photo

**Avant:**
![Avant](examples/before_restore.jpg)

**Après:**
![Après](examples/after_restore.jpg)

### Exemple 3: Super-résolution

**Avant (256x256):**
![Avant](examples/before_sr.jpg)

**Après (512x512):**
![Après](examples/after_sr.jpg)

---

## 🛠️ **Utilisation en Ligne de Commande**

### Traitement d'une seule image

```bash
# Syntax
python scripts/process_image.py --input input.jpg --output output.jpg --operation auto_enhance

# Exemples
python scripts/process_image.py --input photo.jpg --output result.jpg --operation remove_background
python scripts/process_image.py --input photo.jpg --output result.jpg --operation enhance_colors --strength 1.5
```

### Traitement par lots

```bash
python scripts/batch_process.py --input_dir input/ --output_dir output/ --operation auto_enhance
```

---

## 📊 **Performances**

### Configuration Minimale
- CPU: Intel i3 / AMD Ryzen 3
- RAM: 4 Go
- Temps de traitement: 2-5 secondes par image

### Configuration Recommandée
- CPU: Intel i5 / AMD Ryzen 5
- RAM: 8 Go
- GPU: NVIDIA GTX 1060 ou supérieur (optionnel)
- Temps de traitement: 0.5-2 secondes par image

### Configuration Optimale
- CPU: Intel i7 / AMD Ryzen 7
- RAM: 16 Go
- GPU: NVIDIA RTX 2060 ou supérieur
- Temps de traitement: 0.1-0.5 secondes par image

---

## 🤝 **Contribution**

Les contributions sont les bienvenues ! Voici comment contribuer :

1. **Forker** le dépôt
2. **Créer** une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Commiter** vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. **Pousser** vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. **Ouvrir** une Pull Request

### Idées de Contribution
- Ajouter de nouveaux modèles IA
- Améliorer l'interface utilisateur
- Optimiser les performances
- Ajouter de nouvelles fonctionnalités de retouche
- Traduire l'application dans d'autres langues

---

## 📜 **Licence**

Ce projet est sous licence **MIT** - vous êtes libre de l'utiliser, le modifier et le distribuer.

```
MIT License

Copyright (c) 2025 PhotoRetouch AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 **Remerciements**

- [Streamlit](https://streamlit.io/) - Pour l'interface utilisateur
- [OpenCV](https://opencv.org/) - Pour le traitement d'images
- [MediaPipe](https://mediapipe.dev/) - Pour la segmentation
- [ONNX Runtime](https://onnxruntime.ai/) - Pour l'exécution des modèles IA
- [HuggingFace](https://huggingface.co/) - Pour les modèles pré-entraînés

---

## 📧 **Contact**

Pour toute question ou suggestion, n'hésitez pas à ouvrir une **Issue** sur GitHub.

---

**Créé avec ❤️ pour la communauté de la retouche photo**

*Dernière mise à jour: Juin 2025*
