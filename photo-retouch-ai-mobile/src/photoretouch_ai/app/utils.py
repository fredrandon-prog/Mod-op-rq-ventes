# PhotoRetouch AI - Utilitaires
# Fonctions communes pour le traitement d'images

import os
import cv2
import numpy as np
from PIL import Image
import yaml
import logging
from typing import Tuple, Optional, Union
import onnxruntime as ort


# ============================================
# CONFIGURATION
# ============================================

def load_config(config_path: str = "config.yaml") -> dict:
    """Charge la configuration depuis un fichier YAML."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config if config else {}
    except FileNotFoundError:
        logging.warning(f"Fichier de configuration introuvable: {config_path}")
        return {}
    except yaml.YAMLError as e:
        logging.error(f"Erreur de parsing YAML: {e}")
        return {}


# Initialiser la configuration globale
CONFIG = load_config()


# ============================================
# GESTION DES CHEMINS
# ============================================

def get_models_dir() -> str:
    """Retourne le chemin du dossier des modèles."""
    return CONFIG.get("paths", {}).get("models_dir", "./models")


def get_output_dir() -> str:
    """Retourne le chemin du dossier de sortie."""
    output_dir = CONFIG.get("paths", {}).get("output_dir", "./output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_temp_dir() -> str:
    """Retourne le chemin du dossier temporaire."""
    temp_dir = CONFIG.get("paths", {}).get("temp_dir", "./temp")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


# ============================================
# CONVERSION D'IMAGES
# ============================================

def image_to_numpy(image: Union[Image.Image, np.ndarray]) -> np.ndarray:
    """Convertit une image PIL ou numpy en tableau numpy (BGR)."""
    if isinstance(image, Image.Image):
        image = np.array(image)
        if image.ndim == 3 and image.shape[2] == 4:  # RGBA
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        elif image.ndim == 3 and image.shape[2] == 3:  # RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif image.ndim == 2:  # Grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image


def numpy_to_pil(image: np.ndarray) -> Image.Image:
    """Convertit un tableau numpy (BGR) en image PIL (RGB)."""
    if image.ndim == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(image)


def resize_image(image: np.ndarray, max_size: int = 4096) -> np.ndarray:
    """Redimensionne une image pour ne pas dépasser max_size."""
    if max_size <= 0:
        return image
    
    h, w = image.shape[:2]
    if max(h, w) <= max_size:
        return image
    
    scale = max_size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


# ============================================
# GESTION DES MODÈLES ONNX
# ============================================

# Cache pour les sessions ONNX
_onnx_sessions = {}


def get_onnx_session(model_name: str, use_gpu: bool = True) -> Optional[ort.InferenceSession]:
    """
    Charge ou récupère une session ONNX pour un modèle.
    
    Args:
        model_name: Nom du fichier modèle (ex: "selfie_segmentation.onnx")
        use_gpu: Utiliser le GPU si disponible
        
    Returns:
        Session ONNX ou None si échec
    """
    cache_key = (model_name, use_gpu)
    
    if cache_key in _onnx_sessions:
        return _onnx_sessions[cache_key]
    
    try:
        model_path = os.path.join(get_models_dir(), model_name)
        
        if not os.path.exists(model_path):
            logging.warning(f"Modèle introuvable: {model_path}")
            return None
        
        # Configuration des providers
        providers = []
        
        if use_gpu:
            try:
                # Essayer CUDA
                providers.append('CUDAExecutionProvider')
            except:
                try:
                    # Essayer DirectML (Windows)
                    providers.append('DmlExecutionProvider')
                except:
                    pass
        
        # Toujours ajouter CPU comme fallback
        providers.append('CPUExecutionProvider')
        
        # Créer la session
        session = ort.InferenceSession(
            model_path,
            providers=providers,
            sess_options=ort.SessionOptions()
        )
        
        _onnx_sessions[cache_key] = session
        return session
        
    except Exception as e:
        logging.error(f"Erreur de chargement du modèle {model_name}: {e}")
        return None


def clear_onnx_cache():
    """Vide le cache des sessions ONNX."""
    global _onnx_sessions
    _onnx_sessions = {}


# ============================================
# SAUVEGARDE D'IMAGES
# ============================================

def save_image(
    image: Union[Image.Image, np.ndarray],
    output_path: str,
    quality: int = 95,
    format: str = None
) -> str:
    """
    Sauvegarde une image avec les paramètres spécifiés.
    
    Args:
        image: Image à sauvegarder (PIL ou numpy)
        output_path: Chemin de sortie
        quality: Qualité (0-100)
        format: Format (JPEG, PNG, WEBP) ou None pour déduire
        
    Returns:
        Chemin du fichier sauvegardé
    """
    # Créer le dossier parent si nécessaire
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    # Convertir en PIL si nécessaire
    if isinstance(image, np.ndarray):
        image = numpy_to_pil(image)
    
    # Déterminer le format
    if format:
        format = format.upper()
    else:
        ext = os.path.splitext(output_path)[1].lower()
        format = ext[1:].upper() if ext else "JPEG"
    
    # Sauvegarder
    if format == "JPEG":
        image.save(output_path, format="JPEG", quality=quality, optimize=True)
    elif format == "PNG":
        image.save(output_path, format="PNG", compress_level=9)
    elif format == "WEBP":
        image.save(output_path, format="WEBP", quality=quality)
    else:
        image.save(output_path, quality=quality)
    
    return output_path


# ============================================
# FONCTIONS DIVERSES
# ============================================

def generate_output_filename(input_path: str, suffix: str = "_retouched") -> str:
    """Génère un nom de fichier de sortie basé sur le fichier d'entrée."""
    base, ext = os.path.splitext(input_path)
    output_dir = get_output_dir()
    filename = os.path.basename(base) + suffix + ext
    return os.path.join(output_dir, filename)


def get_image_info(image: Union[Image.Image, np.ndarray]) -> dict:
    """Retourne des informations sur une image."""
    if isinstance(image, Image.Image):
        w, h = image.size
        mode = image.mode
    else:
        h, w = image.shape[:2]
        mode = "RGB" if image.ndim == 3 and image.shape[2] == 3 else "L"
    
    return {
        "width": w,
        "height": h,
        "mode": mode,
        "size_mb": (w * h * (3 if mode == "RGB" else 1)) / (1024 * 1024)
    }


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalise une image entre 0 et 1."""
    return image.astype(np.float32) / 255.0


def denormalize_image(image: np.ndarray) -> np.ndarray:
    """Dénormalise une image entre 0 et 255."""
    return (image * 255).clip(0, 255).astype(np.uint8)


# ============================================
# LOGGING
# ============================================

def setup_logging(log_dir: str = None, log_level: str = "INFO") -> logging.Logger:
    """Configure le logging pour l'application."""
    if log_dir is None:
        log_dir = CONFIG.get("advanced", {}).get("logs_dir", "./logs")
    
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger("PhotoRetouchAI")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Handler fichier
    file_handler = logging.FileHandler(os.path.join(log_dir, "photo_retouch.log"))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    
    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)s - %(message)s"
    ))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Initialiser le logger global
logger = setup_logging()
