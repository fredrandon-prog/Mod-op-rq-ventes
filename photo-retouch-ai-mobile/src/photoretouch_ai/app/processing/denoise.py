# PhotoRetouch AI - Débruitage
# Module pour le débruitage avancé des images

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


class Denoiser:
    """
    Classe pour le débruitage avancé des images.
    Utilise des techniques classiques et IA pour réduire le bruit.
    """
    
    def __init__(self):
        """Initialise le débruiteur."""
        self.model_name = "denoise.onnx"
        self.session = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialise la session ONNX pour le modèle de débruitage."""
        try:
            use_gpu = True
            self.session = get_onnx_session(self.model_name, use_gpu)
            
            if self.session:
                logger.info("Modèle de débruitage chargé avec succès")
            else:
                logger.info("Modèle de débruitage non trouvé, utilisation des méthodes classiques")
        except Exception as e:
            logger.error(f"Erreur de chargement du modèle de débruitage: {e}")
            self.session = None
    
    def denoise(
        self,
        image: np.ndarray,
        strength: float = 0.85,
        method: str = "auto"
    ) -> np.ndarray:
        """
        Débruite une image.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force du débruitage (0-1)
            method: Méthode à utiliser ("auto", "onnx", "bilateral", "non_local", "wavelet")
            
        Returns:
            Image débruitée
        """
        if method == "auto" or method == "onnx":
            if self.session is not None:
                try:
                    return self._denoise_with_model(image, strength)
                except Exception as e:
                    logger.warning(f"Échec du débruitage avec modèle: {e}")
        
        # Utiliser les méthodes classiques
        if method == "bilateral" or (method == "auto" and self.session is None):
            return self._denoise_bilateral(image, strength)
        elif method == "non_local":
            return self._denoise_non_local(image, strength)
        elif method == "wavelet":
            return self._denoise_wavelet(image, strength)
        else:
            return self._denoise_bilateral(image, strength)
    
    def _denoise_with_model(self, image: np.ndarray, strength: float) -> np.ndarray:
        """
        Débruite une image avec le modèle ONNX.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force du débruitage
            
        Returns:
            Image débruitée
        """
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
    
    def _denoise_bilateral(self, image: np.ndarray, strength: float) -> np.ndarray:
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
        
        # Appliquer le filtre bilatéral sur chaque canal séparément
        channels = cv2.split(image)
        denoised_channels = []
        
        for channel in channels:
            denoised = cv2.bilateralFilter(channel, d, sigma_color, sigma_space)
            denoised_channels.append(denoised)
        
        result = cv2.merge(denoised_channels)
        
        return result
    
    def _denoise_non_local(self, image: np.ndarray, strength: float) -> np.ndarray:
        """
        Débruite une image avec un filtre non-local means.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force du débruitage (0-1)
            
        Returns:
            Image débruitée
        """
        # Calculer les paramètres
        h = int(10 * strength)
        template_window_size = max(7, int(15 * strength))
        search_window_size = max(21, int(35 * strength))
        
        # Appliquer le filtre non-local means
        result = cv2.fastNlMeansDenoisingColored(
            image, 
            None, 
            h, 
            h, 
            template_window_size, 
            search_window_size
        )
        
        return result
    
    def _denoise_wavelet(self, image: np.ndarray, strength: float) -> np.ndarray:
        """
        Débruite une image avec une transformation en ondelettes.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force du débruitage (0-1)
            
        Returns:
            Image débruitée
        """
        # Convertir en niveaux de gris pour le traitement
        if image.ndim == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Appliquer le débruitage par ondelettes
        # (Implémentation simplifiée)
        # Décomposition en ondelettes (simplifiée)
        # Pour une implémentation complète, utiliser pywt
        
        # Méthode alternative: débruitage par seuil
        # Appliquer un flou gaussien léger
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Calculer la différence (détails)
        details = cv2.subtract(gray, blurred)
        
        # Appliquer un seuil sur les détails
        threshold_value = int(30 * (1 - strength))
        _, thresholded = cv2.threshold(details, threshold_value, 255, cv2.THRESH_TOZERO)
        
        # Recombiner
        result_gray = cv2.add(blurred, thresholded)
        
        # Si l'image était en couleur, appliquer le même traitement à chaque canal
        if image.ndim == 3:
            channels = cv2.split(image)
            result_channels = []
            for channel in channels:
                blurred_c = cv2.GaussianBlur(channel, (5, 5), 0)
                details_c = cv2.subtract(channel, blurred_c)
                _, thresholded_c = cv2.threshold(details_c, threshold_value, 255, cv2.THRESH_TOZERO)
                result_c = cv2.add(blurred_c, thresholded_c)
                result_channels.append(result_c)
            result = cv2.merge(result_channels)
        else:
            result = result_gray
        
        return result
    
    def denoise_gaussian(self, image: np.ndarray, strength: float = 0.85) -> np.ndarray:
        """
        Débruite une image avec un filtre gaussien.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force du débruitage (0-1)
            
        Returns:
            Image débruitée
        """
        # Calculer la taille du noyau
        kernel_size = (int(5 * strength) * 2 + 1, int(5 * strength) * 2 + 1)
        
        # Appliquer le filtre gaussien
        result = cv2.GaussianBlur(image, kernel_size, 0)
        
        return result
    
    def denoise_median(self, image: np.ndarray, strength: float = 0.85) -> np.ndarray:
        """
        Débruite une image avec un filtre médian.
        
        Args:
            image: Image d'entrée (BGR)
            strength: Force du débruitage (0-1)
            
        Returns:
            Image débruitée
        """
        # Calculer la taille du noyau
        kernel_size = int(3 * strength) * 2 + 1
        
        # Appliquer le filtre médian
        result = cv2.medianBlur(image, kernel_size)
        
        return result


# Instance globale
denoiser = Denoiser()


# Fonctions simplifiées
def denoise(
    image: np.ndarray,
    strength: float = 0.85,
    method: str = "auto"
) -> np.ndarray:
    """Débruite une image avec la méthode automatique."""
    return denoiser.denoise(image, strength, method)


def denoise_bilateral(image: np.ndarray, strength: float = 0.85) -> np.ndarray:
    """Débruite une image avec un filtre bilatéral."""
    return denoiser._denoise_bilateral(image, strength)


def denoise_non_local(image: np.ndarray, strength: float = 0.85) -> np.ndarray:
    """Débruite une image avec un filtre non-local means."""
    return denoiser._denoise_non_local(image, strength)


def denoise_wavelet(image: np.ndarray, strength: float = 0.85) -> np.ndarray:
    """Débruite une image avec une transformation en ondelettes."""
    return denoiser._denoise_wavelet(image, strength)


def denoise_gaussian(image: np.ndarray, strength: float = 0.85) -> np.ndarray:
    """Débruite une image avec un filtre gaussien."""
    return denoiser.denoise_gaussian(image, strength)


def denoise_median(image: np.ndarray, strength: float = 0.85) -> np.ndarray:
    """Débruite une image avec un filtre médian."""
    return denoiser.denoise_median(image, strength)
