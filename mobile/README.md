# SahelField Mobile App & Enquêtes Numériques (Couche 1)
**Projet :** Thèse de Doctorat — Écologie Fonctionnelle & Bio-informatique (2026–2029)  
**Composant :** Collecte terrain hors-ligne, traçabilité QR-Code et enquêtes socio-écologiques  
**Maître d'ouvrage :** YAGO Abdoul Rachide (UJKZ - École Doctorale Sciences & Technologies / ICC)

---

## 1. Vue d'Ensemble & Objectifs
SahelField est l'application mobile *offline-first* dédiée aux campagnes de terrain des écosystèmes sahéliens et soudano-sahéliens du Burkina Faso (Dori, Kaya, Pô). Elle assure :
1. **La collecte dendrométrique & régénération** sur placettes permanentes calibrées (50 m × 20 m et 5 m × 5 m) avec géolocalisation GPS haute précision (< 5 m).
2. **La traçabilité biométrique intégrale via QR-Codes** reliant chaque arbre aux sachets foliaires (`TAG-LEAF-...`), carottes de bois (`TAG-WOOD-...`), lots de semences (`LOT-SEED-...`) et prélèvements de sol (`TAG-SOIL-...`).
3. **Le suivi des traits fonctionnels (ETS v1.0)** en laboratoire et sur le terrain avec contrôle qualité statistique temps réel (détection automatique des 3-sigmas) et respect strict des règles biologiques (masse sèche foliaire impérativement inférieure à la masse fraîche saturée).
4. **Le déploiement des enquêtes socio-écologiques auprès de 450 répondants** (150 experts et 300 riverains locaux) grâce à la trame standard **XLSForm** (`sahelfield_enquete_socioeco.xlsx`) et un runner applicatif local avec calcul temps réel de l'Indice de Saillance de Smith.
5. **La synchronisation différée transactionnelle** vers l'API backend `SahelTraits-DB` (`POST /api/v1/sync/field-batch`) dès la disponibilité d'un réseau 4G ou Wi-Fi, avec garantie formelle de **zéro perte de données** en cas de redémarrage du smartphone en mode avion.

---

## 2. Architecture Technique

```
mobile/
├── public/
│   ├── manifest.json                  # PWA Manifest Android installable
│   ├── sw.js                          # Service Worker (CacheFirst + NetworkFallback)
│   ├── icons/                         # Icônes PWA 192x192 & 512x512
│   └── forms/
│       └── sahelfield_enquete_socioeco.xlsx # Trame XLSForm standard KoboToolbox / ODK
├── src/
│   ├── app/
│   │   ├── layout.tsx                 # Layout PWA global + bandeau offline & audio
│   │   ├── page.tsx                   # Tableau de bord principal & métriques
│   │   ├── plots/page.tsx             # Gestion des placettes 50x20m & régénération 5x5m
│   │   ├── inventory/page.tsx         # Saisie dendrométrique rapide (DHP >= 5cm)
│   │   ├── traits/page.tsx            # Traits ETS v1.0 (SLA, LDMC, bois, graines, sol)
│   │   ├── qrcode/page.tsx            # Générateur d'étiquettes & scanner caméra
│   │   ├── surveys/page.tsx           # Enquêtes M1-M5 & export XLSForm Kobo
│   │   └── sync/page.tsx              # Synchronisation différée POST /api/v1/sync/field-batch
│   ├── components/
│   │   ├── Navigation.tsx             # Barre de navigation mobile ergonomique
│   │   ├── OfflineBadge.tsx           # Indicateur réseau temps réel & synthèse vocale
│   │   ├── GPSWidget.tsx              # Geolocation API native avec badge précision < 5m
│   │   ├── QRScannerModal.tsx         # Scanner caméra MediaDevices avec fallback manuel
│   │   ├── QRTagGenerator.tsx         # Générateur et exportateur d'étiquettes QR
│   │   └── CameraCapture.tsx          # Capture photo native avec compression locale
│   ├── lib/
│   │   ├── db.ts                      # Dexie.js (IndexedDB) pour persistance 100% hors-ligne
│   │   ├── syncService.ts             # Client d'ingestion vers SahelTraits-DB FastAPI
│   │   ├── validation.ts              # Moteur de règles de validation métier & 3-sigmas
│   │   ├── taxaData.ts                # Référentiel taxonomique (Noms scientifiques + Mooré/Dioula/Fulfuldé)
│   │   ├── speechFeedback.ts          # Feedback vocal Web Speech API
│   │   └── xlsformGenerator.ts        # Constructeur XLSForm multi-onglets (survey/choices/settings)
│   └── types/index.ts                 # Définitions TypeScript strictes
├── scripts/
│   └── generate_xlsform.js            # Script Node de génération du classeur XLSForm
├── tests/
│   ├── validation.test.js             # Tests unitaires des règles de cohérence biologique
│   ├── xlsform.test.js                # Tests de conformité du classeur KoboToolbox
│   └── syncQueue.test.js              # Tests du format du payload SyncBatchRequest
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

---

## 3. Fonctionnalités Clés Implémentées

### 3.1. Gestion des Placettes & Sous-Placettes
* **Placettes Permanentes (50 m × 20 m = 1 000 m²) :** Saisie rapide de l'identifiant (ex: `BF-DOR-01`), zone bioclimatique (Sahélienne, Soudano-Sahélienne, Soudanienne), altitude, pente en degrés, statut de protection et historique des feux sur 20 ans.
* **Capture GPS Intégrée :** Utilisation de l'API Geolocation avec indicateur de qualité satellite temps réel (`< 5m Haute Précision`, `5-10m Acceptable`, `>10m Faible`).
* **Sous-placettes de régénération (5 m × 5 m = 25 m²) :** Relevé des 4 quadrants (A, B, C, D) par classe de hauteur (`< 50 cm`, `50-150 cm`, `> 150 cm`) pour évaluer le renouvellement naturel des ligneux.

### 3.2. Saisie Dendrométrique des Individus
* **DHP $\ge 5$ cm :** Vérification stricte en temps réel. Si $DHP < 5$ cm, l'application émet un message et une alerte vocale invitant à basculer vers les sous-placettes de régénération. Les DHP négatifs sont strictement bloqués.
* **Paramètres biométriques :** Hauteur totale, diamètre du houppier, position dans la canopée (*Dominant*, *Codominant*, *Intermédiaire*, *Sous-étage*, *Émergent*) et score d'état sanitaire standardisé de 1 à 5.
* **Prise de photo native :** Capture via la caméra de l'appareil avec compression automatique et stockage Base64 dans IndexedDB.

### 3.3. Générateur & Scanner de QR-Codes
* **Génération multi-organes :**
  * Arbre : `TAG-BF-DOR-BAL-001`
  * Sachet foliaire : `TAG-LEAF-BF-DOR-BAL-001-A`
  * Carotte de bois : `TAG-WOOD-BF-DOR-BAL-001`
  * Lot de semences : `LOT-BAL-DOR-2026-001`
  * Échantillon de sol : `TAG-SOIL-BF-DOR-01-S001`
* **Impression & Téléchargement :** Aperçu étiquette format terrain, téléchargement PNG et impression directe.
* **Scanner Caméra :** Décodage instantané du flux vidéo pour rattacher immédiatement une pesée de laboratoire ou un essai de germination à l'individu terrain.

### 3.4. Validation Temps Réel & Détection des 3-Sigmas
* **Règle foliaire inviolable :** Blocage absolu si la masse sèche foliaire dépasse la masse fraîche saturée ($M_{dry} \le M_{fresh}$).
* **Calcul automatique de traits :**
  $$SLA = \frac{\text{Surface foliaire }(mm^2)}{\text{Masse sèche }(mg)} \quad (mm^2/mg)$$
  $$LDMC = \frac{\text{Masse sèche }(mg)}{\text{Masse fraîche }(mg)} \times 1000 \quad (mg/g)$$
  $$\text{Densité du bois} = \frac{\text{Masse sèche }(g)}{\text{Volume déplacé }(cm^3)} \quad (g/cm^3)$$
* **Détection statistique 3-sigma :** Comparaison instantanée avec la moyenne et l'écart-type de référence de l'espèce (ex: *Balanites aegyptiaca* $SLA = 9.9 \pm 0.6$). Si $|x - \mu| > 3\sigma$, l'application notifie l'opérateur et prépare l'étiquetage `SUSPECT_OUTLIER_3SIGMA` pour le backend.
* **Contrôle granulométrique du sol :** Somme argile + limon + sable obligatoirement comprise entre $98\%$ et $102\%$.

### 3.5. Module Enquêtes Socio-Écologiques & XLSForm
* **Enquêtes structurées (Modules M1 à M5) :**
  * **M1 (Ancrage) :** Géopoint automatique, terroir, profil (agriculteur, éleveur transhumant, agropasteur, tradithérapeute, coutumier, forestier, chercheur) et ancienneté.
  * **M2 (Free-listing) :** Saisie dynamique de 1 à 10 essences avec autocomplétion sur les noms scientifiques et vernaculaires (**Mooré**, **Dioula**, **Fulfuldé**). Calcul en direct de l'Indice de Saillance de Smith :
    $$S_i = \frac{L - r_i + 1}{L}$$
  * **M3 (Diagnostic sanitaire) :** Matrice de Likert standardisée de -2 à +2 (tendance perçue des populations, dépérissement des houppiers, attaques parasitaires).
  * **M4 (Phénologie) :** Suivi des perturbations saisonnières (décalages de floraison et fructification sur échelle -2 à +2).
  * **M5 (Pressions & RNA) :** Pression d'émondage (0 à 4), fréquence des feux, surpâturage et adoption des techniques de Régénération Naturelle Assistée (protection des rejets, taille de formation, aménagements Zaï/demi-lunes, mise en défens).
* **Fichier XLSForm Déployable :**
  * Fichier généré : [`public/forms/sahelfield_enquete_socioeco.xlsx`](public/forms/sahelfield_enquete_socioeco.xlsx)
  * Comprend les 3 feuilles requises : `survey`, `choices`, `settings`
  * Déployable directement sur **KoboToolbox** (`kf.kobotoolbox.org`) et **ODK Collect**.

### 3.6. Synchronisation Différée (POST /api/v1/sync/field-batch)
* Connexion directe à l'API SahelTraits-DB avec gestion des jetons JWT Bearer.
* File d'attente transactionnelle regroupant placettes, arbres, traits, semences, sols et enquêtes.
* Restitution complète des métriques renvoyées par le backend (nombre d'enregistrements ingérés, anomalies et nombre d'outliers 3-sigmas confirmés).

---

## 4. Guide d'Exécution & Commandes

### 4.1. Lancer l'application en mode développement
```bash
npm run dev
# L'application est accessible sur http://localhost:3000
```

### 4.2. Compiler pour la production
```bash
npm run build
```

### 4.3. Exécuter la suite de tests unitaires
```bash
npm test
```
*Vérifie automatiquement : les règles DHP, le blocage foliaire, la détection des 3-sigmas, le calcul de Smith, la texture des sols, la conformité XLSForm et le schéma du payload API.*

### 4.4. Régénérer le fichier XLSForm
```bash
npm run generate-xlsform
```

---

## 5. Déploiement KoboToolbox & ODK Collect
1. Télécharger le fichier [`sahelfield_enquete_socioeco.xlsx`](public/forms/sahelfield_enquete_socioeco.xlsx).
2. Se connecter sur la plateforme KoboToolbox (`kf.kobotoolbox.org`).
3. Créer un nouveau projet > Téléverser un fichier XLSForm > Sélectionner `sahelfield_enquete_socioeco.xlsx`.
4. Cliquer sur **Déployer**.
5. Flasher le QR-Code du projet depuis les tablettes de terrain exécutant **ODK Collect**. Les données recueillies peuvent ensuite être importées et synchronisées dans SahelTraits-DB.
