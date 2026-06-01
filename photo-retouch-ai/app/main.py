# PhotoRetouch AI - Interface Principale
# Application de retouche photo locale avec IA - Sans censure

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import tempfile
from datetime import datetime

# Importer les modules de traitement
from processing import (
    auto_enhance,
    enhance_colors,
    enhance_contrast,
    enhance_sharpness,
    denoise,
    denoise_bilateral,
    denoise_non_local,
    upscale_x2,
    upscale_x4,
    remove_background,
    replace_background,
    restore,
    enhance_portrait,
    enhance_landscape,
    fix_red_eyes,
    AVAILABLE_FEATURES
)

from utils import (
    image_to_numpy,
    numpy_to_pil,
    save_image,
    get_output_dir,
    get_temp_dir,
    generate_output_filename,
    get_image_info,
    load_config,
    logger
)


# ============================================
# CONFIGURATION DE L'APPLICATION
# ============================================

# Charger la configuration
CONFIG = load_config("../config.yaml")

# Configuration de Streamlit
st.set_page_config(
    page_title="PhotoRetouch AI - Sans Censure",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 4px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stSelectbox, .stSlider, .stNumberInput {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #2d2d2d;
    }
    h1, h2, h3 {
        color: #4CAF50;
    }
    .success-box {
        background-color: #2e7d32;
        color: white;
        padding: 10px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #ff9800;
        color: white;
        padding: 10px;
        border-radius: 4px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def load_image(uploaded_file) -> np.ndarray:
    """Charge une image depuis un fichier uploadé."""
    try:
        if uploaded_file is not None:
            # Lire l'image
            image = Image.open(uploaded_file)
            return image_to_numpy(image)
    except Exception as e:
        st.error(f"Erreur de chargement de l'image: {e}")
    return None


def display_image(image: np.ndarray, title: str = "Image", width: int = None):
    """Affiche une image avec Streamlit."""
    if image is not None:
        # Convertir en PIL
        pil_image = numpy_to_pil(image)
        
        # Redimensionner si nécessaire
        if width is not None:
            w_percent = width / float(pil_image.size[0])
            h_size = int((float(pil_image.size[1]) * float(w_percent)))
            pil_image = pil_image.resize((width, h_size), Image.LANCZOS)
        
        st.image(pil_image, caption=title, use_column_width=False)


def save_result(image: np.ndarray, original_name: str = "image") -> str:
    """Sauvegarde le résultat et retourne le chemin."""
    try:
        output_dir = get_output_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{original_name}_retouched_{timestamp}.jpg"
        output_path = os.path.join(output_dir, filename)
        
        save_image(image, output_path, quality=95, format="JPEG")
        return output_path
    except Exception as e:
        st.error(f"Erreur de sauvegarde: {e}")
        return None


def apply_operation(image: np.ndarray, operation: str, **kwargs) -> np.ndarray:
    """Applique une opération de retouche à une image."""
    try:
        if operation == "Amélioration automatique":
            return auto_enhance(image, **kwargs)
        elif operation == "Amélioration des couleurs":
            return enhance_colors(image, **kwargs)
        elif operation == "Amélioration du contraste":
            return enhance_contrast(image, **kwargs)
        elif operation == "Amélioration de la netteté":
            return enhance_sharpness(image, **kwargs)
        elif operation == "Débruitage":
            return denoise(image, **kwargs)
        elif operation == "Débruitage bilatéral":
            return denoise_bilateral(image, **kwargs)
        elif operation == "Débruitage non-local":
            return denoise_non_local(image, **kwargs)
        elif operation == "Super-résolution x2":
            return upscale_x2(image)
        elif operation == "Super-résolution x4":
            return upscale_x4(image)
        elif operation == "Suppression d'arrière-plan":
            return remove_background(image, **kwargs)
        elif operation == "Restauration de photo":
            return restore(image, **kwargs)
        elif operation == "Correction des couleurs fanées":
            return restore(image, fix_colors=True, fix_scratches=False, fix_blur=False, fix_contrast=False)
        elif operation == "Suppression des rayures":
            return restore(image, fix_colors=False, fix_scratches=True, fix_blur=False, fix_contrast=False)
        elif operation == "Réduction du flou":
            return restore(image, fix_colors=False, fix_scratches=False, fix_blur=True, fix_contrast=False)
        elif operation == "Correction des yeux rouges":
            return fix_red_eyes(image)
        elif operation == "Amélioration pour portrait":
            return enhance_portrait(image)
        elif operation == "Amélioration pour paysage":
            return enhance_landscape(image)
        else:
            st.warning(f"Opération inconnue: {operation}")
            return image
    except Exception as e:
        st.error(f"Erreur lors de l'application de {operation}: {e}")
        logger.error(f"Erreur: {operation} - {e}")
        return image


# ============================================
# INTERFACE PRINCIPALE
# ============================================

def main():
    """Fonction principale de l'application."""
    
    # Titre
    st.title("🖼️ PhotoRetouch AI - Sans Censure")
    st.markdown("""
        **Application de retouche photo locale avec IA**
        
        ✅ **100% Local** - Aucune donnée n'est envoyée sur internet
        ✅ **Sans Censure** - Traite toutes les images sans restriction
        ✅ **Puissant** - Modèles d'IA pour des résultats professionnels
        ✅ **Simple** - Interface intuitive glisser-déposer
    """)
    
    # Barre latérale
    with st.sidebar:
        st.header("⚙️ Paramètres")
        
        # Sélection du mode
        mode = st.selectbox(
            "Mode",
            ["Retouche Simple", "Retouche Avancée", "Traitement par Lots"]
        )
        
        st.markdown("---")
        
        # Lien vers les outils avancés
        st.markdown("### 🎯 Outils Avancés")
        st.markdown("[Gommage et Clonage →](/🎯_Gommage_et_Clonage)")
        st.markdown("""
        - Gommage d'objets
        - Clone Stamp
        - Healing Brush
        """)
        
        st.markdown("---")
        
        # Informations
        st.subheader("ℹ️ Informations")
        st.markdown(f"""
        **Version:** {CONFIG.get('app', {}).get('version', '1.0.0')}
        
        **Dossier de sortie:** `{get_output_dir()}`
        
        **Modèles chargés:**
        - ✅ Suppression d'arrière-plan (MediaPipe)
        - ✅ Amélioration d'images
        - ✅ Débruitage
        - ⚠️ Super-résolution (nécessite modèles ONNX)
        """)
        
        st.markdown("---")
        
        # Liens utiles
        st.markdown("""
        **Besoin d'aide ?**
        Consultez le [README](../README.md) pour plus d'informations.
        """)
    
    # Contenu principal
    if mode == "Retouche Simple":
        simple_mode()
    elif mode == "Retouche Avancée":
        advanced_mode()
    elif mode == "Traitement par Lots":
        batch_mode()


def simple_mode():
    """Mode de retouche simple."""
    st.header("🎨 Retouche Simple")
    st.markdown("Glissez-déposez une image ou cliquez pour en sélectionner une.")
    
    # Upload d'image
    uploaded_file = st.file_uploader(
        "Sélectionnez une image",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        accept_multiple_files=False,
        key="simple_upload"
    )
    
    if uploaded_file is not None:
        # Charger l'image
        image = load_image(uploaded_file)
        
        if image is not None:
            # Afficher l'image originale
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Image Originale")
                display_image(image, "Originale", width=400)
                
                # Informations sur l'image
                info = get_image_info(image)
                st.markdown(f"""
                **Informations:**
                - Taille: {info['width']} x {info['height']} pixels
                - Mode: {info['mode']}
                - Taille: {info['size_mb']:.2f} MB
                """)
            
            with col2:
                st.subheader("Image Retouchée")
                
                # Sélection de l'opération
                operation = st.selectbox(
                    "Sélectionnez une opération",
                    list(AVAILABLE_FEATURES.keys())
                )
                
                # Paramètres spécifiques
                params = {}
                if operation in ["Débruitage", "Débruitage bilatéral", "Débruitage non-local"]:
                    params["strength"] = st.slider("Force", 0.1, 1.0, 0.85, 0.05)
                elif operation in ["Amélioration automatique", "Amélioration des couleurs", 
                                  "Amélioration du contraste", "Amélioration de la netteté"]:
                    params["strength"] = st.slider("Force", 0.1, 2.0, 1.0, 0.1)
                elif operation == "Suppression d'arrière-plan":
                    params["threshold"] = st.slider("Seuil", 0.1, 0.9, 0.7, 0.05)
                    params["background_color"] = st.color_picker("Couleur d'arrière-plan", "#000000")
                    # Convertir la couleur hex en BGR
                    hex_color = params["background_color"].lstrip('#')
                    params["background_color"] = tuple(
                        int(hex_color[i:i+2], 16) for i in (4, 2, 0)
                    )
                elif operation == "Restauration de photo":
                    params["strength"] = st.slider("Force", 0.1, 1.0, 1.0, 0.1)
                
                # Bouton d'application
                if st.button("Appliquer", key="apply_simple"):
                    with st.spinner("Traitement en cours..."):
                        result = apply_operation(image, operation, **params)
                        
                        if result is not None:
                            display_image(result, f"Résultat: {operation}", width=400)
                            
                            # Sauvegarder le résultat
                            output_path = save_result(result, uploaded_file.name)
                            if output_path:
                                st.success(f"✅ Image sauvegardée: {os.path.basename(output_path)}")
                                
                                # Bouton de téléchargement
                                st.download_button(
                                    label="Télécharger",
                                    data=open(output_path, "rb").read(),
                                    file_name=os.path.basename(output_path),
                                    mime="image/jpeg"
                                )


def advanced_mode():
    """Mode de retouche avancée."""
    st.header("🔬 Retouche Avancée")
    st.markdown("Appliquez plusieurs opérations successives pour des résultats optimaux.")
    
    # Upload d'image
    uploaded_file = st.file_uploader(
        "Sélectionnez une image",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        accept_multiple_files=False,
        key="advanced_upload"
    )
    
    if uploaded_file is not None:
        # Charger l'image
        image = load_image(uploaded_file)
        
        if image is not None:
            # Afficher l'image originale
            st.subheader("Image Originale")
            display_image(image, "Originale", width=600)
            
            st.markdown("---")
            
            # Sélection des opérations
            st.subheader("📋 Pipeline de Traitement")
            
            # Liste des opérations disponibles
            available_ops = list(AVAILABLE_FEATURES.keys())
            
            # Sélection des opérations à appliquer
            selected_ops = st.multiselect(
                "Sélectionnez les opérations à appliquer (dans l'ordre)",
                available_ops,
                default=["Amélioration automatique"]
            )
            
            # Paramètres pour chaque opération
            st.markdown("### Paramètres")
            operation_params = {}
            
            for op in selected_ops:
                with st.expander(f"⚙️ {op}"):
                    params = {}
                    if op in ["Débruitage", "Débruitage bilatéral", "Débruitage non-local"]:
                        params["strength"] = st.slider(f"Force ({op})", 0.1, 1.0, 0.85, 0.05, key=f"{op}_strength")
                    elif op in ["Amélioration automatique", "Amélioration des couleurs", 
                               "Amélioration du contraste", "Amélioration de la netteté"]:
                        params["strength"] = st.slider(f"Force ({op})", 0.1, 2.0, 1.0, 0.1, key=f"{op}_strength")
                    elif op == "Suppression d'arrière-plan":
                        params["threshold"] = st.slider(f"Seuil ({op})", 0.1, 0.9, 0.7, 0.05, key=f"{op}_threshold")
                        params["background_color"] = st.color_picker(f"Couleur ({op})", "#000000", key=f"{op}_color")
                        hex_color = params["background_color"].lstrip('#')
                        params["background_color"] = tuple(
                            int(hex_color[i:i+2], 16) for i in (4, 2, 0)
                        )
                    elif op == "Restauration de photo":
                        params["strength"] = st.slider(f"Force ({op})", 0.1, 1.0, 1.0, 0.1, key=f"{op}_strength")
                    
                    operation_params[op] = params
            
            # Bouton d'application
            if st.button("Appliquer le Pipeline", key="apply_advanced"):
                with st.spinner("Traitement en cours..."):
                    result = image.copy()
                    
                    # Appliquer chaque opération dans l'ordre
                    for op in selected_ops:
                        params = operation_params.get(op, {})
                        result = apply_operation(result, op, **params)
                    
                    if result is not None:
                        st.subheader("Résultat Final")
                        display_image(result, "Résultat", width=600)
                        
                        # Sauvegarder le résultat
                        output_path = save_result(result, uploaded_file.name)
                        if output_path:
                            st.success(f"✅ Image sauvegardée: {os.path.basename(output_path)}")
                            
                            # Bouton de téléchargement
                            st.download_button(
                                label="Télécharger",
                                data=open(output_path, "rb").read(),
                                file_name=os.path.basename(output_path),
                                mime="image/jpeg"
                            )


def batch_mode():
    """Mode de traitement par lots."""
    st.header("📦 Traitement par Lots")
    st.markdown("Traitez plusieurs images avec les mêmes paramètres.")
    
    # Upload de plusieurs images
    uploaded_files = st.file_uploader(
        "Sélectionnez plusieurs images",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        accept_multiple_files=True,
        key="batch_upload"
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} images sélectionnées**")
        
        # Sélection de l'opération
        operation = st.selectbox(
            "Sélectionnez une opération",
            list(AVAILABLE_FEATURES.keys())
        )
        
        # Paramètres
        params = {}
        if operation in ["Débruitage", "Débruitage bilatéral", "Débruitage non-local"]:
            params["strength"] = st.slider("Force", 0.1, 1.0, 0.85, 0.05)
        elif operation in ["Amélioration automatique", "Amélioration des couleurs", 
                          "Amélioration du contraste", "Amélioration de la netteté"]:
            params["strength"] = st.slider("Force", 0.1, 2.0, 1.0, 0.1)
        elif operation == "Suppression d'arrière-plan":
            params["threshold"] = st.slider("Seuil", 0.1, 0.9, 0.7, 0.05)
            params["background_color"] = st.color_picker("Couleur d'arrière-plan", "#000000")
            hex_color = params["background_color"].lstrip('#')
            params["background_color"] = tuple(
                int(hex_color[i:i+2], 16) for i in (4, 2, 0)
            )
        elif operation == "Restauration de photo":
            params["strength"] = st.slider("Force", 0.1, 1.0, 1.0, 0.1)
        
        # Bouton de traitement
        if st.button("Traiter toutes les images", key="process_batch"):
            with st.spinner("Traitement en cours..."):
                results = []
                
                for uploaded_file in uploaded_files:
                    image = load_image(uploaded_file)
                    if image is not None:
                        result = apply_operation(image, operation, **params)
                        if result is not None:
                            output_path = save_result(result, uploaded_file.name)
                            results.append({
                                "original": uploaded_file.name,
                                "result": output_path
                            })
                
                if results:
                    st.success(f"✅ {len(results)} images traitées avec succès!")
                    
                    # Afficher les résultats
                    for res in results:
                        st.markdown(f"**{res['original']}** → {os.path.basename(res['result'])}")
                    
                    # Bouton de téléchargement de toutes les images
                    st.markdown("---")
                    st.subheader("Téléchargement")
                    
                    # Créer une archive ZIP (optionnel)
                    zip_path = os.path.join(get_output_dir(), "results.zip")
                    
                    # Pour simplifier, on propose de télécharger chaque image individuellement
                    for res in results:
                        with open(res['result'], "rb") as f:
                            st.download_button(
                                label=f"Télécharger {os.path.basename(res['result'])}",
                                data=f.read(),
                                file_name=os.path.basename(res['result']),
                                mime="image/jpeg",
                                key=f"dl_{res['result']}"
                            )


# ============================================
# FONCTIONS DE DÉMARRAGE
# ============================================

def download_models_page():
    """Page pour télécharger les modèles ONNX."""
    st.title("📥 Téléchargement des Modèles")
    st.markdown("""
        Certains modèles d'IA nécessitent des fichiers ONNX pour fonctionner.
        Cette page vous permet de les télécharger automatiquement.
    """)
    
    st.warning("⚠️ Cette fonctionnalité nécessite une connexion internet pour le téléchargement initial.")
    
    # Liste des modèles disponibles
    models_info = {
        "esrgan_tiny.onnx": {
            "name": "Super-Résolution (ESRGAN Tiny)",
            "size": "~5 MB",
            "description": "Modèle léger pour l'agrandissement d'images x2 ou x4"
        },
        "denoise.onnx": {
            "name": "Débruitage",
            "size": "~3 MB",
            "description": "Modèle pour la suppression du bruit dans les images"
        },
        "restore.onnx": {
            "name": "Restauration",
            "size": "~8 MB",
            "description": "Modèle pour la restauration de vieilles photos"
        }
    }
    
    st.subheader("Modèles Disponibles")
    for model_file, info in models_info.items():
        with st.expander(f"📦 {info['name']}"):
            st.markdown(f"""
            **Description:** {info['description']}
            **Taille:** {info['size']}
            **Fichier:** `{model_file}`
            """)
            
            # Vérifier si le modèle existe déjà
            model_path = os.path.join(get_models_dir(), model_file)
            if os.path.exists(model_path):
                st.success("✅ Modèle déjà présent")
            else:
                st.warning("❌ Modèle non trouvé")
                if st.button(f"Télécharger {info['name']}", key=f"dl_{model_file}"):
                    st.info("Fonctionnalité de téléchargement à implémenter")


# ============================================
# POINT D'ENTRÉE
# ============================================

if __name__ == "__main__":
    # Vérifier si on est en mode téléchargement
    if "download_models" in st.experimental_get_query_params():
        download_models_page()
    else:
        main()
