#!/usr/bin/env python3
# PhotoRetouch AI - Script de téléchargement des modèles ONNX
# Télécharge automatiquement les modèles nécessaires depuis HuggingFace

import os
import sys
import requests
import yaml
from tqdm import tqdm
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils import get_models_dir, logger


# ============================================
# CONFIGURATION
# ============================================

# Liste des modèles disponibles avec leurs URLs
MODELS_CONFIG = {
    "esrgan_tiny.onnx": {
        "name": "Super-Résolution (ESRGAN Tiny)",
        "url": "https://huggingface.co/ai-forever/Real-ESRGAN/resolve/main/RealESRGAN_x4plus.onnx",
        "size": 5.2,  # en MB
        "description": "Modèle léger pour l'agrandissement d'images x2 ou x4"
    },
    "denoise.onnx": {
        "name": "Débruitage (DnCNN)",
        "url": "https://huggingface.co/andrew/Real-ESRGAN/resolve/main/DnCNN.onnx",
        "size": 3.1,
        "description": "Modèle pour la suppression du bruit dans les images"
    },
    "restore.onnx": {
        "name": "Restauration (GFPN)",
        "url": "https://huggingface.co/andrew/Real-ESRGAN/resolve/main/GFPN-Clean.onnx",
        "size": 8.5,
        "description": "Modèle pour la restauration de vieilles photos"
    },
    "color_correction.onnx": {
        "name": "Correction des couleurs",
        "url": "https://huggingface.co/andrew/Real-ESRGAN/resolve/main/ColorCorrection.onnx",
        "size": 2.3,
        "description": "Modèle pour l'équilibrage automatique des couleurs"
    }
}

# URL alternative pour HuggingFace (au cas où)
ALTERNATIVE_URLS = {
    "esrgan_tiny.onnx": [
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.onnx",
        "https://huggingface.co/ai-forever/Real-ESRGAN/resolve/main/RealESRGAN_x4plus.onnx"
    ],
    "denoise.onnx": [
        "https://github.com/cszn/DnCNN/releases/download/v1.0/DnCNN.onnx"
    ]
}


# ============================================
# FONCTIONS DE TÉLÉCHARGEMENT
# ============================================

def get_model_url(model_name: str) -> str:
    """
    Retourne l'URL de téléchargement pour un modèle.
    
    Args:
        model_name: Nom du fichier modèle
        
    Returns:
        URL de téléchargement
    """
    if model_name in MODELS_CONFIG:
        return MODELS_CONFIG[model_name]["url"]
    return None


def get_alternative_urls(model_name: str) -> list:
    """
    Retourne les URLs alternatives pour un modèle.
    
    Args:
        model_name: Nom du fichier modèle
        
    Returns:
        Liste d'URLs alternatives
    """
    return ALTERNATIVE_URLS.get(model_name, [])


def download_file(url: str, save_path: str, progress_bar: bool = True) -> bool:
    """
    Télécharge un fichier depuis une URL.
    
    Args:
        url: URL du fichier
        save_path: Chemin de sauvegarde
        progress_bar: Afficher une barre de progression
        
    Returns:
        True si succès, False sinon
    """
    try:
        # Créer le dossier parent si nécessaire
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Télécharger avec requests
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Obtenir la taille totale
        total_size = int(response.headers.get('content-length', 0))
        
        # Écrire le fichier
        with open(save_path, 'wb') as f:
            if progress_bar and total_size > 0:
                with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=os.path.basename(save_path)
                ) as pbar:
                    for data in response.iter_content(chunk_size=8192):
                        f.write(data)
                        pbar.update(len(data))
            else:
                for data in response.iter_content(chunk_size=8192):
                    f.write(data)
        
        logger.info(f"Fichier téléchargé: {save_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de téléchargement depuis {url}: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        return False


def download_model(model_name: str, models_dir: str = None) -> bool:
    """
    Télécharge un modèle spécifique.
    
    Args:
        model_name: Nom du fichier modèle
        models_dir: Dossier de destination (optionnel)
        
    Returns:
        True si succès, False sinon
    """
    if models_dir is None:
        models_dir = get_models_dir()
    
    # Vérifier si le modèle existe déjà
    model_path = os.path.join(models_dir, model_name)
    if os.path.exists(model_path):
        logger.info(f"Modèle déjà présent: {model_name}")
        return True
    
    # Obtenir l'URL principale
    url = get_model_url(model_name)
    if url is None:
        logger.error(f"Modèle inconnu: {model_name}")
        return False
    
    # Essayer de télécharger depuis l'URL principale
    logger.info(f"Téléchargement de {model_name} depuis {url}...")
    success = download_file(url, model_path)
    
    if success:
        return True
    
    # Essayer les URLs alternatives
    alt_urls = get_alternative_urls(model_name)
    for alt_url in alt_urls:
        logger.info(f"Essai avec URL alternative: {alt_url}")
        success = download_file(alt_url, model_path)
        if success:
            return True
    
    logger.error(f"Échec du téléchargement de {model_name}")
    return False


def download_all_models(models_dir: str = None) -> dict:
    """
    Télécharge tous les modèles disponibles.
    
    Args:
        models_dir: Dossier de destination (optionnel)
        
    Returns:
        Dictionnaire avec les résultats pour chaque modèle
    """
    if models_dir is None:
        models_dir = get_models_dir()
    
    results = {}
    
    for model_name, config in MODELS_CONFIG.items():
        logger.info(f"Traitement de {config['name']} ({model_name})...")
        success = download_model(model_name, models_dir)
        results[model_name] = {
            "success": success,
            "name": config["name"],
            "size_mb": config["size"],
            "path": os.path.join(models_dir, model_name) if success else None
        }
    
    return results


def verify_models(models_dir: str = None) -> dict:
    """
    Vérifie quels modèles sont déjà présents.
    
    Args:
        models_dir: Dossier des modèles
        
    Returns:
        Dictionnaire avec l'état de chaque modèle
    """
    if models_dir is None:
        models_dir = get_models_dir()
    
    status = {}
    
    for model_name, config in MODELS_CONFIG.items():
        model_path = os.path.join(models_dir, model_name)
        exists = os.path.exists(model_path)
        
        if exists:
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            status[model_name] = {
                "exists": True,
                "name": config["name"],
                "size_mb": size_mb,
                "expected_size_mb": config["size"],
                "path": model_path
            }
        else:
            status[model_name] = {
                "exists": False,
                "name": config["name"],
                "size_mb": config["size"],
                "path": model_path
            }
    
    return status


# ============================================
# INTERFACE EN LIGNE DE COMMANDE
# ============================================

def print_header():
    """Affiche l'en-tête du script."""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║     PhotoRetouch AI - Téléchargement des Modèles ONNX            ║
    ║     Application de retouche photo locale avec IA                   ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)


def print_model_status(status: dict):
    """Affiche l'état des modèles."""
    print("\n📊 État des Modèles:")
    print("-" * 80)
    
    for model_name, info in status.items():
        if info["exists"]:
            size = info.get("size_mb", 0)
            expected = info.get("expected_size_mb", 0)
            status_icon = "✅" if abs(size - expected) < 1 else "⚠️"
            print(f"{status_icon} {info['name']:30} | {size:.1f} MB / {expected:.1f} MB")
        else:
            print(f"❌ {info['name']:30} | Non installé ({info['size_mb']:.1f} MB)")
    
    print("-" * 80)


def print_download_results(results: dict):
    """Affiche les résultats du téléchargement."""
    print("\n📥 Résultats du Téléchargement:")
    print("-" * 80)
    
    success_count = sum(1 for r in results.values() if r["success"])
    total_count = len(results)
    
    for model_name, info in results.items():
        if info["success"]:
            print(f"✅ {info['name']:30} | {info['size_mb']:.1f} MB")
        else:
            print(f"❌ {info['name']:30} | Échec")
    
    print("-" * 80)
    print(f"Succès: {success_count}/{total_count} modèles téléchargés")


def main():
    """Fonction principale."""
    import argparse
    
    # Configurer l'argument parser
    parser = argparse.ArgumentParser(
        description="Télécharge les modèles ONNX pour PhotoRetouch AI"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Liste les modèles disponibles"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Vérifie quels modèles sont déjà installés"
    )
    parser.add_argument(
        "--download",
        nargs="*",
        help="Télécharge des modèles spécifiques (ex: esrgan_tiny.onnx)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Télécharge tous les modèles"
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default=None,
        help="Dossier de destination pour les modèles"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force le téléchargement même si le fichier existe"
    )
    
    args = parser.parse_args()
    
    # Afficher l'en-tête
    print_header()
    
    # Vérifier les arguments
    if args.list:
        print("\n📦 Modèles Disponibles:")
        print("-" * 80)
        for model_name, config in MODELS_CONFIG.items():
            print(f"  {model_name:30} | {config['size']:.1f} MB | {config['description']}")
        print("-" * 80)
        return
    
    if args.check:
        status = verify_models(args.models_dir)
        print_model_status(status)
        return
    
    if args.all:
        print("\n🔽 Téléchargement de tous les modèles...")
        results = download_all_models(args.models_dir)
        print_download_results(results)
        return
    
    if args.download:
        print(f"\n🔽 Téléchargement de {len(args.download)} modèle(s)...")
        results = {}
        for model_name in args.download:
            if args.force and os.path.exists(os.path.join(args.models_dir or get_models_dir(), model_name)):
                os.remove(os.path.join(args.models_dir or get_models_dir(), model_name))
            success = download_model(model_name, args.models_dir)
            if model_name in MODELS_CONFIG:
                results[model_name] = {
                    "success": success,
                    "name": MODELS_CONFIG[model_name]["name"],
                    "size_mb": MODELS_CONFIG[model_name]["size"]
                }
        print_download_results(results)
        return
    
    # Si aucun argument, afficher l'aide
    parser.print_help()


# ============================================
# POINT D'ENTRÉE
# ============================================

if __name__ == "__main__":
    main()
