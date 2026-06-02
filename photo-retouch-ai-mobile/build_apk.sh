#!/bin/bash
# Script de build pour l'APK PhotoRetouch AI
# Ce script utilise BeeWare Briefcase pour créer une APK Android

# Couleurs pour le terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher un message avec couleur
function message {
    local color=$1
    local text=$2
    echo -e "${color}[PhotoRetouch AI] ${text}${NC}"
}

# Fonction pour vérifier si une commande existe
function command_exists {
    command -v "$1" >/dev/null 2>&1
}

# Fonction pour installer une dépendance
function install_dependency {
    local package=$1
    local name=$2
    
    if ! command_exists "$package"; then
        message "$YELLOW" "Installation de $name..."
        if ! pip install "$package"; then
            message "$RED" "Échec de l'installation de $name"
            exit 1
        fi
        message "$GREEN" "$name installé avec succès"
    else
        message "$GREEN" "$name est déjà installé"
    fi
}

# Fonction pour vérifier Java
function check_java {
    message "$BLUE" "Vérification de Java..."
    
    if ! command_exists java; then
        message "$RED" "Java n'est pas installé"
        message "$YELLOW" "Installez Java JDK 11 ou supérieur"
        message "$YELLOW" "Téléchargez depuis: https://adoptium.net/"
        exit 1
    fi
    
    local version=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    local major_version=$(echo "$version" | cut -d'.' -f1)
    
    if [ "$major_version" -lt 11 ]; then
        message "$RED" "Java 11 ou supérieur est requis (vous avez $version)"
        exit 1
    fi
    
    message "$GREEN" "Java $version est installé"
}

# Fonction pour vérifier Android SDK
function check_android_sdk {
    message "$BLUE" "Vérification de l'Android SDK..."
    
    if [ ! -d "$ANDROID_HOME" ] && [ ! -d "$HOME/Android/Sdk" ]; then
        message "$RED" "Android SDK n'est pas installé"
        message "$YELLOW" "Installez Android Studio depuis: https://developer.android.com/studio"
        message "$YELLOW" "Ou installez le SDK avec:"
        message "$YELLOW" "  sdkmanager --install \"platform-tools\" \"platforms;android-34\" \"build-tools;34.0.0\""
        exit 1
    fi
    
    message "$GREEN" "Android SDK est installé"
}

# Fonction pour vérifier les variables d'environnement
function check_environment {
    message "$BLUE" "Vérification des variables d'environnement..."
    
    # Vérifier ANDROID_HOME
    if [ -z "$ANDROID_HOME" ]; then
        if [ -d "$HOME/Android/Sdk" ]; then
            export ANDROID_HOME="$HOME/Android/Sdk"
            message "$YELLOW" "ANDROID_HOME défini à $ANDROID_HOME"
        else
            message "$RED" "ANDROID_HOME n'est pas défini"
            message "$YELLOW" "Exportez ANDROID_HOME=/chemin/vers/android/sdk"
            exit 1
        fi
    fi
    
    # Vérifier ANDROID_NDK_HOME
    if [ -z "$ANDROID_NDK_HOME" ]; then
        local ndk_path="$ANDROID_HOME/ndk"
        if [ -d "$ndk_path" ]; then
            export ANDROID_NDK_HOME="$ndk_path"
            message "$YELLOW" "ANDROID_NDK_HOME défini à $ANDROID_NDK_HOME"
        else
            message "$RED" "ANDROID_NDK_HOME n'est pas défini"
            message "$YELLOW" "Installez le NDK avec Android Studio ou sdkmanager"
            exit 1
        fi
    fi
    
    # Ajouter les outils Android au PATH
    export PATH="$PATH:$ANDROID_HOME/platform-tools"
    export PATH="$PATH:$ANDROID_HOME/tools"
    export PATH="$PATH:$ANDROID_HOME/tools/bin"
    
    message "$GREEN" "Variables d'environnement configurées"
}

# Fonction pour créer l'APK avec Briefcase
function build_with_briefcase {
    message "$BLUE" "Création de l'APK avec BeeWare Briefcase..."
    
    # Aller dans le dossier du projet
    cd "$(dirname "$0")" || exit 1
    
    # Installer Briefcase
    install_dependency "briefcase" "BeeWare Briefcase"
    
    # Vérifier Java
    check_java
    
    # Vérifier Android SDK
    check_android_sdk
    
    # Vérifier les variables d'environnement
    check_environment
    
    # Créer le projet Android
    message "$YELLOW" "Création du projet Android..."
    if ! briefcase create android; then
        message "$RED" "Échec de la création du projet Android"
        exit 1
    fi
    
    # Builder l'APK
    message "$YELLOW" "Build de l'APK (cela peut prendre plusieurs minutes)..."
    if ! briefcase build android; then
        message "$RED" "Échec du build de l'APK"
        exit 1
    fi
    
    # Trouver l'APK générée
    local apk_path=$(find . -name "*.apk" -type f | head -n 1)
    
    if [ -n "$apk_path" ]; then
        message "$GREEN" "APK créée avec succès: $apk_path"
        message "$GREEN" "Vous pouvez maintenant installer l'APK sur votre Samsung S23"
    else
        message "$RED" "APK non trouvée après le build"
        exit 1
    fi
}

# Fonction pour créer l'APK avec Buildozer (alternative)
function build_with_buildozer {
    message "$BLUE" "Création de l'APK avec Buildozer..."
    
    # Aller dans le dossier du projet
    cd "$(dirname "$0")" || exit 1
    
    # Installer Buildozer
    install_dependency "buildozer" "Buildozer"
    
    # Vérifier Java
    check_java
    
    # Vérifier Android SDK
    check_android_sdk
    
    # Vérifier les variables d'environnement
    check_environment
    
    # Initialiser Buildozer
    if [ ! -f "buildozer.spec" ]; then
        message "$YELLOW" "Création du fichier buildozer.spec..."
        buildozer init
    fi
    
    # Builder l'APK
    message "$YELLOW" "Build de l'APK avec Buildozer (cela peut prendre 30-60 minutes)..."
    if ! buildozer -v android debug; then
        message "$RED" "Échec du build de l'APK avec Buildozer"
        exit 1
    fi
    
    # Trouver l'APK générée
    local apk_path=$(find . -path "*/bin/*-debug.apk" -type f | head -n 1)
    
    if [ -n "$apk_path" ]; then
        message "$GREEN" "APK créée avec succès: $apk_path"
        message "$GREEN" "Vous pouvez maintenant installer l'APK sur votre Samsung S23"
    else
        message "$RED" "APK non trouvée après le build"
        exit 1
    fi
}

# Fonction pour afficher l'aide
function show_help {
    echo ""
    message "$BLUE" "Script de build pour PhotoRetouch AI APK"
    echo ""
    message "$YELLOW" "Usage:"
    echo "  ./build_apk.sh [option]"
    echo ""
    message "$YELLOW" "Options:"
    echo "  --briefcase    Utiliser BeeWare Briefcase (recommandé)"
    echo "  --buildozer    Utiliser Buildozer (alternative)"
    echo "  --help, -h     Afficher cette aide"
    echo ""
    message "$YELLOW" "Prérequis:"
    echo "  - Java JDK 11+"
    echo "  - Android SDK (API 24+)"
    echo "  - Android NDK"
    echo "  - Python 3.8+"
    echo "  - pip"
    echo ""
    message "$YELLOW" "Pour Samsung S23:"
    echo "  - Android 14 (API 34) est supporté"
    echo "  - L'APK sera compatible avec votre appareil"
    echo ""
}

# ============================================
# POINT D'ENTRÉE
# ============================================

# Vérifier les arguments
if [ $# -eq 0 ]; then
    # Par défaut, utiliser Briefcase
    build_with_briefcase
elif [ "$1" == "--briefcase" ]; then
    build_with_briefcase
elif [ "$1" == "--buildozer" ]; then
    build_with_buildozer
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
else
    message "$RED" "Option inconnue: $1"
    show_help
    exit 1
fi
