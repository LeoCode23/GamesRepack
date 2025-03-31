import os
import shutil
import subprocess
from pathlib import Path

# Name of file
nom_app = "OxygenNotIncluded.app"
chemin_app = Path("/Applications") / nom_app
nom_volume = "OxygenNotIncluded"
dossier_temp = Path("/tmp/RepackDMG")
dossier_sortie = Path("~/Desktop/RepackOutput").expanduser()
nom_dmg = f"{nom_volume}.dmg"
chemin_dmg = dossier_sortie / nom_dmg

def confirmer(message):
    input(f"[CONFIRMER] {message} (Entrée pour continuer)")

def preparer_temp():
    if dossier_temp.exists():
        shutil.rmtree(dossier_temp)
    dossier_temp.mkdir(parents=True)
    shutil.copytree(chemin_app, dossier_temp / nom_app)

def creer_dossier_sortie():
    dossier_sortie.mkdir(parents=True, exist_ok=True)

def creer_dmg():
    if chemin_dmg.exists():
        chemin_dmg.unlink()
    subprocess.run([
        "hdiutil", "create",
        "-volname", nom_volume,
        "-srcfolder", str(dossier_temp),
        "-format", "UDZO", 
        str(chemin_dmg)
    ])

def main():
    if not chemin_app.exists():
        print(f"❌ L'application {chemin_app} est introuvable.")
        return

    confirmer("Créer une image disque DMG compressée dans un dossier dédié ?")
    preparer_temp()
    creer_dossier_sortie()
    creer_dmg()
    print(f"✅ DMG créé avec succès : {chemin_dmg}")

if __name__ == "__main__":
    main()
