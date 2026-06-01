# PhotoRetouch AI - Gommage et Clonage
# Page dédiée aux outils de gommage d'objets et de clonage

import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw
import os
from datetime import datetime

# Importer les modules de traitement
from processing.object_removal import (
    remove_object_by_rectangle,
    remove_object_by_mask,
    smart_remove,
    REPLACEMENT_METHODS
)
from processing.clone_stamp import (
    clone_area,
    clone_rectangle,
    set_clone_source,
    clone_with_rotation,
    pattern_clone,
    heal_brush
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
# CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Gommage et Clonage - PhotoRetouch AI",
    page_icon="🎯",
    layout="wide"
)

# Style personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #2196F3;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 4px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #0b7dda;
    }
    h1, h2, h3 {
        color: #2196F3;
    }
    .success-box {
        background-color: #2e7d32;
        color: white;
        padding: 10px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #1976d2;
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
            image = Image.open(uploaded_file)
            return image_to_numpy(image)
    except Exception as e:
        st.error(f"Erreur de chargement de l'image: {e}")
    return None


def display_image(image: np.ndarray, title: str = "Image", width: int = None):
    """Affiche une image avec Streamlit."""
    if image is not None:
        pil_image = numpy_to_pil(image)
        
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
        filename = f"{original_name}_edited_{timestamp}.jpg"
        output_path = os.path.join(output_dir, filename)
        
        save_image(image, output_path, quality=95, format="JPEG")
        return output_path
    except Exception as e:
        st.error(f"Erreur de sauvegarde: {e}")
        return None


def create_rectangle_mask(image_shape: Tuple[int, int], x: int, y: int, w: int, h: int) -> np.ndarray:
    """Crée un masque rectangulaire."""
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    return mask


# ============================================
# PAGE PRINCIPALE
# ============================================

def main():
    """Fonction principale de la page."""
    
    st.title("🎯 Gommage et Clonage")
    st.markdown("""
        **Outils avancés pour modifier vos images**
        
        - 🗑️ **Gommage d'objets** : Supprimez des éléments indésirables
        - 🖌️ **Clone Stamp** : Copiez et collez des parties de l'image
        - 🎨 **Healing Brush** : Corrigez les imperfections
    """)
    
    # Barre latérale
    with st.sidebar:
        st.header("⚙️ Outils")
        
        tool = st.selectbox(
            "Sélectionnez un outil",
            [
                "Gommage par Rectangle",
                "Gommage Intelligent",
                "Clone Stamp",
                "Clone Rectangle",
                "Healing Brush"
            ]
        )
        
        st.markdown("---")
        
        # Paramètres globaux
        st.subheader("ℹ️ Aide")
        st.markdown("""
        **Gommage** : Supprimez des objets ou zones indésirables
        
        **Clone Stamp** : Copiez une partie de l'image et collez-la ailleurs
        
        **Healing Brush** : Corrigez les imperfections en mélangeant avec les pixels environnants
        """)
    
    # Contenu principal
    if tool == "Gommage par Rectangle":
        gommage_rectangle_tool()
    elif tool == "Gommage Intelligent":
        gommage_intelligent_tool()
    elif tool == "Clone Stamp":
        clone_stamp_tool()
    elif tool == "Clone Rectangle":
        clone_rectangle_tool()
    elif tool == "Healing Brush":
        healing_brush_tool()


def gommage_rectangle_tool():
    """Outil de gommage par rectangle."""
    st.header("🗑️ Gommage par Rectangle")
    st.markdown("Sélectionnez une zone rectangulaire à supprimer de l'image.")
    
    # Upload d'image
    uploaded_file = st.file_uploader(
        "Sélectionnez une image",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        accept_multiple_files=False,
        key="gommage_rect_upload"
    )
    
    if uploaded_file is not None:
        image = load_image(uploaded_file)
        
        if image is not None:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Image Originale")
                display_image(image, "Originale", width=500)
                
                # Informations
                info = get_image_info(image)
                st.markdown(f"""
                **Informations:**
                - Taille: {info['width']} x {info['height']} pixels
                - Mode: {info['mode']}
                """)
            
            with col2:
                st.subheader("Paramètres de Gommage")
                
                # Paramètres du rectangle
                h, w = image.shape[:2]
                
                x = st.slider("Position X", 0, w - 1, w // 4, key="gommage_x")
                y = st.slider("Position Y", 0, h - 1, h // 4, key="gommage_y")
                
                max_width = w - x
                max_height = h - y
                
                width = st.slider("Largeur", 10, max_width, min(200, max_width), key="gommage_width")
                height = st.slider("Hauteur", 10, max_height, min(200, max_height), key="gommage_height")
                
                # Méthode de remplacement
                replacement = st.selectbox(
                    "Méthode de remplacement",
                    ["inpainting", "blur", "color", "context"],
                    index=0,
                    key="gommage_replacement"
                )
                
                if replacement == "color":
                    replacement_color = st.color_picker("Couleur de remplacement", "#808080", key="gommage_color")
                    hex_color = replacement_color.lstrip('#')
                    replacement_color_bgr = tuple(
                        int(hex_color[i:i+2], 16) for i in (4, 2, 0)
                    )
                else:
                    replacement_color_bgr = (128, 128, 128)
                
                # Paramètres supplémentaires
                if replacement == "blur":
                    blur_radius = st.slider("Rayon du flou", 5, 50, 25, key="gommage_blur")
                elif replacement == "inpainting":
                    inpainting_radius = st.slider("Rayon d'inpainting", 5, 30, 10, key="gommage_inpaint")
                else:
                    blur_radius = 25
                    inpainting_radius = 10
                
                # Bouton d'application
                if st.button("Appliquer le Gommage", key="apply_gommage_rect"):
                    with st.spinner("Traitement en cours..."):
                        result = remove_object_by_rectangle(
                            image, x, y, width, height, replacement
                        )
                        
                        if result is not None:
                            st.subheader("Résultat")
                            display_image(result, "Après gommage", width=500)
                            
                            # Sauvegarder
                            output_path = save_result(result, uploaded_file.name)
                            if output_path:
                                st.success(f"✅ Image sauvegardée: {os.path.basename(output_path)}")
                                
                                # Téléchargement
                                with open(output_path, "rb") as f:
                                    st.download_button(
                                        label="Télécharger",
                                        data=f.read(),
                                        file_name=os.path.basename(output_path),
                                        mime="image/jpeg",
                                        key="dl_gommage_rect"
                                    )


def gommage_intelligent_tool():
    """Outil de gommage intelligent."""
    st.header("🤖 Gommage Intelligent")
    st.markdown("Supprimez automatiquement les objets détectés (personnes, animaux, etc.).")
    
    # Upload d'image
    uploaded_file = st.file_uploader(
        "Sélectionnez une image",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        accept_multiple_files=False,
        key="gommage_smart_upload"
    )
    
    if uploaded_file is not None:
        image = load_image(uploaded_file)
        
        if image is not None:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Image Originale")
                display_image(image, "Originale", width=500)
            
            with col2:
                st.subheader("Paramètres")
                
                method = st.selectbox(
                    "Méthode de détection",
                    ["segmentation", "contours"],
                    index=0,
                    key="smart_method"
                )
                
                threshold = st.slider("Seuil de détection", 0.1, 0.9, 0.7, 0.05, key="smart_threshold")
                
                remove_subject = st.radio(
                    "Supprimer",
                    ["Le sujet principal", "L'arrière-plan"],
                    index=0,
                    key="smart_remove"
                )
                
                replacement = st.selectbox(
                    "Méthode de remplacement",
                    ["inpainting", "blur", "color"],
                    index=0,
                    key="smart_replacement"
                )
                
                # Bouton d'application
                if st.button("Appliquer le Gommage Intelligent", key="apply_smart_gommage"):
                    with st.spinner("Détection et traitement en cours..."):
                        remove_bg = (remove_subject == "L'arrière-plan")
                        
                        result = smart_remove(
                            image,
                            method=method,
                            threshold=threshold,
                            remove_background=remove_bg
                        )
                        
                        if result is not None:
                            st.subheader("Résultat")
                            display_image(result, "Après gommage intelligent", width=500)
                            
                            # Sauvegarder
                            output_path = save_result(result, uploaded_file.name)
                            if output_path:
                                st.success(f"✅ Image sauvegardée: {os.path.basename(output_path)}")
                                
                                # Téléchargement
                                with open(output_path, "rb") as f:
                                    st.download_button(
                                        label="Télécharger",
                                        data=f.read(),
                                        file_name=os.path.basename(output_path),
                                        mime="image/jpeg",
                                        key="dl_smart_gommage"
                                    )


def clone_stamp_tool():
    """Outil Clone Stamp."""
    st.header("🖌️ Clone Stamp")
    st.markdown("Copiez une partie de l'image et collez-la ailleurs.")
    
    # Upload d'image
    uploaded_file = st.file_uploader(
        "Sélectionnez une image",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        accept_multiple_files=False,
        key="clone_stamp_upload"
    )
    
    if uploaded_file is not None:
        image = load_image(uploaded_file)
        
        if image is not None:
            st.subheader("Image Originale")
            display_image(image, "Originale", width=700)
            
            st.markdown("---")
            st.subheader("⚙️ Paramètres du Clone Stamp")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Point Source (d'où copier)")
                h, w = image.shape[:2]
                source_x = st.slider("Source X", 0, w - 1, w // 4, key="clone_source_x")
                source_y = st.slider("Source Y", 0, h - 1, h // 4, key="clone_source_y")
                
                if st.button("Définir comme source", key="set_source"):
                    set_clone_source(source_x, source_y)
                    st.success(f"Point source défini: ({source_x}, {source_y})")
            
            with col2:
                st.markdown("### Point Cible (où coller)")
                target_x = st.slider("Cible X", 0, w - 1, 3 * w // 4, key="clone_target_x")
                target_y = st.slider("Cible Y", 0, h - 1, 3 * h // 4, key="clone_target_y")
                
                brush_size = st.slider("Taille du pinceau", 5, 100, 20, key="clone_brush")
                opacity = st.slider("Opacité", 0.1, 1.0, 1.0, 0.1, key="clone_opacity")
            
            # Bouton d'application
            if st.button("Appliquer le Clone Stamp", key="apply_clone_stamp"):
                with st.spinner("Clonage en cours..."):
                    result = clone_area(
                        image,
                        target_x,
                        target_y,
                        brush_size=brush_size,
                        opacity=opacity
                    )
                    
                    if result is not None:
                        st.subheader("Résultat")
                        display_image(result, "Après clonage", width=700)
                        
                        # Sauvegarder
                        output_path = save_result(result, uploaded_file.name)
                        if output_path:
                            st.success(f"✅ Image sauvegardée: {os.path.basename(output_path)}")
                            
                            # Téléchargement
                            with open(output_path, "rb") as f:
                                st.download_button(
                                    label="Télécharger",
                                    data=f.read(),
                                    file_name=os.path.basename(output_path),
                                    mime="image/jpeg",
                                    key="dl_clone_stamp"
                                )


def clone_rectangle_tool():
    """Outil de clonage de rectangle."""
    st.header("📦 Clone Rectangle")
    st.markdown("Copiez un rectangle et collez-le à un autre endroit.")
    
    # Upload d'image
    uploaded_file = st.file_uploader(
        "Sélectionnez une image",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        accept_multiple_files=False,
        key="clone_rect_upload"
    )
    
    if uploaded_file is not None:
        image = load_image(uploaded_file)
        
        if image is not None:
            st.subheader("Image Originale")
            display_image(image, "Originale", width=700)
            
            st.markdown("---")
            
            h, w = image.shape[:2]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Rectangle Source")
                src_x = st.slider("Source X", 0, w - 1, w // 4, key="rect_src_x")
                src_y = st.slider("Source Y", 0, h - 1, h // 4, key="rect_src_y")
                src_w = st.slider("Source Largeur", 10, w - src_x, min(200, w - src_x), key="rect_src_w")
                src_h = st.slider("Source Hauteur", 10, h - src_y, min(200, h - src_y), key="rect_src_h")
            
            with col2:
                st.markdown("### Rectangle Cible")
                tgt_x = st.slider("Cible X", 0, w - 1, w // 2, key="rect_tgt_x")
                tgt_y = st.slider("Cible Y", 0, h - 1, h // 2, key="rect_tgt_y")
                tgt_w = st.slider("Cible Largeur", 10, w - tgt_x, min(200, w - tgt_x), key="rect_tgt_w")
                tgt_h = st.slider("Cible Hauteur", 10, h - tgt_y, min(200, h - tgt_y), key="rect_tgt_h")
                
                opacity = st.slider("Opacité", 0.1, 1.0, 1.0, 0.1, key="rect_opacity")
            
            # Bouton d'application
            if st.button("Appliquer le Clone Rectangle", key="apply_clone_rect"):
                with st.spinner("Clonage en cours..."):
                    result = clone_rectangle(
                        image,
                        source_rect=(src_x, src_y, src_w, src_h),
                        target_rect=(tgt_x, tgt_y, tgt_w, tgt_h),
                        opacity=opacity
                    )
                    
                    if result is not None:
                        st.subheader("Résultat")
                        display_image(result, "Après clonage", width=700)
                        
                        # Sauvegarder
                        output_path = save_result(result, uploaded_file.name)
                        if output_path:
                            st.success(f"✅ Image sauvegardée: {os.path.basename(output_path)}")
                            
                            # Téléchargement
                            with open(output_path, "rb") as f:
                                st.download_button(
                                    label="Télécharger",
                                    data=f.read(),
                                    file_name=os.path.basename(output_path),
                                    mime="image/jpeg",
                                    key="dl_clone_rect"
                                )


def healing_brush_tool():
    """Outil Healing Brush."""
    st.header("🎨 Healing Brush")
    st.markdown("Corrigez les imperfections en mélangeant avec les pixels environnants.")
    
    # Upload d'image
    uploaded_file = st.file_uploader(
        "Sélectionnez une image",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        accept_multiple_files=False,
        key="healing_upload"
    )
    
    if uploaded_file is not None:
        image = load_image(uploaded_file)
        
        if image is not None:
            st.subheader("Image Originale")
            display_image(image, "Originale", width=700)
            
            st.markdown("---")
            st.subheader("⚙️ Paramètres du Healing Brush")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Point Source (échantillon)")
                h, w = image.shape[:2]
                source_x = st.slider("Source X", 0, w - 1, w // 4, key="heal_source_x")
                source_y = st.slider("Source Y", 0, h - 1, h // 4, key="heal_source_y")
                
                if st.button("Définir comme source", key="set_heal_source"):
                    set_clone_source(source_x, source_y)
                    st.success(f"Point source défini: ({source_x}, {source_y})")
            
            with col2:
                st.markdown("### Point Cible (à corriger)")
                target_x = st.slider("Cible X", 0, w - 1, 3 * w // 4, key="heal_target_x")
                target_y = st.slider("Cible Y", 0, h - 1, 3 * h // 4, key="heal_target_y")
                
                brush_size = st.slider("Taille du pinceau", 5, 100, 20, key="heal_brush")
                sample_radius = st.slider("Rayon d'échantillonnage", 1, 50, 5, key="heal_sample")
            
            # Bouton d'application
            if st.button("Appliquer le Healing Brush", key="apply_healing"):
                with st.spinner("Correction en cours..."):
                    result = heal_brush(
                        image,
                        target_x,
                        target_y,
                        brush_size=brush_size,
                        sample_radius=sample_radius
                    )
                    
                    if result is not None:
                        st.subheader("Résultat")
                        display_image(result, "Après correction", width=700)
                        
                        # Sauvegarder
                        output_path = save_result(result, uploaded_file.name)
                        if output_path:
                            st.success(f"✅ Image sauvegardée: {os.path.basename(output_path)}")
                            
                            # Téléchargement
                            with open(output_path, "rb") as f:
                                st.download_button(
                                    label="Télécharger",
                                    data=f.read(),
                                    file_name=os.path.basename(output_path),
                                    mime="image/jpeg",
                                    key="dl_healing"
                                )


# ============================================
# POINT D'ENTRÉE
# ============================================

if __name__ == "__main__":
    main()
