import os
import urllib.request
import zipfile

def download_chinook_db():
    """Télécharge et extrait la base de données Chinook"""
    # URL de la base de données Chinook
    db_url = "https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip"
    zip_path = "chinook.zip"
    
    print("Téléchargement de la base de données Chinook...")
    
    # Téléchargement du fichier
    urllib.request.urlretrieve(db_url, zip_path)
    
    # Extraction du fichier
    print("Extraction de l'archive...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("data")
    
    # Nettoyage
    os.remove(zip_path)
    
    # Vérification du fichier extrait
    db_path = os.path.join("data", "chinook.db")
    if os.path.exists(db_path):
        print(f"La base de données a été téléchargée avec succès : {os.path.abspath(db_path)}")
        return True
    else:
        print("Erreur lors du téléchargement ou de l'extraction de la base de données.")
        return False

if __name__ == "__main__":
    # Création du dossier data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    # Téléchargement de la base de données
    if download_chinook_db():
        print("\nVous pouvez maintenant lancer le tableau de bord avec la commande :")
        print("python dashboard.py")
    else:
        print("\nÉchec du téléchargement de la base de données.")
        print("Veuillez vérifier votre connexion Internet et réessayer.")
