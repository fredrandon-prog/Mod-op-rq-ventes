# PhotoRetouch AI - Super Résolution
# Module pour l'agrandissement d'images avec IA (ESRGAN léger)

import cv2
import numpy as np
from typing import Tuple, Optional
import onnxruntime as ort

from ..utils import (
    image_to_numpy,
    numpy_to_pil,
    resize_image,
    normalize_image,
    denormalize_image,
    get_onnx_session,
    get_models_dir,
    logger
)


class SuperResolutionModel:
    """
    Classe pour la super-résolution utilisant un modèle ESRGAN léger.
    Permet d'agrandir les images jusqu'à 4x sans perte de qualité.
    """
    
    def __init__(self, scale: int = 2):
        """
        Initialise le modèle de super-résolution.
        
        Args:
            scale: Facteur d'agrandissement (2 ou 4)
        """
        self.scale = scale
        self.model_name = f"esrgan_x{scale}.onnx"
        self.session = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialise la session ONNX pour le modèle ESRGAN."""
        try:
            use_gpu = True  # Utiliser le GPU si disponible
            self.session = get_onnx_session(self.model_name, use_gpu)
            
            if self.session is None:
                # Essayer avec un nom de modèle alternatif
                self.model_name = "esrgan_tiny.onnx"
                self.session = get_onnx_session(self.model_name, use_gpu)
            
            if self.session:
                logger.info(f"Modèle ESRGAN x{self.scale} chargé avec succès")
            else:
                logger.warning(f"Modèle ESRGAN x{self.scale} non trouvé, utilisation du redimensionnement classique")
        except Exception as e:
            logger.error(f"Erreur de chargement du modèle ESRGAN: {e}")
            self.session = None
    
    def upscale(
        self,
        image: np.ndarray,
        scale: int = None,
        output_size: Tuple[int, int] = None
    ) -> np.ndarray:
        """
        Agrandit une image avec super-résolution.
        
        Args:
            image: Image d'entrée (BGR)
            scale: Facteur d'agrandissement (remplace self.scale si spécifié)
            output_size: Taille de sortie exacte (largeur, hauteur)
            
        Returns:
            Image agrandie
        """
        target_scale = scale if scale is not None else self.scale
        
        # Si une taille de sortie est spécifiée, calculer le facteur
        if output_size is not None:
            h, w = image.shape[:2]
            target_scale_w = output_size[0] / w
            target_scale_h = output_size[1] / h
            target_scale = max(target_scale_w, target_scale_h)
        
        # Si le modèle est disponible, l'utiliser
        if self.session is not None:
            try:
                return self._upscale_with_model(image, target_scale)
            except Exception as e:
                logger.warning(f"Échec de la super-résolution avec modèle: {e}")
        
        # Sinon, utiliser le redimensionnement classique
        return self._upscale_classic(image, target_scale)
    
    def _upscale_with_model(self, image: np.ndarray, scale: int) -> np.ndarray:
        """
        Agrandit une image avec le modèle ESRGAN.
        
        Args:
            image: Image d'entrée (BGR)
            scale: Facteur d'agrandissement
            
        Returns:
            Image agrandie
        """
        # Convertir en RGB et normaliser
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_image = normalize_image(rgb_image)
        
        # Préparer l'entrée pour le modèle
        # ESRGAN attend une image en format CHW (Canaux, Hauteur, Largeur)
        input_tensor = np.transpose(input_image, (2, 0, 1))
        input_tensor = np.expand_dims(input_tensor, axis=0).astype(np.float32)
        
        # Exécuter l'inférence
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name
        
        outputs = self.session.run(
            [output_name],
            {input_name: input_tensor}
        )
        
        # Traiter la sortie
        output_tensor = outputs[0][0]
        output_tensor = np.transpose(output_tensor, (1, 2, 0))
        output_image = denormalize_image(output_tensor)
        
        # Convertir en BGR
        result = cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR)
        
        return result
    
    def _upscale_classic(self, image: np.ndarray, scale: int) -> np.ndarray:
        """
        Agrandit une image avec des méthodes classiques.
        
        Args:
            image: Image d'entrée (BGR)
            scale: Facteur d'agrandissement
            
        Returns:
            Image agrandie
        """
        h, w = image.shape[:2]
        new_w, new_h = int(w * scale), int(h * scale)
        
        # Utiliser l'interpolation lanczos pour une meilleure qualité
        result = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        return result
    
    def upscale_to_size(self, image: np.ndarray, width: int, height: int) -> np.ndarray:
        """
        Agrandit une image à une taille spécifique.
        
        Args:
            image: Image d'entrée (BGR)
            width: Largeur de sortie
            height: Hauteur de sortie
            
        Returns:
            Image redimensionnée
        """
        return self.upscale(image, output_size=(width, height))


# Instance globale pour x2
sr_model_x2 = SuperResolutionModel(scale=2)

# Instance globale pour x4
sr_model_x4 = SuperResolutionModel(scale=4)


# Fonctions simplifiées
def upscale_x2(image: np.ndarray) -> np.ndarray:
    """Agrandit une image x2 avec super-résolution."""
    return sr_model_x2.upscale(image, scale=2)


def upscale_x4(image: np.ndarray) -> np.ndarray:
    """Agrandit une image x4 avec super-résolution."""
    return sr_model_x4.upscale(image, scale=4)


def upscale_to_size(image: np.ndarray, width: int, height: int) -> np.ndarray:
    """Agrandit une image à une taille spécifique."""
    return sr_model_x2.upscale_to_size(image, width, height)


def upscale(image: np.ndarray, scale: int = 2) -> np.ndarray:
    """
    Agrandit une image avec super-résolution.
    
    Args:
        image: Image d'entrée
        scale: Facteur d'agrandissement (2 ou 4)
        
    Returns:
        Image agrandie
    """
    if scale == 4:
        return sr_model_x4.upscale(image, scale=4)
    else:
        return sr_model_x2.upscale(image, scale=scale)
