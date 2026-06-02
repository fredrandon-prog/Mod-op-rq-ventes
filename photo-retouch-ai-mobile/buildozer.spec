# Buildozer specification file for PhotoRetouch AI
# This file is used by Buildozer to create Android APK

[app]

# (str) Title of your application
#title = My Application
title = PhotoRetouch AI

# (str) Package name
#package.name = myapp
package.name = app.photoretouch.ai

# (str) Package domain (needed for android/ios packaging)
#package.domain = org.test
package.domain = org.photoretouch

# (str) Source code where the main.py live
#source.dir = .
source.dir = src

# (list) Source files to include (let empty to include all the files)
#source.include_exts = py,png,jpg,kv,atlas,json,txt,xml,ttf,woff,woff2
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,xml,onnx,yaml

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png
source.include_patterns = photoretouch_ai/**,assets/*,models/*

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec
source.exclude_exts = spec,__pycache__,*.pyc,*.pyo,*.pyd

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin
source.exclude_dirs = tests, bin, .git, __pycache__, *.egg-info

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
#version = 1.0
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.2.1,kivymd==1.1.1,opencv-python-headless==4.9.0.80,Pillow==10.2.0,numpy==1.26.4,mediapipe==0.10.11,onnxruntime==1.18.0,pyyaml==6.0.1

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source = 

# (list) Garden requirements
#garden_requirements = 

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png
icon.filename = src/photoretouch_ai/assets/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PYTHON_FILE

#
# OSX Specific customizations
#

[

# (str) Path to store the keystore for signing
#osx.codesign.identity = iPhone Developer: John Doe (3R47Z5QY5L)

#
# Android specific customizations
#

[android]

# (bool) Indicate if the application should be fullscreen or not
#fullscreen = false
fullscreen = false

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (int) Android API to use
#android.api = 30
android.api = 34

# (int) Minimum API required
#android.minapi = 21
android.minapi = 24

# (int) Android SDK version to use
#android.sdk = 20
android.sdk = 34

# (str) Android NDK version to use
#android.ndk = 19b
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) python-for-android branch to use
#android.p4a_branch = develop
android.p4a_branch = master

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of the Android library to be used
#android.library_reference =

# (str) Android logcat filters (optional)
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libs.zip
#android.copy_libs = 1

# (str) The Android entry point for the application
#android.entrypoint = org.renpy.android.PythonActivity

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src = 

# (list) Android AAR archives to add (currently works only with sdl2_gradle
# bootstrap, for details see bootstrap build script)
#android.add_aars = 

# (list) Gradle dependencies to add (currently works only with sdl2_gradle
# bootstrap, for details see bootstrap build script)
#android.add_gradle_dependencies = 

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#android.p4a_url = git+https://github.com/kivy/python-for-android.git

# (str) The bootstrap flavor for python-for-android (can be sdl2, pygame, webview, service_only or webview_sdl2)
#android.bootstrap = sdl2
android.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#android.port = 

#
# iOS specific customizations
#

[ios]

# (str) Path to store the keystore for signing
#ios.codesign.identity = iPhone Developer: John Doe (3R47Z5QY5L)

# (str) Name of the certificate to use for signing the debug version
#ios.codesign.debug = iPhone Developer: John Doe (3R47Z5QY5L)

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = iPhone Distribution: John Doe (3R47Z5QY5L)

# (str) URL pointing to the .p12 certificate to use for signing
#ios.codesign.certificate = local.p12

# (str) Name of the provisioning profile to use for signing
#ios.codesign.provisioning = iOS_Development_Profile.p12

# (str) URL pointing to the .mobileprovision provisioning profile to use for signing
#ios.codesign.provisioning_profile = local.mobileprovision

# (list) List of entitlements to use for signing the debug version
#ios.entitlements.debug = entitlements.debug.plist

# (list) List of entitlements to use for signing the release version
#ios.entitlements.release = entitlements.release.plist

# (bool) Indicate if the application should be fullscreen or not
#ios.fullscreen = true

# (str) Name of the iOS entry point for the application
#ios.entrypoint = main.py

# (list) List of iOS frameworks to add (can be a string for a single framework)
#ios.frameworks = foundation,coregraphics,quartzcore,opengles,uiKit,coreLocation

# (str) Path to store the xcodebuild archive for the application
#ios.xcodebuild_archive = xcodebuild_archive

#
# Windows specific customizations
#

[windows]

# (str) Path to store the virtual environment for the application
#windows.venv_path = venv

# (bool) Indicate if the application should be fullscreen or not
#windows.fullscreen = false

# (str) Name of the Windows entry point for the application
#windows.entrypoint = main.py

# (list) List of Windows frameworks to add (can be a string for a single framework)
#windows.frameworks = 

#
# Web specific customizations
#

[web]

# (str) Path to store the virtual environment for the application
#web.venv_path = venv

# (bool) Indicate if the application should be fullscreen or not
#web.fullscreen = false

# (str) Name of the Web entry point for the application
#web.entrypoint = main.py

# (list) List of Web frameworks to add (can be a string for a single framework)
#web.frameworks = 

#
# Additional customizations
#

# (str) Custom build command (can be a string for a single command)
#build.command = python setup.py build_ext --inplace

# (str) Custom clean command (can be a string for a single command)
#build.clean_command = rm -rf build dist

# (list) List of additional commands to run before the build
#build.pre_build_commands = 

# (list) List of additional commands to run after the build
#build.post_build_commands = 

# (str) Custom p4a branch to use for the build
#p4a.branch = develop

# (list) List of additional p4a arguments to pass to the build
#p4a.args = 

# (bool) Indicate if the application should be debuggable or not
#debug = true

# (list) List of additional Python modules to include in the build
#additional_python_modules = 

# (list) List of additional C libraries to include in the build
#additional_c_libraries = 

# (list) List of additional C++ libraries to include in the build
#additional_cpp_libraries = 

# (list) List of additional Java libraries to include in the build
#additional_java_libraries = 

# (list) List of additional Objective-C libraries to include in the build
#additional_objc_libraries = 

# (list) List of additional Swift libraries to include in the build
#additional_swift_libraries = 

# (str) Custom source code path for the application
#source.custom_path = 

# (str) Custom build directory for the application
#build.dir = build

# (str) Custom distribution directory for the application
#dist.dir = dist

# (list) List of additional files to include in the build
#additional_files = 

# (list) List of additional directories to include in the build
#additional_dirs = 

# (list) List of files to exclude from the build
#exclude_files = 

# (list) List of directories to exclude from the build
#exclude_dirs = 

# (str) Custom main.py path for the application
#main.py.path = main.py

# (str) Custom icon path for the application
#icon.path = icon.png

# (str) Custom presplash path for the application
#presplash.path = presplash.png

# (str) Custom version file path for the application
#version.path = version.txt

# (str) Custom requirements file path for the application
#requirements.path = requirements.txt

# (str) Custom source directory for the application
#source.dir.path = src

# (str) Custom build directory for the application
#build.dir.path = build

# (str) Custom distribution directory for the application
#dist.dir.path = dist
