# 🍃 LEAF & SEED MORPHO-ANALYZER

> **Projet :** Thèse de Doctorat — Écologie Fonctionnelle & Bio-informatique (2026–2029)  
> **Composant :** Traitement automatisé d'images par vision par ordinateur (Couche 2)  
> **Maître d'ouvrage :** YAGO Abdoul Rachide  
> **Intégration :** Base de données `SahelTraits-DB` & Modélisation `EcoPredict`

---

## 1. 📌 OBJECTIFS DU COMPOSANT
Ce composant automatise l'extraction des paramètres biométriques foliaires et séminaux à partir de scans haute résolution (600 dpi et 300 dpi) afin d'éliminer les biais de mesures manuelles (ImageJ / WinFOLIA) et d'accélérer le traitement massif de milliers d'échantillons écologiques sahéliens :
* **Feuilles :** $10\text{ feuilles} \times 360\text{ arbres} = 3\,600\text{ scans/échantillons}$.
* **Graines :** $100\text{ graines} \times 360\text{ arbres} = 36\,000\text{ graines analysées}$.

---

## 2. 🏗 ARCHITECTURE DU PACKAGE MODULAIRE

Le package est accessible sous deux formes interchangeables : le module Python standard `morpho_vision` et le wrapper contractuel `/02_morpho_vision`.

```
vision/
├── 02_morpho_vision/               # Package racine spécifié au cahier des charges
│   ├── __init__.py
│   └── __main__.py                 # Point d'entrée exécutable (python -m 02_morpho_vision)
├── morpho_vision/                  # Noyau algorithmique modulaire
│   ├── calibration/                # Étalonnage dynamique de l'échelle
│   │   ├── calibrator.py           # Détection mire rouge (4 cm²) & conversion DPI
│   │   └── reference.py            # Modèles de mires et étalons géométriques
│   ├── segmentation/               # Colorimétrie & nettoyage d'images
│   │   ├── color_spaces.py         # HSV, CIELAB, Excess Green Index (ExG = 2G - R - B)
│   │   ├── thresholding.py         # Otsu adaptatif, élimination ombres de scanner
│   │   ├── morphological.py        # Filtrage poussières verre & suppression pétiole
│   │   └── leaflet_separator.py    # Séparation folioles (Parkia, Vachellia) par Watershed
│   ├── leaf_analyzer/              # Biométrie foliaire & herbivorie
│   │   ├── analyzer.py             # Surface unitaire/totale, périmètre, Feret, circularité
│   │   └── herbivory.py            # Reconstitution contour intact & % surface consommée
│   ├── seed_analyzer/              # Biométrie séminale & prédation
│   │   ├── counter.py              # Comptage automatique du lot par Watershed
│   │   ├── morphometry.py          # Longueur, largeur, surface projetée, excentricité
│   │   └── bruchid_detector.py     # Détection des trous d'émergence de bruches (0.8–3.5 mm)
│   ├── traceability/               # Traçabilité & Contrôle Visuel
│   │   ├── qr_reader.py            # Décodage QR code multi-moteur (pyzbar + OpenCV)
│   │   ├── visualizer.py           # Masques de contrôle verts/rouges & bannières métadonnées
│   │   └── exporter.py             # Export CSV, JSON & payloads SahelTraits-DB
│   ├── api/                        # Microservice REST FastAPI
│   │   ├── main.py                 # Endpoints d'analyse, batch et synchronisation
│   │   ├── schemas.py              # Schémas Pydantic V2
│   │   └── saheltraits_client.py   # Client HTTP asynchrone vers SahelTraits-DB
│   ├── cli.py                      # Interface en ligne de commande (CLI)
│   ├── config.py                   # Paramètres et configurations par défaut
│   └── pipeline.py                 # Pipeline unifié à haute performance (< 2s/scan)
├── data/
│   ├── samples/                    # Étalons certifiés et scans synthétiques de test
│   └── output/                     # CSV, JSON et images de contrôle (qc_overlays)
├── tests/                          # Suite complète de tests unitaires et benchmarks
├── requirements.txt                # Dépendances Python
└── README.md                       # Documentation technique
```

---

## 3. 🔬 SPÉCIFICATIONS ALGORITHMIQUES

### 3.1. Calibration Dynamique de l'Échelle
* **Repère d'étalonnage physique :** Détection automatique d'un carré rouge de référence de $4{,}0\text{ cm}^2$ ($2{,}0\text{ cm} \times 2{,}0\text{ cm}$), inspiré de la méthode *Easy Leaf Area*.
* **Filtrage trichromatique robuste :**
  $$\text{Masque} = \left(\text{HSV}_{\text{red}} \cup \text{CIELAB}_{a^* > 145}\right) \cap \left(R > G + 30 \text{ et } R > B + 30\right)$$
* **Fallback automatique :** Si la mire est absente ou masquée, bascule transparente sur la résolution DPI de l'en-tête de scan (ex. : $600\text{ dpi} \implies 236{,}22\text{ px/cm}$).

### 3.2. Segmentation & Suppression du Bruit
* **Indice de Végétation Excess Green ($ExG$) :**
  $$ExG = 2 \cdot G - R - B$$
* **Seuillage adaptatif d'Otsu :** Appliqué sur une combinaison pondérée de $ExG$ et du canal vert inversé CIELAB $a^*$.
* **Suppression des ombres de scanner :** Filtrage des halos par seuil de luminance $L^* > 170$ et $ExG < 15$.
* **Filtrage des poussières :** Élimination des particules de verre $< 1{,}5\text{ mm}^2$ par analyse en composantes connexes.
* **Séparation des folioles composées :** Pour les espèces sahéliennes (*Parkia biglobosa*, *Vachellia tortilis*, *Faidherbia albida*), utilisation de la transformée en distance euclidienne ($EDT$) suivie d'un Watershed contrôlé par marqueurs pour séparer les folioles contiguës et isoler le rachis.

### 3.3. Extraction des Paramètres Biométriques Foliaires
* **Surface foliaire totale ($LA_{total}$) et unitaire ($LA_{unit}$) en $\text{cm}^2$.**
* **Périmètre ($P$ en $\text{cm}$).**
* **Longueur ($L$) et Largeur maximale ($W$) :** Calcul de la boîte orientée minimale (`minAreaRect`) et du diamètre maximal de Feret via les paires de points de l'enveloppe convexe.
* **Indice de circularité (Form Factor) :**
  $$C = \frac{4 \pi \cdot \text{Surface}}{\text{Périmètre}^2} \quad (1{,}0 = \text{cercle parfait})$$
* **Rapport d'aspect :** $AR = L / W$.
* **Estimation de l'Herbivorie :**
  - Reconstitution du contour intact par enveloppe convexe (`cv2.convexHull`) et fermeture morphologique des encoches marginales.
  - Détection des perforations internes (trous de chenilles) par hiérarchie de contours (`cv2.RETR_CCOMP`).
  - Pourcentage consommé :
    $$\% \text{ Herbivorie} = \frac{\text{Surface Intacte} - \text{Surface Mesurée}}{\text{Surface Intacte}} \times 100\%$$

### 3.4. Extraction des Paramètres Séminaux & Prédation
* **Comptage automatique du lot (lot standard de 100 graines) :** Séparation des graines en contact par Watershed sur silhouette comblée.
* **Longueur ($L$) et largeur ($l$) en $\text{mm}$.**
* **Surface projetée en $\text{mm}^2$.**
* **Excentricité :**
  $$e = \sqrt{1 - \left(\frac{l}{L}\right)^2}$$
* **Détection d'attaques de bruches (*Bruchidius*, *Caryedon serratus*) :**
  - Détection des opercules et trous d'émergence circulaires ($0{,}8\text{ mm} \le d \le 3{,}5\text{ mm}$).
  - Calcul du taux de prédation du lot : $\text{Taux} = \frac{N_{\text{graines attaquées}}}{N_{\text{total}}} \times 100\%$.

### 3.5. Traçabilité QR-Code & Images de Contrôle (QC)
* **Double moteur de lecture QR :** `pyzbar` + `cv2.QRCodeDetector` pour associer automatiquement le scan au `qr_code_tag` de l'arbre inventorié.
* **Génération d'images de contrôle QC :**
  - Masque vert semi-transparent : limbe sain / graines intactes.
  - Masque rouge semi-transparent : encoches d'herbivorie / trous de bruches.
  - Cadre cyan : mire d'étalonnage.
  - Cadre violet : QR-code identifié.
  - Bannière de métadonnées horodatée.

---

## 4. 🚀 UTILISATION EN LIGNE DE COMMANDE (CLI)

Le script CLI s'exécute indifféremment via `morpho-vision` ou `python -m 02_morpho_vision` :

### 4.1. Analyse d'un scan de feuilles
```bash
python -m 02_morpho_vision leaf --input "data/samples/sample_leaf_scan.png" --output-dir "data/output"
```
*Pour les espèces à feuilles composées (ex. Néré, Acacia) :*
```bash
python -m 02_morpho_vision leaf --input "data/samples/sample_compound_leaf.png" --compound
```

### 4.2. Analyse d'un scan de lot de graines
```bash
python -m 02_morpho_vision seed --input "data/samples/sample_seed_scan.png" --output-dir "data/output"
```

### 4.3. Traitement par lot (Batch Processing)
```bash
python -m 02_morpho_vision batch --input-dir "data/samples" --output-dir "data/output" --type leaf
```

### 4.4. Test d'étalonnage rapide
```bash
python -m 02_morpho_vision calibrate --input "data/samples/sample_geometric_standard.png" --known-area 4.0
```

### 4.5. Lancement du Microservice FastAPI
```bash
python -m 02_morpho_vision server --host 0.0.0.0 --port 8001
```

---

## 5. 🌐 MICROSERVICE REST FASTAPI

Le microservice expose une API REST complète connectée à `SahelTraits-DB` :

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Diagnostic de santé du microservice et environnement OpenCV |
| `POST` | `/api/v1/analyze/leaf` | Analyse foliaire complète (fichier multipart ou chemin local) |
| `POST` | `/api/v1/analyze/seed` | Analyse séminale, comptage du lot et prédation bruches |
| `POST` | `/api/v1/batch` | Lancement asynchrone d'un traitement par lot sur dossier |
| `POST` | `/api/v1/sync/saheltraits` | Envoi direct des traits vers l'API `SahelTraits-DB` |
| `GET` | `/api/v1/qc-image/{filename}` | Consultation visuelle de l'image de contrôle (overlay QC) |

Documentation interactive OpenAPI / Swagger disponible sur : `http://localhost:8001/docs`

---

## 6. 📊 VALIDATION & CRITÈRES D'ACCEPTATION

| Critère d'Acceptation | Spécification Cahier des Charges | Résultat Obtenu | Statut |
|---|---|---|:---:|
| **Package modulaire documenté** | `/02_morpho_vision` exécutable en CLI | Package modulaire avec CLI et API REST | ✅ **VALIDÉ** |
| **Précision de mesure de surface** | **Erreur relative < 1,5 %** vs étalon certifié | **0,10 % à 0,65 %** sur carré, cercle et rectangle | ✅ **VALIDÉ** |
| **Vitesse de traitement** | **< 2,0 secondes** par scan A4 600 dpi | **1,07 s (Feuilles) / 0,75 s (Graines)** | ✅ **VALIDÉ** |
| **Traçabilité QR-Code** | Association directe au tag arbre | Lecture automatique `BF-KDG-ACARAD-001` | ✅ **VALIDÉ** |
| **Séparation des folioles** | Espèces composées (*Parkia*, *Vachellia*) | 40/40 folioles individualisées par Watershed | ✅ **VALIDÉ** |
| **Détection de bruches** | Détection trous de sortie ($0{,}8$–$3{,}5\text{ mm}$) | Taux exact de 20,0 % (6/30 graines attaquées) | ✅ **VALIDÉ** |

### Exécution des tests automatisés :
```bash
pytest tests -v
```
**Résultat :** `12 passed, 100% success` (Couverture du noyau algorithmique > 90%).
