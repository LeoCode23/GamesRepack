import os
import zipfile
import shutil
from tqdm import tqdm
from pathlib import Path
import time
import hashlib
import subprocess


#H:/GamesBlue/Madden NFL 20
#H:/GamesBlue/Oddworld - Munch's Oddysee
#Problème de résolution suite à l'installation: .exe -> properties -> high dpi setting -> overide high dpi (ON) -> option 'application'
jeu_source = Path("H:/GamesBlue/Madden NFL 20")
nom_jeu = jeu_source.name

base_repack = Path("C:/Users/leot2/OneDrive/Bureau/Note/Python")
dossier_final = base_repack / nom_jeu
taille_max_bin = 20 * 1024**3
fichier_zip = dossier_final / f"{nom_jeu}.zip"

def compresser_jeu(source: Path, destination: Path):
    fichiers = [f for f in source.rglob('*') if f.is_file()]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for f in tqdm(fichiers, desc="Compression", unit="fichier"):
            zipf.write(f, arcname=f.relative_to(source))

def decouper_zip(archive: Path, dossier_sortie: Path):
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    with open(archive, 'rb') as f:
        index = 1
        while True:
            chunk = f.read(taille_max_bin)
            if not chunk:
                break
            with open(dossier_sortie / f"{nom_jeu}.part{index:03}.bin", 'wb') as f_out:
                f_out.write(chunk)
            index += 1

def generer_hash_sha256(fichier):
    h = hashlib.sha256()
    with open(fichier, 'rb') as f:
        for bloc in iter(lambda: f.read(1024 * 1024), b''):
            h.update(bloc)
    return h.hexdigest()

def sauvegarder_hashes(dossier, fichier_out):
    lignes = []
    for bin_file in sorted(dossier.glob("*.bin")):
        hash_val = generer_hash_sha256(bin_file)
        lignes.append(f"{bin_file.name}:{hash_val}")
    fichier_out.write_text("\n".join(lignes), encoding='utf-8')

def generer_installeur():
    script = Path("installeur.py")
    contenu = f'''
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import os
import time
from pathlib import Path
import hashlib
import sys

NOM_JEU = "{nom_jeu}"

def extraire_zip(zip_path, dest_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        fichiers = zip_ref.namelist()
        total = len(fichiers)
        debut = time.time()
        for i, f in enumerate(fichiers):
            zip_ref.extract(f, dest_path)
            elapsed = time.time() - debut
            eta = (elapsed / (i + 1)) * (total - i - 1)
            print(f"Progression : {{i + 1}}/{{total}} | ETA : {{eta:.1f}} sec")

def verifier_hash(fichier, hash_attendu):
    h = hashlib.sha256()
    with open(fichier, 'rb') as f:
        for bloc in iter(lambda: f.read(1024 * 1024), b''):
            h.update(bloc)
    return h.hexdigest() == hash_attendu

def reconstruire_zip(zip_final, base):
    hash_file = Path(sys._MEIPASS) / "hashes.txt" if hasattr(sys, "_MEIPASS") else base / "hashes.txt"
    if not hash_file.exists():
        raise Exception("Fichier de hash manquant.")
    lignes = hash_file.read_text(encoding='utf-8').splitlines()
    for ligne in lignes:
        nom_fichier, hash_attendu = ligne.split(":")
        fichier = base / nom_fichier
        if not fichier.exists() or not verifier_hash(fichier, hash_attendu):
            raise Exception(f"Fichier corrompu ou absent : {{nom_fichier}}")
    with open(zip_final, 'wb') as f_out:
        for ligne in lignes:
            nom_fichier, _ = ligne.split(":")
            with open(base / nom_fichier, 'rb') as f_in:
                f_out.write(f_in.read())

root = tk.Tk()
root.withdraw()
destination_root = filedialog.askdirectory(title="Choisir le dossier d'installation")
if not destination_root:
    messagebox.showerror("Erreur", "Aucun dossier sélectionné.")
    exit()

destination = Path(destination_root) / NOM_JEU
destination.mkdir(parents=True, exist_ok=True)

messagebox.showinfo("Repack", f"Repack for Life 🚀\\nInstallation dans : {{destination}}")

base_dir = Path(sys.executable).parent
zip_temp = base_dir / "temp.zip"
reconstruire_zip(zip_temp, base_dir)
extraire_zip(zip_temp, destination)
os.remove(zip_temp)
messagebox.showinfo("Terminé", "Jeu installé avec succès !")
'''
    script.write_text(contenu, encoding='utf-8')
    return script



def compiler_exe(script: Path):
    shutil.copy(dossier_final / "hashes.txt", Path.cwd() / "hashes.txt")
    subprocess.run([
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--add-data", "hashes.txt;.",
        "--distpath", ".",
        str(script)
    ], check=True)

def repack():
    if not jeu_source.exists():
        print("Dossier de jeu introuvable.")
        return
    compresser_jeu(jeu_source, fichier_zip)
    decouper_zip(fichier_zip, dossier_final)
    sauvegarder_hashes(dossier_final, dossier_final / "hashes.txt")
    fichier_zip.unlink()
    script = generer_installeur()
    compiler_exe(script)
    if Path("installeur.exe").exists():
        shutil.move("installeur.exe", dossier_final / "installeur.exe")
    if Path("hashes.txt").exists():
        os.remove("hashes.txt")
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
    Path("installeur.spec").unlink(missing_ok=True)
    script.unlink()
    print(f"✅ Repack terminé dans : {dossier_final}")

if __name__ == "__main__":
    repack()