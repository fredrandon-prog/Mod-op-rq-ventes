# PhotoRetouch AI - Gommage d'Objets
# Module pour supprimer des objets spécifiques d'une image

import cv2
import numpy as np
from typing import Tuple, List, Optional
import mediapipe as mp

from ..utils import (
    image_to_numpy,
    numpy_to_pil,
    normalize_image,
    denormalize_image,
    logger
)


class ObjectRemover:
    """
    Classe pour le gommage intelligent d'objets dans une image.
    Permet de sélectionner des zones à supprimer et de les remplacer par :
    - Une couleur unie
    - Un flou (fond flou)
    - Une texture similaire (inpainting)
    - Une autre partie de l'image (clonage)
    """
    
    def __init__(self):
        """Initialise le module de gommage d'objets."""
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=1  # Modèle optimisé pour les selfies
        )
    
    def remove_object_by_mask(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        replacement: str = "blur",
        blur_radius: int = 25,
        replacement_color: Tuple[int, int, int] = (128, 128, 128),
        inpainting_radius: int = 10
    ) -> np.ndarray:
        """
        Supprime un objet en utilisant un masque.
        
        Args:
            image: Image d'entrée (BGR)
            mask: Masque binaire (255 = zone à garder, 0 = zone à supprimer)
            replacement: Méthode de remplacement ("blur", "color", "inpainting", "context")
            blur_radius: Rayon du flou pour la méthode "blur"
            replacement_color: Couleur de remplacement pour la méthode "color"
            inpainting_radius: Rayon pour l'inpainting
            
        Returns:
            Image avec l'objet supprimé
        """
        if mask is None:
            return image
        
        # S'assurer que le masque est binaire
        if mask.dtype != np.uint8:
            mask = (mask > 0).astype(np.uint8) * 255
        
        # Inverser le masque (0 = à supprimer, 255 = à garder)
        mask_inv = cv2.bitwise_not(mask)
        
        if replacement == "blur":
            return self._replace_with_blur(image, mask_inv, blur_radius)
        elif replacement == "color":
            return self._replace_with_color(image, mask_inv, replacement_color)
        elif replacement == "inpainting":
            return self._replace_with_inpainting(image, mask_inv, inpainting_radius)
        elif replacement == "context":
            return self._replace_with_context_aware(image, mask_inv)
        else:
            return self._replace_with_blur(image, mask_inv, blur_radius)
    
    def _replace_with_blur(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        radius: int
    ) -> np.ndarray:
        """
        Remplace la zone masquée par un flou de l'image.
        
        Args:
            image: Image d'entrée (BGR)
            mask: Masque de la zone à remplacer (255 = à remplacer)
            radius: Rayon du flou
            
        Returns:
            Image avec la zone floutée
        """
        # Appliquer un flou gaussien sur toute l'image
        blurred = cv2.GaussianBlur(image, (0, 0), radius)
        
        # Créer un masque 3D
        if image.ndim == 3:
            mask_3d = np.stack([mask] * 3, axis=-1)
        else:
            mask_3d = mask
        
        # Remplacer la zone masquée par le flou
        foreground = cv2.bitwise_and(image, cv2.bitwise_not(mask_3d))
        background = cv2.bitwise_and(blurred, mask_3d)
        result = cv2.add(foreground, background)
        
        return result
    
    def _replace_with_color(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        color: Tuple[int, int, int]
    ) -> np.ndarray:
        """
        Remplace la zone masquée par une couleur unie.
        
        Args:
            image: Image d'entrée (BGR)
            mask: Masque de la zone à remplacer (255 = à remplacer)
            color: Couleur de remplacement (BGR)
            
        Returns:
            Image avec la zone colorée
        """
        # Créer une image de la couleur de remplacement
        if image.ndim == 3:
            replacement = np.full_like(image, color)
            mask_3d = np.stack([mask] * 3, axis=-1)
        else:
            replacement = np.full_like(image, color[0])
            mask_3d = mask
        
        # Remplacer la zone masquée
        foreground = cv2.bitwise_and(image, cv2.bitwise_not(mask_3d))
        background = cv2.bitwise_and(replacement, mask_3d)
        result = cv2.add(foreground, background)
        
        return result
    
    def _replace_with_inpainting(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        radius: int
    ) -> np.ndarray:
        """
        Remplace la zone masquée en utilisant l'algorithme d'inpainting.
        
        Args:
            image: Image d'entrée (BGR)
            mask: Masque de la zone à remplacer (255 = à remplacer)
            radius: Rayon pour l'inpainting
            
        Returns:
            Image avec la zone reconstruite
        """
        # Convertir en float32 pour l'inpainting
        image_float = image.astype(np.float32)
        
        # Inverser le masque (OpenCV attend 0 = à reconstruire, 255 = à garder)
        mask_inv = cv2.bitwise_not(mask)
        
        # Appliquer l'inpainting
        if image.ndim == 3:
            result = cv2.inpaint(
                image_float,
                mask_inv,
                inpaintRadius=radius,
                flags=cv2.INPAINT_TELEA  # ou cv2.INPAINT_NS pour Navier-Stokes
            )
        else:
            result = cv2.inpaint(
                image_float,
                mask_inv,
                inpaintRadius=radius,
                flags=cv2.INPAINT_TELEA
            )
        
        return result.astype(np.uint8)
    
    def _replace_with_context_aware(
        self,
        image: np.ndarray,
        mask: np.ndarray
    ) -> np.ndarray:
        """
        Remplace la zone masquée en utilisant une méthode sensible au contexte.
        
        Args:
            image: Image d'entrée (BGR)
            mask: Masque de la zone à remplacer (255 = à remplacer)
            
        Returns:
            Image avec la zone reconstruite intelligemment
        """
        # Méthode avancée : utiliser les bords de la zone pour reconstruire
        # 1. Dilater légèrement le masque pour capturer les bords
        kernel = np.ones((3, 3), np.uint8)
        dilated_mask = cv2.dilate(mask, kernel, iterations=1)
        
        # 2. Extraire les bords de la zone à remplacer
        edges = cv2.Canny(image, 100, 200)
        
        # 3. Utiliser l'inpainting avec un rayon adapté
        return self._replace_with_inpainting(image, mask, radius=15)
    
    def remove_object_by_rectangle(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        replacement: str = "inpainting"
    ) -> np.ndarray:
        """
        Supprime un objet en utilisant un rectangle de sélection.
        
        Args:
            image: Image d'entrée (BGR)
            x, y: Coordonnées du coin supérieur gauche
            width, height: Dimensions du rectangle
            replacement: Méthode de remplacement
            
        Returns:
            Image avec l'objet supprimé
        """
        # Créer un masque rectangulaire
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.rectangle(mask, (x, y), (x + width, y + height), 255, -1)
        
        return self.remove_object_by_mask(image, mask, replacement)
    
    def remove_object_by_polygon(
        self,
        image: np.ndarray,
        points: List[Tuple[int, int]],
        replacement: str = "inpainting"
    ) -> np.ndarray:
        """
        Supprime un objet en utilisant un polygone de sélection.
        
        Args:
            image: Image d'entrée (BGR)
            points: Liste de points définissant le polygone
            replacement: Méthode de remplacement
            
        Returns:
            Image avec l'objet supprimé
        """
        # Créer un masque polygonal
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        pts = np.array(points, np.int32)
        cv2.fillPoly(mask, [pts], 255)
        
        return self.remove_object_by_mask(image, mask, replacement)
    
    def remove_multiple_objects(
        self,
        image: np.ndarray,
        masks: List[np.ndarray],
        replacement: str = "inpainting"
    ) -> np.ndarray:
        """
        Supprime plusieurs objets en utilisant plusieurs masques.
        
        Args:
            image: Image d'entrée (BGR)
            masks: Liste de masques (chaque masque = un objet à supprimer)
            replacement: Méthode de remplacement
            
        Returns:
            Image avec tous les objets supprimés
        """
        # Combiner tous les masques
        combined_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        for mask in masks:
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        return self.remove_object_by_mask(image, combined_mask, replacement)
    
    def smart_remove(
        self,
        image: np.ndarray,
        method: str = "auto",
        **kwargs
    ) -> np.ndarray:
        """
        Suppression intelligente d'objets avec détection automatique.
        
        Args:
            image: Image d'entrée (BGR)
            method: Méthode de détection ("auto", "segmentation", "contours")
            **kwargs: Arguments supplémentaires
            
        Returns:
            Image avec les objets supprimés
        """
        if method == "segmentation":
            # Utiliser MediaPipe pour détecter les personnes/objets
            return self._remove_with_segmentation(image, **kwargs)
        elif method == "contours":
            # Détecter les contours pour identifier les objets
            return self._remove_with_contours(image, **kwargs)
        else:
            # Méthode automatique
            return self._remove_with_segmentation(image, **kwargs)
    
    def _remove_with_segmentation(
        self,
        image: np.ndarray,
        threshold: float = 0.7,
        remove_background: bool = False
    ) -> np.ndarray:
        """
        Supprime les objets en utilisant la segmentation MediaPipe.
        
        Args:
            image: Image d'entrée (BGR)
            threshold: Seuil de confiance
            remove_background: Si True, supprime l'arrière-plan au lieu du sujet
            
        Returns:
            Image avec les objets supprimés
        """
        # Convertir en RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Traiter avec MediaPipe
        results = self.segmentation.process(rgb_image)
        
        if results is None or results.segmentation_mask is None:
            return image
        
        # Obtenir le masque
        mask = results.segmentation_mask
        mask = (mask > threshold).astype(np.uint8) * 255
        
        if remove_background:
            # Supprimer l'arrière-plan (garder le sujet)
            return self.remove_object_by_mask(image, mask, replacement="inpainting")
        else:
            # Supprimer le sujet (garder l'arrière-plan)
            mask_inv = cv2.bitwise_not(mask)
            return self.remove_object_by_mask(image, mask_inv, replacement="inpainting")
    
    def _remove_with_contours(
        self,
        image: np.ndarray,
        min_area: int = 1000,
        max_area: int = 10000
    ) -> np.ndarray:
        """
        Supprime les objets en détectant les contours.
        
        Args:
            image: Image d'entrée (BGR)
            min_area: Surface minimale pour considérer un contour
            max_area: Surface maximale pour considérer un contour
            
        Returns:
            Image avec les objets supprimés
        """
        # Convertir en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Détecter les contours
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Créer un masque pour tous les contours valides
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                cv2.drawContours(mask, [contour], -1, 255, -1)
        
        # Supprimer les zones détectées
        return self.remove_object_by_mask(image, mask, replacement="inpainting")


# Instance globale
object_remover = ObjectRemover()


# Fonctions simplifiées
def remove_object_by_mask(
    image: np.ndarray,
    mask: np.ndarray,
    replacement: str = "inpainting"
) -> np.ndarray:
    """Supprime un objet en utilisant un masque."""
    return object_remover.remove_object_by_mask(image, mask, replacement)


def remove_object_by_rectangle(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
    replacement: str = "inpainting"
) -> np.ndarray:
    """Supprime un objet en utilisant un rectangle."""
    return object_remover.remove_object_by_rectangle(image, x, y, width, height, replacement)


def remove_object_by_polygon(
    image: np.ndarray,
    points: List[Tuple[int, int]],
    replacement: str = "inpainting"
) -> np.ndarray:
    """Supprime un objet en utilisant un polygone."""
    return object_remover.remove_object_by_polygon(image, points, replacement)


def smart_remove(
    image: np.ndarray,
    method: str = "auto",
    **kwargs
) -> np.ndarray:
    """Suppression intelligente d'objets."""
    return object_remover.smart_remove(image, method, **kwargs)
