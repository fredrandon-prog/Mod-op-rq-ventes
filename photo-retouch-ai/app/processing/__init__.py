# PhotoRetouch AI - Module de traitement des images
# Package pour toutes les fonctionnalités de retouche photo

from .background import (
    BackgroundRemover,
    background_remover,
    remove_background,
    replace_background,
    get_segmentation_mask
)

from .enhancers import (
    ImageEnhancer,
    image_enhancer,
    auto_enhance,
    enhance_colors,
    enhance_contrast,
    enhance_sharpness,
    denoise_bilateral,
    enhance_details,
    auto_white_balance,
    enhance_portrait,
    enhance_landscape
)

from .super_resolution import (
    SuperResolutionModel,
    sr_model_x2,
    sr_model_x4,
    upscale_x2,
    upscale_x4,
    upscale_to_size,
    upscale
)

from .denoise import (
    Denoiser,
    denoiser,
    denoise,
    denoise_bilateral,
    denoise_non_local,
    denoise_wavelet,
    denoise_gaussian,
    denoise_median
)

from .restore import (
    ImageRestorer,
    image_restorer,
    restore,
    fix_faded_colors,
    remove_scratches,
    reduce_blur,
    enhance_old_contrast,
    colorize_bw,
    fix_red_eyes
)

# NOUVELLES FONCTIONNALITÉS
from .object_removal import (
    ObjectRemover,
    object_remover,
    remove_object_by_mask,
    remove_object_by_rectangle,
    remove_object_by_polygon,
    smart_remove
)

from .clone_stamp import (
    CloneStamp,
    clone_stamp,
    set_clone_source,
    clone_area,
    clone_rectangle,
    clone_with_rotation,
    pattern_clone,
    heal_brush
)

# Liste de toutes les fonctionnalités disponibles
AVAILABLE_FEATURES = {
    # Retouches de base
    "Amélioration automatique": auto_enhance,
    "Amélioration des couleurs": enhance_colors,
    "Amélioration du contraste": enhance_contrast,
    "Amélioration de la netteté": enhance_sharpness,
    "Débruitage": denoise,
    "Débruitage bilatéral": denoise_bilateral,
    "Débruitage non-local": denoise_non_local,
    
    # Super-résolution
    "Super-résolution x2": upscale_x2,
    "Super-résolution x4": upscale_x4,
    
    # Arrière-plan
    "Suppression d'arrière-plan": remove_background,
    "Remplacement d'arrière-plan": replace_background,
    
    # Restauration
    "Restauration de photo": restore,
    "Correction des couleurs fanées": fix_faded_colors,
    "Suppression des rayures": remove_scratches,
    "Réduction du flou": reduce_blur,
    "Correction des yeux rouges": fix_red_eyes,
    
    # Optimisations spécifiques
    "Amélioration pour portrait": enhance_portrait,
    "Amélioration pour paysage": enhance_landscape,
    
    # NOUVELLES FONCTIONNALITÉS
    # Gommage d'objets
    "Gommage par rectangle": lambda img, x=0, y=0, w=100, h=100, r="inpainting": remove_object_by_rectangle(img, x, y, w, h, r),
    "Gommage intelligent": smart_remove,
    
    # Clone Stamp
    "Clone Stamp (simple)": lambda img, sx=0, sy=0, tx=0, ty=0, bs=20: clone_area(img, tx, ty, bs) if set_clone_source(sx, sy) else img,
    "Clone rectangle": clone_rectangle,
    "Clone avec rotation": clone_with_rotation,
    "Clone motif": pattern_clone,
    "Correction (Healing Brush)": heal_brush
}

# Liste des méthodes de remplacement pour le gommage
REPLACEMENT_METHODS = [
    "blur",      # Flou
    "color",     # Couleur unie
    "inpainting", # Reconstruction intelligente
    "context"    # Sensible au contexte
]

__all__ = [
    # Background
    "BackgroundRemover", "background_remover", "remove_background", 
    "replace_background", "get_segmentation_mask",
    
    # Enhancers
    "ImageEnhancer", "image_enhancer", "auto_enhance", "enhance_colors",
    "enhance_contrast", "enhance_sharpness", "denoise_bilateral",
    "enhance_details", "auto_white_balance", "enhance_portrait",
    "enhance_landscape",
    
    # Super Resolution
    "SuperResolutionModel", "sr_model_x2", "sr_model_x4", "upscale_x2",
    "upscale_x4", "upscale_to_size", "upscale",
    
    # Denoise
    "Denoiser", "denoiser", "denoise", "denoise_bilateral",
    "denoise_non_local", "denoise_wavelet", "denoise_gaussian",
    "denoise_median",
    
    # Restore
    "ImageRestorer", "image_restorer", "restore", "fix_faded_colors",
    "remove_scratches", "reduce_blur", "enhance_old_contrast",
    "colorize_bw", "fix_red_eyes",
    
    # Object Removal (NOUVEAU)
    "ObjectRemover", "object_remover", "remove_object_by_mask",
    "remove_object_by_rectangle", "remove_object_by_polygon", "smart_remove",
    
    # Clone Stamp (NOUVEAU)
    "CloneStamp", "clone_stamp", "set_clone_source", "clone_area",
    "clone_rectangle", "clone_with_rotation", "pattern_clone", "heal_brush",
    
    # Features
    "AVAILABLE_FEATURES", "REPLACEMENT_METHODS"
]
