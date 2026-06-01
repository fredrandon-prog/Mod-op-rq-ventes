# PhotoRetouch AI - Amélioration d'images
# Module pour l'amélioration automatique des images (couleurs, contraste, netteté)

import cv2
import numpy as np
from typing import Tuple, Optional
from PIL import Image, ImageEnhance

from ..utils import (
    image_to_numpy,
    numpy_to_pil,
    resize_image,
    normalize_image,
    denormalize_image,
    logger
)


class ImageEnhancer:
    """
    Classe pour l'amélioration automatique des images.
    Utilise des techniques classiques et IA pour améliorer la qualité.
    """
    
    def __init__(self):
        """Initialise l'améliorateur d'images."""
        pass
    
    def auto_enhance(
        self,
        image: np.ndarray,
        brightness: float = 1.0,
        contrast: float = 1.2,
        saturation: float = 1.3,
        sharpness: float = 1.5,
        auto_balance: bool = True
    ) -> np.ndarray:
        """
        Améliore automatiquement une image avec des réglages intelligents.
        
        Args:
            image: Image d'entrée (BGR)
            brightness: Facteur de luminosité (1.0 = original)
            contrast: Facteur de contraste (1.0 = original)
            saturation: Facteur de saturation (1.0 = original)
            sharpness: Facteur de netteté (1.0 = original)
            auto_balance: Appliquer l'équilibrage automatique des couleurs
            
        Returns:
            Image améliorée
        """
        # Convertir en PIL pour les améliorations de base
        pil_image = numpy_to_pil(image)
        
        # Appliquer les améliorations
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(contrast)
        
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(saturation)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(sharpness)
        
        # Convertir en numpy pour les traitements avancés
        result = image_to_numpy(pil_image)
        
        # Équilibrage automatique des couleurs
        if auto_balance:
            result = self._auto_color_balance(result)
        
        return result
    
    def _auto_color_balance(self, image: np.ndarray) -> np.ndarray:
        """
        Équilibre automatiquement les couleurs d'une image.
        
        Args:
            image: Image d'entrée (BGR)
            
        Returns:
            Image avec couleurs équilibrées
        """
        # Convertir en Lab pour un meilleur traitement des couleurs
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Séparer les canaux
        l, a, b = cv2.split(lab)
        
        # Équilibrer les canaux a et b (couleurs)
        a_mean = np.mean(a)
        b_mean = np.mean(b)
        
        # Ajuster pour centrer autour de 128 (neutre)
        a = cv2.add(a, int(128 - a_mean))
        b = cv2.add(b, int(128 - b_mean))
        
        # Recombiner
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return result
    
    def enhance_colors(self, image: np.ndarray, strength: float = 1.5) -> np.ndarray:
        """
        Améliore les couleurs avec un effet vibrant.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force de l'amélioration (1.0 = original)
            
        Returns:
            Image avec couleurs améliorées
        """
        # Convertir en HSV pour manipuler la saturation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # Augmenter la saturation
        s = np.clip(s * strength, 0, 255).astype(np.uint8)
        
        # Recombiner
        hsv = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return result
    
    def enhance_contrast(self, image: np.ndarray, strength: float = 1.5) -> np.ndarray:
        """
        Améliore le contraste avec CLAHE (Contrast Limited Adaptive Histogram Equalization).
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force du contraste (1.0 = original)
            
        Returns:
            Image avec contraste amélioré
        """
        # Convertir en Lab pour un meilleur traitement
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Appliquer CLAHE sur le canal L (luminosité)
        clahe = cv2.createCLAHE(clipLimit=2.0 * strength, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Recombiner
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return result
    
    def enhance_sharpness(self, image: np.ndarray, strength: float = 1.5) -> np.ndarray:
        """
        Améliore la netteté avec un filtre unsharp mask.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force de la netteté (1.0 = original)
            
        Returns:
            Image avec netteté améliorée
        """
        # Appliquer un filtre gaussien
        blurred = cv2.GaussianBlur(image, (0, 0), 3)
        
        # Calculer l'unsharp mask
        unsharp = cv2.addWeighted(image, 1.0 + strength, blurred, -strength, 0)
        
        return unsharp
    
    def denoise_bilateral(self, image: np.ndarray, strength: float = 0.85) -> np.ndarray:
        """
        Débruite une image avec un filtre bilatéral.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force du débruitage (0-1)
            
        Returns:
            Image débruitée
        """
        # Calculer les paramètres en fonction de la force
        d = int(9 * strength)
        sigma_color = 75 * strength
        sigma_space = 75 * strength
        
        result = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
        
        return result
    
    def enhance_details(self, image: np.ndarray, strength: float = 1.5) -> np.ndarray:
        """
        Améliore les détails avec un filtre de haute fréquence.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force de l'amélioration des détails
            
        Returns:
            Image avec détails améliorés
        """
        # Appliquer un filtre passe-haut
        blurred = cv2.GaussianBlur(image, (0, 0), 3)
        high_pass = cv2.subtract(image, blurred)
        
        # Ajouter les détails à l'image originale
        result = cv2.addWeighted(image, 1.0, high_pass, strength, 0)
        
        return result
    
    def auto_white_balance(self, image: np.ndarray) -> np.ndarray:
        """
        Équilibre automatiquement le blanc (white balance).
        
        Args:
            image: Image d'entrée (BGR)
            
        Returns:
            Image avec balance des blancs corrigée
        """
        # Méthode simple: équilibrage des canaux
        b, g, r = cv2.split(image)
        
        # Calculer la moyenne de chaque canal
        b_mean = np.mean(b)
        g_mean = np.mean(g)
        r_mean = np.mean(r)
        
        # Calculer la moyenne globale
        total_mean = (b_mean + g_mean + r_mean) / 3
        
        # Calculer les facteurs de correction
        b_factor = total_mean / b_mean if b_mean > 0 else 1
        g_factor = total_mean / g_mean if g_mean > 0 else 1
        r_factor = total_mean / r_mean if r_mean > 0 else 1
        
        # Appliquer les corrections
        b = cv2.multiply(b, b_factor)
        g = cv2.multiply(g, g_factor)
        r = cv2.multiply(r, r_factor)
        
        # Recombiner
        result = cv2.merge([b, g, r])
        
        return result
    
    def enhance_portrait(self, image: np.ndarray) -> np.ndarray:
        """
        Amélioration spécifique pour les portraits.
        
        Args:
            image: Image d'entrée (BGR)
            
        Returns:
            Image optimisée pour les portraits
        """
        # Appliquer plusieurs améliorations
        result = self.auto_white_balance(image)
        result = self.enhance_colors(result, strength=1.3)
        result = self.enhance_contrast(result, strength=1.2)
        result = self.enhance_sharpness(result, strength=1.3)
        result = self.denoise_bilateral(result, strength=0.7)
        
        return result
    
    def enhance_landscape(self, image: np.ndarray) -> np.ndarray:
        """
        Amélioration spécifique pour les paysages.
        
        Args:
            image: Image d'entrée (BGR)
            
        Returns:
            Image optimisée pour les paysages
        """
        # Appliquer plusieurs améliorations
        result = self.auto_white_balance(image)
        result = self.enhance_contrast(result, strength=1.5)
        result = self.enhance_colors(result, strength=1.4)
        result = self.enhance_sharpness(result, strength=1.2)
        result = self.enhance_details(result, strength=1.3)
        
        return result


# Instance globale
image_enhancer = ImageEnhancer()


# Fonctions simplifiées
def auto_enhance(
    image: np.ndarray,
    brightness: float = 1.0,
    contrast: float = 1.2,
    saturation: float = 1.3,
    sharpness: float = 1.5,
    auto_balance: bool = True
) -> np.ndarray:
    """Amélioration automatique complète."""
    return image_enhancer.auto_enhance(image, brightness, contrast, saturation, sharpness, auto_balance)


def enhance_colors(image: np.ndarray, strength: float = 1.5) -> np.ndarray:
    """Amélioration des couleurs."""
    return image_enhancer.enhance_colors(image, strength)


def enhance_contrast(image: np.ndarray, strength: float = 1.5) -> np.ndarray:
    """Amélioration du contraste."""
    return image_enhancer.enhance_contrast(image, strength)


def enhance_sharpness(image: np.ndarray, strength: float = 1.5) -> np.ndarray:
    """Amélioration de la netteté."""
    return image_enhancer.enhance_sharpness(image, strength)


def denoise_bilateral(image: np.ndarray, strength: float = 0.85) -> np.ndarray:
    """Débruitage bilatéral."""
    return image_enhancer.denoise_bilateral(image, strength)


def enhance_details(image: np.ndarray, strength: float = 1.5) -> np.ndarray:
    """Amélioration des détails."""
    return image_enhancer.enhance_details(image, strength)


def auto_white_balance(image: np.ndarray) -> np.ndarray:
    """Équilibrage automatique du blanc."""
    return image_enhancer.auto_white_balance(image)


def enhance_portrait(image: np.ndarray) -> np.ndarray:
    """Amélioration pour portraits."""
    return image_enhancer.enhance_portrait(image)


def enhance_landscape(image: np.ndarray) -> np.ndarray:
    """Amélioration pour paysages."""
    return image_enhancer.enhance_landscape(image)
