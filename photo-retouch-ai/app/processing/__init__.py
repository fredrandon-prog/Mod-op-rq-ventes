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

# Liste de toutes les fonctionnalités disponibles
AVAILABLE_FEATURES = {
    "Amélioration automatique": auto_enhance,
    "Amélioration des couleurs": enhance_colors,
    "Amélioration du contraste": enhance_contrast,
    "Amélioration de la netteté": enhance_sharpness,
    "Débruitage": denoise,
    "Débruitage bilatéral": denoise_bilateral,
    "Débruitage non-local": denoise_non_local,
    "Super-résolution x2": upscale_x2,
    "Super-résolution x4": upscale_x4,
    "Suppression d'arrière-plan": remove_background,
    "Remplacement d'arrière-plan": replace_background,
    "Restauration de photo": restore,
    "Correction des couleurs fanées": fix_faded_colors,
    "Suppression des rayures": remove_scratches,
    "Réduction du flou": reduce_blur,
    "Correction des yeux rouges": fix_red_eyes,
    "Amélioration pour portrait": enhance_portrait,
    "Amélioration pour paysage": enhance_landscape,
}

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
    
    # Features
    "AVAILABLE_FEATURES"
]
