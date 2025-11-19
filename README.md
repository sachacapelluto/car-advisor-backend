# 🚗 Car Advisor - AI-Powered Car Recommendation System

Application de conseil automobile intelligente avec chatbot IA, filtres avancés et comparaison de véhicules.

## 🎯 Fonctionnalités

- **Chatbot IA avec mémoire conversationnelle** : Conversations naturelles avec contexte
- **RAG (Retrieval Augmented Generation)** : Recommandations basées sur les données réelles
- **Filtres combinés** : Filtres manuels + extraction automatique par IA
- **Comparaison de voitures** : Tableau de comparaison détaillé
- **Interface moderne** : Design 3 colonnes responsive

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Framework** : FastAPI
- **Base de données** : Supabase (PostgreSQL)
- **IA** : OpenAI GPT-4o-mini
- **ORM** : Supabase Client

### Frontend (Lovable)
- **Framework** : React + TypeScript
- **Styling** : Tailwind CSS
- **Icons** : Lucide React

## 📦 Installation

### Prérequis
- Python 3.11+
- Compte Supabase
- Clé API OpenAI

### Backend
```bash
# Cloner le repo
git clone <votre-repo-gitlab>
cd car-advisor-backend

# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
cp .env.example .env
# Remplir les variables d'environnement

# Lancer le serveur
uvicorn app.main:app --reload
```

### Variables d'environnement (.env)
```env
# Supabase
SUPABASE_URL=votre_url_supabase
SUPABASE_KEY=votre_service_role_key

# OpenAI
OPENAI_API_KEY=votre_clé_openai

# App
APP_NAME=Car Advisor
APP_VERSION=1.0.0
```

## 🚀 API Endpoints

### Voitures
- `GET /cars` - Liste toutes les voitures (avec filtres optionnels)
- `GET /cars/{id}` - Détails d'une voiture
- `POST /cars` - Créer une voiture
- `PUT /cars/{id}` - Mettre à jour une voiture
- `DELETE /cars/{id}` - Supprimer une voiture

### Chat
- `POST /chat` - Envoyer un message au chatbot

### Comparaison
- `POST /cars/compare` - Comparer plusieurs voitures

## 📊 Base de données

### Table `cars`
```sql
- id (uuid)
- brand (text)
- model (text)
- year (integer)
- price (numeric)
- fuel_type (text)
- transmission (text)
- seats (integer)
- doors (integer)
- color (text)
- created_at (timestamp)
- updated_at (timestamp)
```

## 🧠 Fonctionnement du RAG

1. **Extraction de filtres** : L'IA analyse le message utilisateur
2. **Combinaison** : Filtres manuels + filtres IA
3. **Recherche** : Requête dans Supabase
4. **Génération** : Réponse naturelle avec OpenAI
5. **Mémoire** : Contexte conversationnel maintenu

## 🎨 Frontend

Interface Lovable déployée avec :
- Chat central avec historique
- Filtres à gauche
- Liste de voitures à droite
- Modal de comparaison

## 📈 Prochaines étapes

- [ ] Déploiement en production (Railway/Render)
- [ ] Ajouter des images réelles de voitures
- [ ] Implémenter LangChain pour embeddings
- [ ] Ajouter authentification utilisateur
- [ ] Système de favoris
- [ ] Export PDF des comparaisons

## 👨‍💻 Auteur

Créé avec ❤️ par [Votre nom]

## 📄 Licence

MIT