from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
import os 

# --- CONFIGURATION BASE DE DONNÉES MODIFIÉE POUR LE CLOUD ---
# On crée un dossier 'data' s'il n'existe pas pour stocker la DB de façon persistante
DB_DIR = "./data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# La base de données sera maintenant dans ./data/ventes.db
DATABASE_URL = f"sqlite:///{DB_DIR}/ventes.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle de la Table
class VenteDB(Base):
    __tablename__ = "ventes"
    id = Column(Integer, primary_key=True, index=True)
    produit = Column(String)
    prix = Column(Float)

Base.metadata.create_all(bind=engine)

# Schémas de données
class VenteBase(BaseModel):
    produit: str
    prix: float

class VenteResponse(VenteBase):
    id: int
    class Config:
        from_attributes = True

app = FastAPI(title="API de Gestion de Ventes")

# Dépendance DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES (Inchangées, elles sont parfaites) ---

@app.post("/login")
def login(payload: dict):
    if payload.get("username") == "admin" and payload.get("password") == "1234":
        return {"status": "success", "token": "fake-jwt-token"}
    raise HTTPException(status_code=401, detail="Identifiants incorrects")

@app.get("/ventes", response_model=List[VenteResponse])
def lire_ventes(db: Session = Depends(get_db)):
    return db.query(VenteDB).all()

@app.post("/ventes", response_model=VenteResponse)
def creer_vente(vente: VenteBase, db: Session = Depends(get_db)):
    nouvelle_vente = VenteDB(produit=vente.produit, prix=vente.prix)
    db.add(nouvelle_vente)
    db.commit()
    db.refresh(nouvelle_vente)
    return nouvelle_vente

@app.put("/ventes/{vente_id}")
def modifier_vente(vente_id: int, vente_update: VenteBase, db: Session = Depends(get_db)):
    db_vente = db.query(VenteDB).filter(VenteDB.id == vente_id).first()
    if not db_vente:
        raise HTTPException(status_code=404, detail="Vente non trouvée")
    db_vente.produit = vente_update.produit
    db_vente.prix = vente_update.prix
    db.commit()
    return {"message": "Mis à jour"}

@app.delete("/ventes/{vente_id}")
def supprimer_vente(vente_id: int, db: Session = Depends(get_db)):
    db_vente = db.query(VenteDB).filter(VenteDB.id == vente_id).first()
    if not db_vente:
        raise HTTPException(status_code=404, detail="Vente non trouvée")
    db.delete(db_vente)
    db.commit()
    return {"message": "Supprimé"}