# PhotoRetouch AI - Restauration d'images
# Module pour la restauration de vieilles photos et la correction des défauts

import cv2
import numpy as np
from typing import Tuple, Optional
import onnxruntime as ort

from ..utils import (
    image_to_numpy,
    numpy_to_pil,
    normalize_image,
    denormalize_image,
    get_onnx_session,
    logger
)


class ImageRestorer:
    """
    Classe pour la restauration d'images.
    Permet de corriger les défauts des vieilles photos :
    - Couleurs fanées
    - Rayures et poussière
    - Flou
    - Contraste faible
    """
    
    def __init__(self):
        """Initialise le restaurateur d'images."""
        self.model_name = "restore.onnx"
        self.session = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialise la session ONNX pour le modèle de restauration."""
        try:
            use_gpu = True
            self.session = get_onnx_session(self.model_name, use_gpu)
            
            if self.session:
                logger.info("Modèle de restauration chargé avec succès")
            else:
                logger.info("Modèle de restauration non trouvé, utilisation des méthodes classiques")
        except Exception as e:
            logger.error(f"Erreur de chargement du modèle de restauration: {e}")
            self.session = None
    
    def restore(
        self,
        image: np.ndarray,
        strength: float = 1.0,
        fix_colors: bool = True,
        fix_scratches: bool = True,
        fix_blur: bool = True,
        fix_contrast: bool = True
    ) -> np.ndarray:
        """
        Restaure une vieille photo.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force de la restauration (0-1)
            fix_colors: Corriger les couleurs fanées
            fix_scratches: Corriger les rayures et la poussière
            fix_blur: Corriger le flou
            fix_contrast: Améliorer le contraste
            
        Returns:
            Image restaurée
        """
        result = image.copy()
        
        # Appliquer les corrections dans l'ordre
        if fix_colors:
            result = self._fix_faded_colors(result, strength)
        
        if fix_scratches:
            result = self._remove_scratches(result, strength)
        
        if fix_blur:
            result = self._reduce_blur(result, strength)
        
        if fix_contrast:
            result = self._enhance_old_contrast(result, strength)
        
        return result
    
    def _fix_faded_colors(self, image: np.ndarray, strength: float) -> np.ndarray:
        """
        Corrige les couleurs fanées des vieilles photos.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force de la correction
            
        Returns:
            Image avec couleurs restaurées
        """
        # Convertir en Lab pour un meilleur traitement des couleurs
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Calculer les moyennes
        a_mean = np.mean(a)
        b_mean = np.mean(b)
        
        # Les vieilles photos ont souvent des couleurs désaturées
        # On augmente la saturation des canaux a et b
        a_boost = int((128 - a_mean) * strength * 0.5)
        b_boost = int((128 - b_mean) * strength * 0.5)
        
        a = np.clip(a + a_boost, 0, 255).astype(np.uint8)
        b = np.clip(b + b_boost, 0, 255).astype(np.uint8)
        
        # Recombiner
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return result
    
    def _remove_scratches(self, image: np.ndarray, strength: float) -> np.ndarray:
        """
        Supprime les rayures et la poussière.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force de la suppression
            
        Returns:
            Image sans rayures
        """
        # Utiliser un filtre médian pour supprimer les petits défauts
        kernel_size = int(3 * strength) * 2 + 1
        result = cv2.medianBlur(image, kernel_size)
        
        # Appliquer un débruitage non-local pour les défauts plus importants
        h = int(10 * strength)
        template_window_size = max(7, int(15 * strength))
        search_window_size = max(21, int(35 * strength))
        
        result = cv2.fastNlMeansDenoisingColored(
            result, 
            None, 
            h, 
            h, 
            template_window_size, 
            search_window_size
        )
        
        return result
    
    def _reduce_blur(self, image: np.ndarray, strength: float) -> np.ndarray:
        """
        Réduit le flou des vieilles photos.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force de la réduction du flou
            
        Returns:
            Image moins floue
        """
        # Appliquer un filtre unsharp mask
        blurred = cv2.GaussianBlur(image, (0, 0), 3)
        unsharp = cv2.addWeighted(image, 1.0 + strength * 0.5, blurred, -strength * 0.5, 0)
        
        return unsharp
    
    def _enhance_old_contrast(self, image: np.ndarray, strength: float) -> np.ndarray:
        """
        Améliore le contraste des vieilles photos.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force de l'amélioration
            
        Returns:
            Image avec meilleur contraste
        """
        # Convertir en Lab
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Appliquer CLAHE sur le canal L
        clahe = cv2.createCLAHE(clipLimit=2.0 * strength, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Recombiner
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return result
    
    def restore_with_model(self, image: np.ndarray, strength: float = 1.0) -> np.ndarray:
        """
        Restaure une image avec le modèle ONNX.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force de la restauration
            
        Returns:
            Image restaurée
        """
        if self.session is None:
            return self.restore(image, strength)
        
        try:
            # Convertir en RGB et normaliser
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            input_image = normalize_image(rgb_image)
            
            # Préparer l'entrée pour le modèle
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
        except Exception as e:
            logger.error(f"Échec de la restauration avec modèle: {e}")
            return self.restore(image, strength)
    
    def colorize_bw(self, image: np.ndarray) -> np.ndarray:
        """
        Colorise une image en noir et blanc.
        (Fonctionnalité expérimentale - nécessite un modèle de colorisation)
        
        Args:
            image: Image d'entrée (BGR ou niveaux de gris)
            
        Returns:
            Image colorisée
        """
        # Pour l'instant, retourner l'image originale
        # (La colorisation nécessite un modèle spécifique)
        logger.warning("La colorisation nécessite un modèle dédié (non implémenté)")
        return image
    
    def fix_red_eyes(self, image: np.ndarray) -> np.ndarray:
        """
        Corrige les yeux rouges.
        
        Args:
            image: Image d'entrée (BGR)
            
        Returns:
            Image avec yeux rouges corrigés
        """
        # Détecter les zones rouges (simplifié)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Masque pour les couleurs rouges
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Trouver les contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrer les petits contours (yeux)
        result = image.copy()
        for contour in contours:
            area = cv2.contourArea(contour)
            if 20 < area < 500:  # Taille typique des yeux
                # Dessiner un cercle noir/gris à la place
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)
                
                # Remplacer par une couleur naturelle
                cv2.circle(result, center, radius, (70, 70, 70), -1)
        
        return result


# Instance globale
image_restorer = ImageRestorer()


# Fonctions simplifiées
def restore(
    image: np.ndarray,
    strength: float = 1.0,
    fix_colors: bool = True,
    fix_scratches: bool = True,
    fix_blur: bool = True,
    fix_contrast: bool = True
) -> np.ndarray:
    """Restaure une vieille photo."""
    return image_restorer.restore(image, strength, fix_colors, fix_scratches, fix_blur, fix_contrast)


def fix_faded_colors(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """Corrige les couleurs fanées."""
    return image_restorer._fix_faded_colors(image, strength)


def remove_scratches(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """Supprime les rayures et la poussière."""
    return image_restorer._remove_scratches(image, strength)


def reduce_blur(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """Réduit le flou."""
    return image_restorer._reduce_blur(image, strength)


def enhance_old_contrast(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """Améliore le contraste des vieilles photos."""
    return image_restorer._enhance_old_contrast(image, strength)


def colorize_bw(image: np.ndarray) -> np.ndarray:
    """Colorise une image en noir et blanc."""
    return image_restorer.colorize_bw(image)


def fix_red_eyes(image: np.ndarray) -> np.ndarray:
    """Corrige les yeux rouges."""
    return image_restorer.fix_red_eyes(image)
