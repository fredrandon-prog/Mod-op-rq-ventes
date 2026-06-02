# PhotoRetouch AI - Suppression d'arrière-plan
# Module pour la suppression intelligente d'arrière-plan

import cv2
import numpy as np
from typing import Tuple, Optional
import mediapipe as mp

from ..utils import (
    image_to_numpy,
    numpy_to_pil,
    resize_image,
    get_models_dir,
    logger
)


class BackgroundRemover:
    """
    Classe pour la suppression d'arrière-plan utilisant MediaPipe Selfie Segmentation.
    Fonctionne en CPU/GPU et ne nécessite pas de connexion internet.
    """
    
    def __init__(self, model_selection: int = 1):
        """
        Initialise le module de suppression d'arrière-plan.
        
        Args:
            model_selection: 0 = modèle général, 1 = modèle optimisé pour les selfies
        """
        self.model_selection = model_selection
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentation = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialise le modèle MediaPipe."""
        try:
            self.segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
                model_selection=self.model_selection
            )
            logger.info("Modèle de segmentation MediaPipe chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur de chargement du modèle de segmentation: {e}")
            self.segmentation = None
    
    def remove_background(
        self,
        image: np.ndarray,
        threshold: float = 0.7,
        background_color: Tuple[int, int, int] = (0, 0, 0),
        return_mask: bool = False
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Supprime l'arrière-plan d'une image.
        
        Args:
            image: Image d'entrée (BGR ou RGB)
            threshold: Seuil de confiance pour la segmentation (0-1)
            background_color: Couleur de l'arrière-plan (BGR)
            return_mask: Si True, retourne aussi le masque
            
        Returns:
            Tuple de (image_sans_arriere_plan, masque) si return_mask=True
            ou juste image_sans_arriere_plan
        """
        if self.segmentation is None:
            logger.error("Modèle de segmentation non initialisé")
            return image if not return_mask else (image, None)
        
        # Convertir en RGB si nécessaire
        if image.ndim == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # Traiter l'image
        results = self.segmentation.process(rgb_image)
        
        if results is None or results.segmentation_mask is None:
            logger.warning("Aucun résultat de segmentation obtenu")
            return image if not return_mask else (image, None)
        
        # Extraire le masque
        mask = results.segmentation_mask
        mask = (mask > threshold).astype(np.uint8) * 255
        
        # Appliquer le masque à l'image
        if image.ndim == 3 and image.shape[2] == 3:
            # Image couleur
            mask_3d = np.stack([mask] * 3, axis=-1)
            foreground = cv2.bitwise_and(image, mask_3d)
            background = np.full_like(image, background_color)
            background = cv2.bitwise_and(background, cv2.bitwise_not(mask_3d))
            result = cv2.add(foreground, background)
        else:
            # Image en niveaux de gris
            foreground = cv2.bitwise_and(image, mask)
            background = np.full_like(image, background_color[0] if len(background_color) > 0 else 0)
            background = cv2.bitwise_and(background, cv2.bitwise_not(mask))
            result = cv2.add(foreground, background)
        
        if return_mask:
            return result, mask
        return result
    
    def replace_background(
        self,
        image: np.ndarray,
        new_background: np.ndarray,
        threshold: float = 0.7
    ) -> np.ndarray:
        """
        Remplace l'arrière-plan par une nouvelle image.
        
        Args:
            image: Image d'entrée (BGR)
            new_background: Nouvelle image d'arrière-plan (BGR)
            threshold: Seuil de confiance pour la segmentation
            
        Returns:
            Image avec le nouvel arrière-plan
        """
        result, mask = self.remove_background(image, threshold, return_mask=True)
        
        if mask is None:
            return image
        
        # Redimensionner le nouvel arrière-plan si nécessaire
        if new_background.shape[:2] != image.shape[:2]:
            new_background = cv2.resize(new_background, (image.shape[1], image.shape[0]))
        
        # Appliquer le nouvel arrière-plan
        if image.ndim == 3 and image.shape[2] == 3:
            mask_3d = np.stack([mask] * 3, axis=-1)
            foreground = cv2.bitwise_and(image, mask_3d)
            background = cv2.bitwise_and(new_background, cv2.bitwise_not(mask_3d))
            result = cv2.add(foreground, background)
        else:
            foreground = cv2.bitwise_and(image, mask)
            background = cv2.bitwise_and(new_background, cv2.bitwise_not(mask))
            result = cv2.add(foreground, background)
        
        return result
    
    def get_mask(self, image: np.ndarray, threshold: float = 0.7) -> np.ndarray:
        """
        Retourne uniquement le masque de segmentation.
        
        Args:
            image: Image d'entrée
            threshold: Seuil de confiance
            
        Returns:
            Masque binaire (255 = premier plan, 0 = arrière-plan)
        """
        result, mask = self.remove_background(image, threshold, return_mask=True)
        return mask


# Instance globale pour réutilisation
background_remover = BackgroundRemover()


def remove_background(
    image: np.ndarray,
    threshold: float = 0.7,
    background_color: Tuple[int, int, int] = (0, 0, 0)
) -> np.ndarray:
    """
    Fonction simplifiée pour supprimer l'arrière-plan.
    
    Args:
        image: Image d'entrée
        threshold: Seuil de confiance
        background_color: Couleur de l'arrière-plan (BGR)
        
    Returns:
        Image sans arrière-plan
    """
    return background_remover.remove_background(image, threshold, background_color)


def replace_background(
    image: np.ndarray,
    new_background: np.ndarray,
    threshold: float = 0.7
) -> np.ndarray:
    """
    Fonction simplifiée pour remplacer l'arrière-plan.
    
    Args:
        image: Image d'entrée
        new_background: Nouvelle image d'arrière-plan
        threshold: Seuil de confiance
        
    Returns:
        Image avec le nouvel arrière-plan
    """
    return background_remover.replace_background(image, new_background, threshold)


def get_segmentation_mask(image: np.ndarray, threshold: float = 0.7) -> np.ndarray:
    """
    Fonction simplifiée pour obtenir le masque de segmentation.
    
    Args:
        image: Image d'entrée
        threshold: Seuil de confiance
        
    Returns:
        Masque binaire
    """
    return background_remover.get_mask(image, threshold)
