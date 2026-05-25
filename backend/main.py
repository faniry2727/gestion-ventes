from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
import os

if not os.path.exists("./data"):
    os.makedirs("./data")

DATABASE_URL = "sqlite:///./data/ventes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class VenteDB(Base):
    __tablename__ = "ventes"
    id = Column(Integer, primary_key=True, index=True)
    produit = Column(String)
    quantite = Column(Integer, default=1)      # Nouvelle colonne
    prix_unitaire = Column(Float, default=0.0) # Nouvelle colonne

Base.metadata.create_all(bind=engine)

class VenteBase(BaseModel):
    produit: str
    quantite: int
    prix_unitaire: float

class VenteResponse(VenteBase):
    id: int
    class Config:
        from_attributes = True

app = FastAPI()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/login")
def login(payload: dict):
    if payload.get("username") == "admin" and payload.get("password") == "1234":
        return {"status": "success"}
    raise HTTPException(status_code=401)

@app.get("/ventes", response_model=List[VenteResponse])
def lire_ventes(db: Session = Depends(get_db)):
    return db.query(VenteDB).all()

@app.post("/ventes")
def creer_vente(vente: VenteBase, db: Session = Depends(get_db)):
    db_vente = VenteDB(
        produit=vente.produit, 
        quantite=vente.quantite, 
        prix_unitaire=vente.prix_unitaire
    )
    db.add(db_vente); db.commit(); db.refresh(db_vente)
    return db_vente

@app.put("/ventes/{vente_id}")
def modifier_vente(vente_id: int, vente_update: VenteBase, db: Session = Depends(get_db)):
    db_vente = db.query(VenteDB).filter(VenteDB.id == vente_id).first()
    if not db_vente: raise HTTPException(status_code=404)
    db_vente.produit = vente_update.produit
    db_vente.quantite = vente_update.quantite
    db_vente.prix_unitaire = vente_update.prix_unitaire
    db.commit()
    return {"message": "success"}

@app.delete("/ventes/{vente_id}")
def supprimer_vente(vente_id: int, db: Session = Depends(get_db)):
    db_vente = db.query(VenteDB).filter(VenteDB.id == vente_id).first()
    if not db_vente: raise HTTPException(status_code=404)
    db.delete(db_vente); db.commit()
    return {"message": "deleted"}