#!/usr/bin/env python3
# PhotoRetouch AI - Point d'entrée pour l'application mobile
# Utilise Kivy pour une interface tactile adaptée aux smartphones

import sys
import os

# Ajouter le chemin du package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Vérifier si on est sur Android
try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    ANDROID = True
except ImportError:
    ANDROID = False

# Importer Kivy
try:
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.image import Image, AsyncImage
    from kivy.uix.filechooser import FileChooserListView
    from kivy.uix.popup import Popup
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.slider import Slider
    from kivy.uix.textinput import TextInput
    from kivy.core.window import Window
    from kivy.core.image import Image as CoreImage
    from kivy.graphics import Color, Rectangle
    from kivy.properties import ObjectProperty, StringProperty, NumericProperty
    from kivy.clock import Clock
    from kivy.lang import Builder
    
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

# Importer les modules de traitement
from app.processing import (
    remove_object_by_rectangle,
    smart_remove,
    clone_area,
    clone_rectangle,
    set_clone_source,
    enhance_colors,
    enhance_contrast,
    enhance_sharpness,
    auto_enhance,
    remove_background,
    denoise,
    upscale_x2,
    restore
)

from app.utils import (
    image_to_numpy,
    numpy_to_pil,
    save_image,
    load_config
)

import cv2
import numpy as np
from PIL import Image as PILImage
import io


# ============================================
# CONFIGURATION
# ============================================

# Charger la configuration
CONFIG = load_config()

# Couleurs
PRIMARY_COLOR = (0.13, 0.59, 0.95, 1)  # #2196F3
BACKGROUND_COLOR = (0.12, 0.12, 0.12, 1)  # #1E1E1E
TEXT_COLOR = (1, 1, 1, 1)  # Blanc
SUCCESS_COLOR = (0.18, 0.5, 0.2, 1)  # Vert
ERROR_COLOR = (0.95, 0.26, 0.21, 1)  # Rouge

# Taille de l'interface pour mobile
Window.size = (360, 640)  # Taille typique pour mobile
Window.clearcolor = BACKGROUND_COLOR


# ============================================
# FONCTIONS UTILITAIRES POUR MOBILE
# ============================================

def load_image_from_path(path: str) -> np.ndarray:
    """Charge une image depuis un chemin."""
    try:
        image = PILImage.open(path)
        return image_to_numpy(image)
    except Exception as e:
        print(f"Erreur de chargement: {e}")
        return None


def save_image_to_path(image: np.ndarray, path: str) -> bool:
    """Sauvegarde une image vers un chemin."""
    try:
        pil_image = numpy_to_pil(image)
        pil_image.save(path, quality=95, format="JPEG")
        return True
    except Exception as e:
        print(f"Erreur de sauvegarde: {e}")
        return False


def get_output_path(filename: str = None) -> str:
    """Retourne un chemin de sortie."""
    if ANDROID:
        base_path = primary_external_storage_path()
        output_dir = os.path.join(base_path, "PhotoRetouchAI")
    else:
        output_dir = os.path.join(os.path.expanduser("~"), "PhotoRetouchAI")
    
    os.makedirs(output_dir, exist_ok=True)
    
    if filename:
        return os.path.join(output_dir, filename)
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(output_dir, f"photo_retouched_{timestamp}.jpg")


def numpy_to_kivy_texture(image: np.ndarray):
    """Convertit une image numpy en texture Kivy."""
    if image is None:
        return None
    
    # Convertir en RGB si nécessaire
    if image.ndim == 3 and image.shape[2] == 3:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image
    
    # Convertir en bytes
    buf = cv2.imencode('.png', image_rgb)[1].tobytes()
    
    # Créer une texture Kivy
    from kivy.core.image import Image
    texture = Image(io.BytesIO(buf), ext='png').texture
    
    return texture


# ============================================
# INTERFACE KIVY
# ============================================

# Langage KV pour l'interface
KV_LANGUAGE = '''
<MainScreen>:
    manager: screen_manager
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        Label:
            text: 'PhotoRetouch AI'
            font_size: 24
            color: 0.13, 0.59, 0.95, 1
            size_hint_y: None
            height: 50
        
        Label:
            text: 'Application de retouche photo locale avec IA'
            font_size: 14
            color: 0.7, 0.7, 0.7, 1
            size_hint_y: None
            height: 30
        
        Button:
            text: '📷 Choisir une Photo'
            font_size: 16
            background_color: 0.13, 0.59, 0.95, 1
            color: 1, 1, 1, 1
            size_hint_y: None
            height: 50
            on_press: root.open_file_chooser()
        
        Button:
            text: '📸 Prendre une Photo'
            font_size: 16
            background_color: 0.13, 0.59, 0.95, 1
            color: 1, 1, 1, 1
            size_hint_y: None
            height: 50
            on_press: root.take_photo()
        
        Button:
            text: '⚙️ Outils Avancés'
            font_size: 16
            background_color: 0.2, 0.2, 0.2, 1
            color: 1, 1, 1, 1
            size_hint_y: None
            height: 50
            on_press: root.go_to_tools()
        
        Label:
            text: '✅ 100% Local | 🔒 Sans Censure'
            font_size: 12
            color: 0.5, 0.8, 0.5, 1
            size_hint_y: None
            height: 30

<FileChooserScreen>:
    file_chooser: file_chooser
    
    BoxLayout:
        orientation: 'vertical'
        
        FileChooserListView:
            id: file_chooser
            filters: ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp']
            on_selection: root.selected(file_chooser.selection)
        
        BoxLayout:
            size_hint_y: None
            height: 50
            
            Button:
                text: 'Annuler'
                on_press: root.go_back()

<EditScreen>:
    image_widget: image_widget
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        # Zone de l'image
        BoxLayout:
            size_hint_y: 2
            
            Image:
                id: image_widget
                allow_stretch: True
                keep_ratio: True
        
        # Boutons d'action
        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 10
            
            Button:
                text: '✨ Amélioration Auto'
                on_press: root.apply_auto_enhance()
            
            Button:
                text: '🗑️ Gommer'
                on_press: root.go_to_removal()
            
            Button:
                text: '🖌️ Cloner'
                on_press: root.go_to_clone()
        
        # Boutons de navigation
        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 10
            
            Button:
                text: '← Retour'
                on_press: root.go_back()
            
            Button:
                text: '💾 Sauvegarder'
                on_press: root.save_image()

<RemovalScreen>:
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        Label:
            text: 'Gommage d\'Objets'
            font_size: 20
            color: 0.13, 0.59, 0.95, 1
            size_hint_y: None
            height: 40
        
        # Zone de l'image avec sélection
        RelativeLayout:
            size_hint_y: 2
            
            Image:
                id: image_widget
                allow_stretch: True
                keep_ratio: True
                
            # Rectangle de sélection (sera ajouté dynamiquement)
        
        # Contrôles de sélection
        BoxLayout:
            size_hint_y: None
            height: 150
            orientation: 'vertical'
            spacing: 5
            
            Label:
                text: 'Sélectionnez la zone à supprimer:'
                color: 0.8, 0.8, 0.8, 1
            
            BoxLayout:
                size_hint_y: None
                height: 40
                spacing: 5
                
                Label:
                    text: 'X:'
                    size_hint_x: None
                    width: 40
                
                Slider:
                    id: x_slider
                    min: 0
                    max: 100
                    value: 25
                
                Label:
                    text: str(int(x_slider.value))
                    size_hint_x: None
                    width: 40
            
            BoxLayout:
                size_hint_y: None
                height: 40
                spacing: 5
                
                Label:
                    text: 'Y:'
                    size_hint_x: None
                    width: 40
                
                Slider:
                    id: y_slider
                    min: 0
                    max: 100
                    value: 25
                
                Label:
                    text: str(int(y_slider.value))
                    size_hint_x: None
                    width: 40
            
            BoxLayout:
                size_hint_y: None
                height: 40
                spacing: 5
                
                Label:
                    text: 'Largeur:'
                    size_hint_x: None
                    width: 70
                
                Slider:
                    id: width_slider
                    min: 10
                    max: 100
                    value: 50
                
                Label:
                    text: str(int(width_slider.value))
                    size_hint_x: None
                    width: 40
            
            BoxLayout:
                size_hint_y: None
                height: 40
                spacing: 5
                
                Label:
                    text: 'Hauteur:'
                    size_hint_x: None
                    width: 70
                
                Slider:
                    id: height_slider
                    min: 10
                    max: 100
                    value: 50
                
                Label:
                    text: str(int(height_slider.value))
                    size_hint_x: None
                    width: 40
        
        # Méthode de remplacement
        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 10
            
            Label:
                text: 'Méthode:'
                size_hint_x: None
                width: 80
            
            Button:
                text: 'Inpainting'
                background_color: 0.13, 0.59, 0.95, 1 if root.replacement == 'inpainting' else 0.3, 0.3, 0.3, 1
                on_press: root.set_replacement('inpainting')
            
            Button:
                text: 'Flou'
                background_color: 0.13, 0.59, 0.95, 1 if root.replacement == 'blur' else 0.3, 0.3, 0.3, 1
                on_press: root.set_replacement('blur')
            
            Button:
                text: 'Couleur'
                background_color: 0.13, 0.59, 0.95, 1 if root.replacement == 'color' else 0.3, 0.3, 0.3, 1
                on_press: root.set_replacement('color')
        
        # Boutons d'action
        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 10
            
            Button:
                text: 'Appliquer'
                background_color: 0.18, 0.5, 0.2, 1
                on_press: root.apply_removal()
            
            Button:
                text: 'Annuler'
                background_color: 0.8, 0.2, 0.2, 1
                on_press: root.go_back()

<CloneScreen>:
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        Label:
            text: 'Clone Stamp'
            font_size: 20
            color: 0.13, 0.59, 0.95, 1
            size_hint_y: None
            height: 40
        
        Label:
            text: '1. Sélectionnez la zone source (d\'où copier)'
            color: 0.8, 0.8, 0.8, 1
            size_hint_y: None
            height: 30
        
        # Zone de sélection source
        BoxLayout:
            size_hint_y: None
            height: 100
            spacing: 10
            
            Button:
                text: 'Définir Source'
                on_press: root.set_source_mode()
            
            Button:
                text: 'Définir Cible'
                on_press: root.set_target_mode()
        
        # Zone de l'image
        RelativeLayout:
            size_hint_y: 2
            
            Image:
                id: image_widget
                allow_stretch: True
                keep_ratio: True
        
        # Paramètres
        BoxLayout:
            size_hint_y: None
            height: 100
            orientation: 'vertical'
            spacing: 5
            
            Label:
                text: 'Taille du pinceau:'
                color: 0.8, 0.8, 0.8, 1
            
            Slider:
                id: brush_slider
                min: 5
                max: 100
                value: 20
            
            Label:
                text: 'Opacité:'
                color: 0.8, 0.8, 0.8, 1
            
            Slider:
                id: opacity_slider
                min: 0.1
                max: 1.0
                value: 1.0
        
        # Boutons d'action
        BoxLayout:
            size_hint_y: None
            height: 50
            spacing: 10
            
            Button:
                text: 'Appliquer'
                background_color: 0.18, 0.5, 0.2, 1
                on_press: root.apply_clone()
            
            Button:
                text: 'Annuler'
                background_color: 0.8, 0.2, 0.2, 1
                on_press: root.go_back()

<ToolsScreen>:
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        Label:
            text: 'Outils Avancés'
            font_size: 20
            color: 0.13, 0.59, 0.95, 1
            size_hint_y: None
            height: 40
        
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                spacing: 10
                size_hint_y: None
                height: 400
                
                Button:
                    text: '🎨 Amélioration des Couleurs'
                    size_hint_y: None
                    height: 50
                    on_press: root.apply_color_enhance()
                
                Button:
                    text: '📊 Amélioration du Contraste'
                    size_hint_y: None
                    height: 50
                    on_press: root.apply_contrast_enhance()
                
                Button:
                    text: '🔍 Amélioration de la Netteté'
                    size_hint_y: None
                    height: 50
                    on_press: root.apply_sharpness_enhance()
                
                Button:
                    text: '🧹 Débruitage'
                    size_hint_y: None
                    height: 50
                    on_press: root.apply_denoise()
                
                Button:
                    text: '🎭 Suppression d\'Arrière-Plan'
                    size_hint_y: None
                    height: 50
                    on_press: root.apply_background_removal()
                
                Button:
                    text: '🔺 Super-Résolution x2'
                    size_hint_y: None
                    height: 50
                    on_press: root.apply_super_resolution()
                
                Button:
                    text: '🏛️ Restauration de Photo'
                    size_hint_y: None
                    height: 50
                    on_press: root.apply_restore()
        
        Button:
            text: '← Retour'
            size_hint_y: None
            height: 50
            on_press: root.go_back()
'''


# ============================================
# CLASSES DES ÉCRANS
# ============================================

class MainScreen(Screen):
    """Écran principal."""
    
    def open_file_chooser(self):
        """Ouvre le sélecteur de fichiers."""
        self.manager.current = 'file_chooser'
    
    def take_photo(self):
        """Prend une photo avec la caméra."""
        # À implémenter avec la caméra Android
        self.show_message("Fonctionnalité caméra à implémenter")
    
    def go_to_tools(self):
        """Va à l'écran des outils."""
        self.manager.current = 'tools'
    
    def show_message(self, message):
        """Affiche un message popup."""
        popup = Popup(title='Information', size_hint=(0.8, 0.4))
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=50)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.content = content
        popup.open()


class FileChooserScreen(Screen):
    """Écran de sélection de fichiers."""
    file_chooser = ObjectProperty(None)
    
    def selected(self, selection):
        """Fonction appelée quand un fichier est sélectionné."""
        if selection:
            # Charger l'image et aller à l'écran d'édition
            app = App.get_running_app()
            app.current_image_path = selection[0]
            app.current_image = load_image_from_path(selection[0])
            self.manager.current = 'edit'
    
    def go_back(self):
        """Retour à l'écran principal."""
        self.manager.current = 'main'


class EditScreen(Screen):
    """Écran d'édition de l'image."""
    image_widget = ObjectProperty(None)
    
    def on_enter(self):
        """Appelé quand on entre dans l'écran."""
        app = App.get_running_app()
        if app.current_image is not None:
            texture = numpy_to_kivy_texture(app.current_image)
            if texture:
                self.image_widget.texture = texture
    
    def apply_auto_enhance(self):
        """Applique l'amélioration automatique."""
        app = App.get_running_app()
        if app.current_image is not None:
            app.current_image = auto_enhance(app.current_image)
            texture = numpy_to_kivy_texture(app.current_image)
            if texture:
                self.image_widget.texture = texture
    
    def go_to_removal(self):
        """Va à l'écran de gommage."""
        self.manager.current = 'removal'
    
    def go_to_clone(self):
        """Va à l'écran de clonage."""
        self.manager.current = 'clone'
    
    def go_back(self):
        """Retour à l'écran principal."""
        self.manager.current = 'main'
    
    def save_image(self):
        """Sauvegarde l'image."""
        app = App.get_running_app()
        if app.current_image is not None:
            output_path = get_output_path()
            if save_image_to_path(app.current_image, output_path):
                self.show_message(f"Image sauvegardée: {output_path}")
            else:
                self.show_message("Erreur de sauvegarde")
    
    def show_message(self, message):
        """Affiche un message popup."""
        popup = Popup(title='Information', size_hint=(0.8, 0.4))
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=50)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.content = content
        popup.open()


class RemovalScreen(Screen):
    """Écran de gommage d'objets."""
    image_widget = ObjectProperty(None)
    replacement = 'inpainting'
    
    def on_enter(self):
        """Appelé quand on entre dans l'écran."""
        app = App.get_running_app()
        if app.current_image is not None:
            texture = numpy_to_kivy_texture(app.current_image)
            if texture:
                self.image_widget.texture = texture
    
    def set_replacement(self, method):
        """Définit la méthode de remplacement."""
        self.replacement = method
    
    def apply_removal(self):
        """Applique le gommage."""
        app = App.get_running_app()
        if app.current_image is not None:
            # Obtenir les valeurs des sliders
            x = int(self.x_slider.value)
            y = int(self.y_slider.value)
            width = int(self.width_slider.value)
            height = int(self.height_slider.value)
            
            # Appliquer le gommage
            app.current_image = remove_object_by_rectangle(
                app.current_image, x, y, width, height, self.replacement
            )
            
            # Mettre à jour l'image
            texture = numpy_to_kivy_texture(app.current_image)
            if texture:
                self.image_widget.texture = texture
    
    def go_back(self):
        """Retour à l'écran d'édition."""
        self.manager.current = 'edit'


class CloneScreen(Screen):
    """Écran de Clone Stamp."""
    image_widget = ObjectProperty(None)
    mode = 'source'  # 'source' ou 'target'
    source_point = None
    target_point = None
    
    def on_enter(self):
        """Appelé quand on entre dans l'écran."""
        app = App.get_running_app()
        if app.current_image is not None:
            texture = numpy_to_kivy_texture(app.current_image)
            if texture:
                self.image_widget.texture = texture
    
    def set_source_mode(self):
        """Définit le mode source."""
        self.mode = 'source'
        self.show_message("Cliquez sur l'image pour définir le point source")
    
    def set_target_mode(self):
        """Définit le mode cible."""
        self.mode = 'target'
        self.show_message("Cliquez sur l'image pour définir le point cible")
    
    def apply_clone(self):
        """Applique le clonage."""
        app = App.get_running_app()
        if app.current_image is not None and self.source_point and self.target_point:
            brush_size = int(self.brush_slider.value)
            opacity = self.opacity_slider.value
            
            # Définir la source
            set_clone_source(self.source_point[0], self.source_point[1])
            
            # Appliquer le clonage
            app.current_image = clone_area(
                app.current_image,
                self.target_point[0],
                self.target_point[1],
                brush_size=brush_size,
                opacity=opacity
            )
            
            # Mettre à jour l'image
            texture = numpy_to_kivy_texture(app.current_image)
            if texture:
                self.image_widget.texture = texture
        else:
            self.show_message("Veuillez définir les points source et cible")
    
    def go_back(self):
        """Retour à l'écran d'édition."""
        self.manager.current = 'edit'
    
    def show_message(self, message):
        """Affiche un message popup."""
        popup = Popup(title='Information', size_hint=(0.8, 0.4))
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint_y=None, height=50)
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.content = content
        popup.open()


class ToolsScreen(Screen):
    """Écran des outils avancés."""
    
    def apply_color_enhance(self):
        """Applique l'amélioration des couleurs."""
        app = App.get_running_app()
        if app.current_image is not None:
            app.current_image = enhance_colors(app.current_image, strength=1.5)
            self.go_back()
    
    def apply_contrast_enhance(self):
        """Applique l'amélioration du contraste."""
        app = App.get_running_app()
        if app.current_image is not None:
            app.current_image = enhance_contrast(app.current_image, strength=1.5)
            self.go_back()
    
    def apply_sharpness_enhance(self):
        """Applique l'amélioration de la netteté."""
        app = App.get_running_app()
        if app.current_image is not None:
            app.current_image = enhance_sharpness(app.current_image, strength=1.5)
            self.go_back()
    
    def apply_denoise(self):
        """Applique le débruitage."""
        app = App.get_running_app()
        if app.current_image is not None:
            app.current_image = denoise(app.current_image, strength=0.85)
            self.go_back()
    
    def apply_background_removal(self):
        """Applique la suppression d'arrière-plan."""
        app = App.get_running_app()
        if app.current_image is not None:
            app.current_image = remove_background(app.current_image, threshold=0.7)
            self.go_back()
    
    def apply_super_resolution(self):
        """Applique la super-résolution."""
        app = App.get_running_app()
        if app.current_image is not None:
            app.current_image = upscale_x2(app.current_image)
            self.go_back()
    
    def apply_restore(self):
        """Applique la restauration."""
        app = App.get_running_app()
        if app.current_image is not None:
            app.current_image = restore(app.current_image, strength=1.0)
            self.go_back()
    
    def go_back(self):
        """Retour à l'écran d'édition."""
        self.manager.current = 'edit'


# ============================================
# APPLICATION PRINCIPALE
# ============================================

class PhotoRetouchApp(App):
    """Application principale."""
    
    current_image = None
    current_image_path = None
    
    def build(self):
        """Construire l'interface."""
        # Charger le langage KV
        Builder.load_string(KV_LANGUAGE)
        
        # Créer le gestionnaire d'écrans
        self.screen_manager = ScreenManager()
        
        # Ajouter les écrans
        self.screen_manager.add_widget(MainScreen(name='main'))
        self.screen_manager.add_widget(FileChooserScreen(name='file_chooser'))
        self.screen_manager.add_widget(EditScreen(name='edit'))
        self.screen_manager.add_widget(RemovalScreen(name='removal'))
        self.screen_manager.add_widget(CloneScreen(name='clone'))
        self.screen_manager.add_widget(ToolsScreen(name='tools'))
        
        return self.screen_manager
    
    def on_start(self):
        """Appelé au démarrage de l'application."""
        # Demander les permissions sur Android
        if ANDROID:
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.CAMERA
            ])


# ============================================
# POINT D'ENTRÉE
# ============================================

if __name__ == '__main__':
    # Vérifier que Kivy est disponible
    if not KIVY_AVAILABLE:
        print("Erreur: Kivy n'est pas installé.")
        print("Installez Kivy avec: pip install kivy")
        sys.exit(1)
    
    # Démarrer l'application
    PhotoRetouchApp().run()
