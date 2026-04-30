"""
post_install.py — Enregistrement automatique des fichiers .okp
S'exécute après: pip install oktopios

Actions selon le système :
- Windows : association .okp + icône dans le registre
- macOS   : association .okp via Launch Services / duti
- Linux   : MIME type + icône dans /usr/share (ou ~/.local)
"""

import sys
import os
import shutil
import subprocess
import pathlib

# ─── Localiser les assets du package ─────────────────────────────────────────

def get_assets_dir():
    """Retrouver le dossier assets/icons du package installé."""
    import vm
    pkg_dir = pathlib.Path(vm.__file__).parent
    assets = pkg_dir / "assets" / "icons"
    if assets.exists():
        return assets
    return None


def get_icon(size=48, fmt="png"):
    """Retourner le chemin de l'icône dans la bonne taille."""
    assets = get_assets_dir()
    if not assets:
        return None
    icon = assets / f"oktopios-{size}.{fmt}"
    return str(icon) if icon.exists() else str(assets / "oktopios-48.png")


# ─── Windows ─────────────────────────────────────────────────────────────────

def install_windows():
    try:
        import winreg
    except ImportError:
        return False

    ico_path = None
    assets = get_assets_dir()
    if assets:
        ico_src = assets / "oktopios.ico"
        # Copier l'icône dans AppData pour qu'elle soit persistante
        app_dir = pathlib.Path(os.environ.get("LOCALAPPDATA", "")) / "Oktopios" / "icons"
        app_dir.mkdir(parents=True, exist_ok=True)
        ico_dst = app_dir / "oktopios.ico"
        if ico_src.exists():
            shutil.copy(str(ico_src), str(ico_dst))
            ico_path = str(ico_dst)

    # Trouver l'exécutable okp
    okp_exe = shutil.which("okp") or "okp"

    try:
        # 1. Créer le type de fichier .okp
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.okp") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "OktopiosFile")
            winreg.SetValueEx(key, "Content Type", 0, winreg.REG_SZ, "text/x-oktopios")

        # 2. Définir OktopiosFile
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OktopiosFile") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "Fichier Oktopios")

        # 3. Icône
        if ico_path:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OktopiosFile\DefaultIcon") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, f"{ico_path},0")

        # 4. Commande d'ouverture
        cmd = f'"{okp_exe}" "%1"'
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                               r"Software\Classes\OktopiosFile\shell\open\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, cmd)

        # 5. Notifier Windows du changement
        try:
            from ctypes import windll
            windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
        except Exception:
            pass

        print("  ✅ Windows : association .okp + icône enregistrées")
        print(f"     Icône  : {ico_path}")
        print(f"     Ouvre  : {cmd}")
        return True

    except Exception as e:
        print(f"  ⚠️  Windows registry: {e}")
        return False


# ─── macOS ───────────────────────────────────────────────────────────────────

def install_macos():
    """Enregistrer le type MIME et l'icône sur macOS."""
    icon_src = get_icon(512)

    # Copier l'icône dans ~/Library/Icons
    icons_dir = pathlib.Path.home() / "Library" / "Icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    icon_dst = icons_dir / "oktopios.png"
    if icon_src:
        shutil.copy(icon_src, str(icon_dst))

    # Créer un .app minimaliste pour l'association
    app_dir = pathlib.Path.home() / "Applications" / "Oktopios.app"
    contents = app_dir / "Contents"
    macos_dir = contents / "MacOS"
    resources_dir = contents / "Resources"
    macos_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)

    # Script de lancement
    launcher = macos_dir / "oktopios"
    launcher.write_text('#!/bin/bash\nokp "$@"\n')
    launcher.chmod(0o755)

    # Info.plist
    plist = contents / "Info.plist"
    plist.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>dev.oktopios.app</string>
    <key>CFBundleName</key>
    <string>Oktopios</string>
    <key>CFBundleExecutable</key>
    <string>oktopios</string>
    <key>CFBundleIconFile</key>
    <string>oktopios</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>Oktopios Source File</string>
            <key>CFBundleTypeExtensions</key>
            <array><string>okp</string></array>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
            <key>LSItemContentTypes</key>
            <array><string>dev.oktopios.source</string></array>
        </dict>
    </array>
    <key>UTExportedTypeDeclarations</key>
    <array>
        <dict>
            <key>UTTypeIdentifier</key>
            <string>dev.oktopios.source</string>
            <key>UTTypeDescription</key>
            <string>Oktopios Source File</string>
            <key>UTTypeConformsTo</key>
            <array><string>public.source-code</string></array>
            <key>UTTypeTagSpecification</key>
            <dict>
                <key>public.filename-extension</key>
                <array><string>okp</string></array>
            </dict>
        </dict>
    </array>
</dict>
</plist>
""")

    # Rafraîchir Launch Services
    try:
        subprocess.run(
            ["/System/Library/Frameworks/CoreServices.framework/Frameworks/"
             "LaunchServices.framework/Support/lsregister",
             "-f", str(app_dir)],
            capture_output=True
        )
    except Exception:
        pass

    print(f"  ✅ macOS : Oktopios.app créé dans ~/Applications")
    print(f"     Les fichiers .okp s'ouvriront avec okp")
    return True


# ─── Linux ───────────────────────────────────────────────────────────────────

def install_linux():
    """Enregistrer MIME type et icône sur Linux (XDG)."""
    icon_src = get_icon(48)
    icon_src_128 = get_icon(128)

    home = pathlib.Path.home()
    local = home / ".local"

    # 1. Installer l'icône dans ~/.local/share/icons
    for size, src in [(48, icon_src), (128, icon_src_128)]:
        if not src:
            continue
        icon_dir = local / "share" / "icons" / "hicolor" / f"{size}x{size}" / "mimetypes"
        icon_dir.mkdir(parents=True, exist_ok=True)
        dst = icon_dir / "text-x-oktopios.png"
        shutil.copy(src, str(dst))

    # Aussi dans apps/
    for size, src in [(48, icon_src), (128, icon_src_128)]:
        if not src:
            continue
        icon_dir = local / "share" / "icons" / "hicolor" / f"{size}x{size}" / "apps"
        icon_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, str(icon_dir / "oktopios.png"))

    # 2. Créer le fichier MIME XML
    mime_dir = local / "share" / "mime" / "packages"
    mime_dir.mkdir(parents=True, exist_ok=True)
    mime_file = mime_dir / "oktopios.xml"
    mime_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="text/x-oktopios">
    <comment>Oktopios Source File</comment>
    <comment xml:lang="fr">Fichier source Oktopios</comment>
    <glob pattern="*.okp"/>
    <magic priority="50">
      <match type="string" value="//" offset="0"/>
    </magic>
    <icon name="text-x-oktopios"/>
    <generic-icon name="text-x-script"/>
  </mime-type>
</mime-info>
""")

    # 3. Créer le .desktop
    apps_dir = local / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    desktop_file = apps_dir / "oktopios.desktop"
    okp_path = shutil.which("okp") or "okp"
    desktop_file.write_text(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Oktopios
GenericName=Oktopios Interpreter
Comment=Langage de programmation Oktopios
Exec={okp_path} %F
Icon=oktopios
Terminal=true
MimeType=text/x-oktopios;
Categories=Development;IDE;
Keywords=oktopios;okp;programming;language;
StartupNotify=false
""")
    desktop_file.chmod(0o755)

    # 4. Mettre à jour les bases de données MIME et icônes
    try:
        subprocess.run(["update-mime-database", str(local / "share" / "mime")],
                       capture_output=True)
    except FileNotFoundError:
        pass
    try:
        subprocess.run(["gtk-update-icon-cache", "-f",
                        str(local / "share" / "icons" / "hicolor")],
                       capture_output=True)
    except FileNotFoundError:
        pass
    try:
        subprocess.run(["xdg-mime", "default", "oktopios.desktop",
                        "text/x-oktopios"],
                       capture_output=True)
    except FileNotFoundError:
        pass

    print("  ✅ Linux : MIME type text/x-oktopios + icône + .desktop enregistrés")
    print(f"     Les fichiers .okp affichent l'icône Oktopios dans votre gestionnaire de fichiers")
    return True


# ─── Point d'entrée ──────────────────────────────────────────────────────────

def run_post_install():
    print()
    print("  🐙 Oktopios — Configuration du système...")
    print()

    if sys.platform == "win32":
        install_windows()
    elif sys.platform == "darwin":
        install_macos()
    else:
        install_linux()

    print()
    print("  Pour forcer la mise à jour des icônes sur Linux :")
    print("    update-mime-database ~/.local/share/mime")
    print("    gtk-update-icon-cache -f ~/.local/share/icons/hicolor")
    print()


if __name__ == "__main__":
    run_post_install()
