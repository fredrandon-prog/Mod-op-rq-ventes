# PhotoRetouch AI - Clone Stamp (Outil de Clonage)
# Module pour l'outil de clonage comme Photoshop

import cv2
import numpy as np
from typing import Tuple, List, Optional

from ..utils import (
    image_to_numpy,
    numpy_to_pil,
    logger
)


class CloneStamp:
    """
    Classe pour l'outil Clone Stamp (clonage).
    Permet de copier une partie de l'image et de la coller sur une autre partie.
    
    Fonctionnalités :
    - Clonage simple (copier-coller)
    - Clonage avec alignement (pour les motifs)
    - Clonage avec rotation
    - Clonage avec mise à l'échelle
    """
    
    def __init__(self):
        """Initialise l'outil Clone Stamp."""
        self.source_point = None  # Point source (d'où on copie)
        self.target_points = []   # Points cible (où on colle)
        self.brush_size = 20      # Taille du pinceau
        self.brush_hardness = 0.8 # Dureté du pinceau (0-1)
        self.opacity = 1.0        # Opacité (0-1)
        self.alignment = False    # Alignement (conserver l'espacement)
    
    def set_source(self, x: int, y: int):
        """
        Définit le point source pour le clonage.
        
        Args:
            x, y: Coordonnées du point source
        """
        self.source_point = (x, y)
        logger.info(f"Point source défini: ({x}, {y})")
    
    def set_brush(self, size: int = 20, hardness: float = 0.8):
        """
        Configure le pinceau de clonage.
        
        Args:
            size: Taille du pinceau
            hardness: Dureté du pinceau (0-1)
        """
        self.brush_size = size
        self.brush_hardness = hardness
    
    def set_opacity(self, opacity: float = 1.0):
        """
        Configure l'opacité du clonage.
        
        Args:
            opacity: Opacité (0-1)
        """
        self.opacity = opacity
    
    def enable_alignment(self, enabled: bool = True):
        """
        Active/désactive l'alignement.
        
        Args:
            enabled: Activer l'alignement
        """
        self.alignment = enabled
    
    def clone(
        self,
        image: np.ndarray,
        target_x: int,
        target_y: int
    ) -> np.ndarray:
        """
        Clone une zone vers une position cible.
        
        Args:
            image: Image d'entrée (BGR)
            target_x, target_y: Coordonnées de la cible
            
        Returns:
            Image avec la zone clonée
        """
        if self.source_point is None:
            logger.warning("Aucun point source défini")
            return image
        
        # Calculer l'offset si l'alignement est activé
        if self.alignment and self.target_points:
            # Utiliser le dernier point cible pour calculer l'offset
            last_target = self.target_points[-1]
            offset_x = target_x - last_target[0]
            offset_y = target_y - last_target[1]
            source_x = self.source_point[0] + offset_x
            source_y = self.source_point[1] + offset_y
        else:
            source_x, source_y = self.source_point
        
        # Cloner la zone
        result = self._clone_area(image, source_x, source_y, target_x, target_y)
        
        # Ajouter le point cible à l'historique
        self.target_points.append((target_x, target_y))
        
        return result
    
    def _clone_area(
        self,
        image: np.ndarray,
        source_x: int,
        source_y: int,
        target_x: int,
        target_y: int
    ) -> np.ndarray:
        """
        Clone une zone circulaire autour du point source vers le point cible.
        
        Args:
            image: Image d'entrée (BGR)
            source_x, source_y: Coordonnées du centre source
            target_x, target_y: Coordonnées du centre cible
            
        Returns:
            Image avec la zone clonée
        """
        result = image.copy()
        h, w = image.shape[:2]
        
        # Calculer la région source (carré autour du point)
        half_size = self.brush_size // 2
        
        # Limiter les coordonnées pour rester dans l'image
        src_x1 = max(0, source_x - half_size)
        src_y1 = max(0, source_y - half_size)
        src_x2 = min(w, source_x + half_size + 1)
        src_y2 = min(h, source_y + half_size + 1)
        
        # Région source
        src_region = image[src_y1:src_y2, src_x1:src_x2]
        
        # Calculer la région cible
        tgt_x1 = max(0, target_x - half_size)
        tgt_y1 = max(0, target_y - half_size)
        tgt_x2 = min(w, target_x + half_size + 1)
        tgt_y2 = min(h, target_y + half_size + 1)
        
        # Ajustement si les régions ont des tailles différentes
        src_h, src_w = src_region.shape[:2]
        tgt_h, tgt_y = tgt_y2 - tgt_y1, tgt_x2 - tgt_x1
        
        # Redimensionner si nécessaire
        if src_h != tgt_h or src_w != tgt_x2 - tgt_x1:
            src_region = cv2.resize(
                src_region,
                (tgt_x2 - tgt_x1, tgt_y2 - tgt_y1),
                interpolation=cv2.INTER_LINEAR
            )
        
        # Appliquer le clonage avec opacité
        if self.opacity < 1.0:
            # Mélanger avec l'image originale
            alpha = self.opacity
            result[tgt_y1:tgt_y2, tgt_x1:tgt_x2] = cv2.addWeighted(
                result[tgt_y1:tgt_y2, tgt_x1:tgt_x2],
                1 - alpha,
                src_region,
                alpha,
                0
            )
        else:
            # Remplacer complètement
            result[tgt_y1:tgt_y2, tgt_x1:tgt_x2] = src_region
        
        return result
    
    def clone_rectangle(
        self,
        image: np.ndarray,
        source_rect: Tuple[int, int, int, int],
        target_rect: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """
        Clone un rectangle vers un autre rectangle.
        
        Args:
            image: Image d'entrée (BGR)
            source_rect: (x, y, width, height) du rectangle source
            target_rect: (x, y, width, height) du rectangle cible
            
        Returns:
            Image avec la zone clonée
        """
        result = image.copy()
        
        src_x, src_y, src_w, src_h = source_rect
        tgt_x, tgt_y, tgt_w, tgt_h = target_rect
        
        # Extraire la région source
        src_region = image[src_y:src_y+src_h, src_x:src_x+src_w]
        
        # Redimensionner si nécessaire
        if src_w != tgt_w or src_h != tgt_h:
            src_region = cv2.resize(
                src_region,
                (tgt_w, tgt_h),
                interpolation=cv2.INTER_LINEAR
            )
        
        # Appliquer le clonage
        if self.opacity < 1.0:
            alpha = self.opacity
            result[tgt_y:tgt_y+tgt_h, tgt_x:tgt_x+tgt_w] = cv2.addWeighted(
                result[tgt_y:tgt_y+tgt_h, tgt_x:tgt_x+tgt_w],
                1 - alpha,
                src_region,
                alpha,
                0
            )
        else:
            result[tgt_y:tgt_y+tgt_h, tgt_x:tgt_x+tgt_w] = src_region
        
        return result
    
    def clone_with_rotation(
        self,
        image: np.ndarray,
        source_center: Tuple[int, int],
        target_center: Tuple[int, int],
        angle: float,
        scale: float = 1.0
    ) -> np.ndarray:
        """
        Clone une zone avec rotation et mise à l'échelle.
        
        Args:
            image: Image d'entrée (BGR)
            source_center: (x, y) du centre source
            target_center: (x, y) du centre cible
            angle: Angle de rotation en degrés
            scale: Facteur de mise à l'échelle
            
        Returns:
            Image avec la zone clonée et transformée
        """
        result = image.copy()
        h, w = image.shape[:2]
        
        # Définir la taille de la région à cloner
        size = self.brush_size * 2
        
        # Extraire la région source (carré autour du centre)
        src_x1 = max(0, source_center[0] - size // 2)
        src_y1 = max(0, source_center[1] - size // 2)
        src_x2 = min(w, source_center[0] + size // 2)
        src_y2 = min(h, source_center[1] + size // 2)
        
        src_region = image[src_y1:src_y2, src_x1:src_x2]
        
        # Calculer le centre de la région source
        src_region_h, src_region_w = src_region.shape[:2]
        src_region_center = (src_region_w // 2, src_region_h // 2)
        
        # Appliquer la rotation
        rotation_matrix = cv2.getRotationMatrix2D(
            src_region_center,
            angle,
            scale
        )
        
        rotated_region = cv2.warpAffine(
            src_region,
            rotation_matrix,
            (src_region_w, src_region_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        # Calculer la région cible
        tgt_x1 = max(0, target_center[0] - src_region_w // 2)
        tgt_y1 = max(0, target_center[1] - src_region_h // 2)
        tgt_x2 = min(w, target_center[0] + src_region_w // 2)
        tgt_y2 = min(h, target_center[1] + src_region_h // 2)
        
        # Redimensionner si nécessaire
        final_w = tgt_x2 - tgt_x1
        final_h = tgt_y2 - tgt_y1
        if rotated_region.shape[1] != final_w or rotated_region.shape[0] != final_h:
            rotated_region = cv2.resize(
                rotated_region,
                (final_w, final_h),
                interpolation=cv2.INTER_LINEAR
            )
        
        # Appliquer le clonage
        if self.opacity < 1.0:
            alpha = self.opacity
            result[tgt_y1:tgt_y2, tgt_x1:tgt_x2] = cv2.addWeighted(
                result[tgt_y1:tgt_y2, tgt_x1:tgt_x2],
                1 - alpha,
                rotated_region,
                alpha,
                0
            )
        else:
            result[tgt_y1:tgt_y2, tgt_x1:tgt_x2] = rotated_region
        
        return result
    
    def pattern_clone(
        self,
        image: np.ndarray,
        source_rect: Tuple[int, int, int, int],
        target_region: Tuple[int, int, int, int],
        pattern_spacing: int = 50
    ) -> np.ndarray:
        """
        Clone un motif de manière répétée dans une région.
        
        Args:
            image: Image d'entrée (BGR)
            source_rect: (x, y, width, height) du motif source
            target_region: (x, y, width, height) de la région cible
            pattern_spacing: Espacement entre les motifs
            
        Returns:
            Image avec le motif cloné
        """
        result = image.copy()
        
        src_x, src_y, src_w, src_h = source_rect
        tgt_x, tgt_y, tgt_w, tgt_h = target_region
        
        # Extraire le motif source
        pattern = image[src_y:src_y+src_h, src_x:src_x+src_w]
        
        # Cloner le motif dans la région cible
        for i in range(tgt_x, tgt_x + tgt_w, pattern_spacing):
            for j in range(tgt_y, tgt_y + tgt_h, pattern_spacing):
                # Calculer la position de destination
                dst_x = i
                dst_y = j
                
                # Limiter pour rester dans l'image
                if dst_x + src_w > tgt_x + tgt_w:
                    dst_x = tgt_x + tgt_w - src_w
                if dst_y + src_h > tgt_y + tgt_h:
                    dst_y = tgt_y + tgt_h - src_h
                
                # Cloner le motif
                if dst_x >= tgt_x and dst_y >= tgt_y:
                    result[dst_y:dst_y+src_h, dst_x:dst_x+src_w] = pattern
        
        return result
    
    def heal_brush(
        self,
        image: np.ndarray,
        target_x: int,
        target_y: int,
        sample_radius: int = 5
    ) -> np.ndarray:
        """
        Outil de correction (Healing Brush) - mélange la zone source avec la cible.
        
        Args:
            image: Image d'entrée (BGR)
            target_x, target_y: Coordonnées de la cible
            sample_radius: Rayon pour l'échantillonnage
            
        Returns:
            Image avec la zone corrigée
        """
        if self.source_point is None:
            return image
        
        result = image.copy()
        
        # Calculer la région source (autour du point source)
        src_x, src_y = self.source_point
        
        # Échantillonner la couleur et la texture autour du point source
        sample_region = image[
            max(0, src_y - sample_radius):min(image.shape[0], src_y + sample_radius + 1),
            max(0, src_x - sample_radius):min(image.shape[1], src_x + sample_radius + 1)
        ]
        
        # Calculer la couleur moyenne
        avg_color = np.mean(sample_region, axis=(0, 1)).astype(np.uint8)
        
        # Appliquer un mélange entre la couleur moyenne et la zone cible
        half_size = self.brush_size // 2
        tgt_x1 = max(0, target_x - half_size)
        tgt_y1 = max(0, target_y - half_size)
        tgt_x2 = min(image.shape[1], target_x + half_size + 1)
        tgt_y2 = min(image.shape[0], target_y + half_size + 1)
        
        # Créer un masque circulaire pour un effet plus naturel
        mask = np.zeros((tgt_y2 - tgt_y1, tgt_x2 - tgt_x1), dtype=np.float32)
        center = (mask.shape[1] // 2, mask.shape[0] // 2)
        cv2.circle(mask, center, min(center) - 1, 1.0, -1)
        
        # Appliquer le mélange
        for c in range(image.shape[2] if image.ndim == 3 else 1):
            if image.ndim == 3:
                channel = result[tgt_y1:tgt_y2, tgt_x1:tgt_x2, c]
            else:
                channel = result[tgt_y1:tgt_y2, tgt_x1:tgt_x2]
            
            blended = cv2.addWeighted(
                channel,
                0.7,
                np.full_like(channel, avg_color[c] if image.ndim == 3 else avg_color[0]),
                0.3,
                0
            )
            
            if image.ndim == 3:
                result[tgt_y1:tgt_y2, tgt_x1:tgt_x2, c] = blended.astype(np.uint8)
            else:
                result[tgt_y1:tgt_y2, tgt_x1:tgt_x2] = blended.astype(np.uint8)
        
        return result
    
    def reset(self):
        """Réinitialise l'outil Clone Stamp."""
        self.source_point = None
        self.target_points = []


# Instance globale
clone_stamp = CloneStamp()


# Fonctions simplifiées
def set_clone_source(x: int, y: int):
    """Définit le point source pour le clonage."""
    clone_stamp.set_source(x, y)


def clone_area(
    image: np.ndarray,
    target_x: int,
    target_y: int,
    brush_size: int = 20,
    opacity: float = 1.0
) -> np.ndarray:
    """Clone une zone vers une position cible."""
    clone_stamp.set_brush(brush_size)
    clone_stamp.set_opacity(opacity)
    return clone_stamp.clone(image, target_x, target_y)


def clone_rectangle(
    image: np.ndarray,
    source_rect: Tuple[int, int, int, int],
    target_rect: Tuple[int, int, int, int],
    opacity: float = 1.0
) -> np.ndarray:
    """Clone un rectangle vers un autre rectangle."""
    clone_stamp.set_opacity(opacity)
    return clone_stamp.clone_rectangle(image, source_rect, target_rect)


def clone_with_rotation(
    image: np.ndarray,
    source_center: Tuple[int, int],
    target_center: Tuple[int, int],
    angle: float,
    scale: float = 1.0,
    brush_size: int = 20
) -> np.ndarray:
    """Clone avec rotation et mise à l'échelle."""
    clone_stamp.set_brush(brush_size)
    return clone_stamp.clone_with_rotation(image, source_center, target_center, angle, scale)


def pattern_clone(
    image: np.ndarray,
    source_rect: Tuple[int, int, int, int],
    target_region: Tuple[int, int, int, int],
    spacing: int = 50
) -> np.ndarray:
    """Clone un motif de manière répétée."""
    return clone_stamp.pattern_clone(image, source_rect, target_region, spacing)


def heal_brush(
    image: np.ndarray,
    target_x: int,
    target_y: int,
    brush_size: int = 20,
    sample_radius: int = 5
) -> np.ndarray:
    """Outil de correction (Healing Brush)."""
    clone_stamp.set_brush(brush_size)
    return clone_stamp.heal_brush(image, target_x, target_y, sample_radius)
