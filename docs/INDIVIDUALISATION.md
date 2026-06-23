# INDIVIDUALISATION.md — Guide d'individualisation de RunY pour Yannis

> **À qui s'adresse ce document** : au développeur (ou à Claude) qui reprend RunY pour
> l'adapter complètement à Yannis. Il est écrit pour être auto-suffisant : tout ce qu'il
> faut savoir et aller chercher est ici. Lire **avant** de toucher au code.
>
> Compagnon : `CLAUDE.md` (pipeline & build), et le `CLAUDE.md` / `docs/TECHNICAL.md` du
> repo **Running** (architecture détaillée du shell, identique).

---

## 0. TL;DR — l'essentiel en 30 secondes

- RunY = **coquille générique** (le shell refondu de Running) **+ données de Yannis**. La coquille est neutre ; tout ce qui est personnel vit dans **`src/data_src.json`**… **sauf le Cockpit**.
- ⚠️ **POINT CHAUD (P0)** : les graphiques et l'historique d'activités du **Cockpit** sont encore **les données de Loïc**, codées en dur dans `src/app.js` (constante `_CK`). Tant qu'on ne les régénère pas depuis le Strava de Yannis, son Cockpit affiche les courses et la FC de Loïc. À traiter en priorité (exactitude **et** confidentialité).
- Avant de coder : faire passer à Yannis l'**intake du §2**. Plusieurs briques attendent ses réponses (palmarès, chaussures, records).
- Le reste (plan, profil, courses à venir, dossiers, historique hebdo) est **déjà le vrai Yannis**.

---

## 1. Ce qu'on a voulu faire (intention produit)

RunY est le pendant, pour **Yannis** (Saint-Étienne, FCmax 180, objectif marathon 3h45), de
l'app de coaching qu'on a construite pour Loïc. On a porté **l'intégralité de l'expérience
refondue** (design system, bottom bar, page Accueil, Coach contextuel, Cockpit analytique,
onglet Courses, couche mouvement) sur ses propres données.

Le principe directeur : **la coquille est universelle, les features ne « s'allument »
correctement que nourries des vraies données de l'athlète.** Une donnée vide ou en placeholder
ne casse pas l'app — la section reste juste muette ou générique jusqu'à ce qu'on la remplisse.

Ce que **chaque onglet doit raconter pour Yannis** (et donc ce qu'il faut individualiser) :

| Onglet | Ce qu'il doit montrer | Dépend de |
|--------|----------------------|-----------|
| **Accueil** | Sa prochaine séance, sa forme du jour, sa prochaine course, bilan du plan | `SBW`, `RACES`, `PROFIL`, séances loggées |
| **Séances** | Son plan semaine par semaine | `SBW`, `PHASES`, `SEMAINES` |
| **Coach** | Un mot contextuel (canicule / charge / affûtage) qui le nomme | `PROFIL`, séances loggées, `ACWR` |
| **Cockpit** | **SES** graphes (volume, ACWR, FC, allures…) + **SES** sorties récentes | ⚠️ `_CK` (app.js) — encore Loïc |
| **Courses** | **À venir** (ses 3 courses) + **Passées** (son palmarès) | `RACES` (ok) + `PALMARES` (vide) |

---

## 2. Questions à poser à Yannis AVANT de commencer (intake)

Ne pas individualiser « à l'aveugle ». Démarrer par cet entretien — chaque réponse débloque une brique.

**A. Strava (débloque le Cockpit, les chaussures, les records)**
1. Quel est son **Strava athlete ID** ? Accepte-t-il qu'on lise ses activités, ses streams et son matériel (`get_gear` demande une **approbation** côté app) ?
2. Sur quelle **période** veut-on les graphes du Cockpit (les 12 dernières semaines ? toute la saison 2026 ?).

**B. Palmarès — onglet Courses « Passées » (actuellement VIDE)**
3. Quelles **courses passées** veut-il afficher ? Pour chacune : nom, date, distance, D+, **temps**, allure, lieu, FC moy/max, météo, **classement** (général/catégorie), chaussures portées, et un **ressenti/bilan** en une phrase.

**C. Chaussures (actuellement 2 placeholders « Non renseigné »)**
4. Son **parc réel** : marque, modèle, kilométrage actuel, et l'usage de chaque paire (route / trail / séances). Idéalement le **gear_id Strava** de chacune (sinon on les retrouve via `get_gear`).

**D. Records & zones (actuellement estimés)**
5. Ses **records réels** : 5 km, 10 km, semi, marathon (chrono + date/contexte). Aujourd'hui certains sont « estimés depuis fractionnés » → à confirmer.
6. Confirmer **FCmax = 180** et ses **seuils de zones** (les zones actuelles en découlent ; à valider).

**E. Objectifs & spécificités**
7. Ses **cibles** par course (chrono visé) — on a 3h45 marathon / ~1h44 semi, à confirmer.
8. Des **points de vigilance** santé (on a noté « ischios fragiles » — à confirmer/compléter).

> Règle : si une réponse manque, **laisser la brique en squelette** (vide ou placeholder explicite) plutôt que d'inventer. L'app le tolère.

---

## 3. Carte d'individualisation (brique par brique)

Légende état : ✅ vrai Yannis · 🟡 partiel / estimé à confirmer · 🟥 placeholder ou vide · ⛔ encore Loïc

| Brique | Où ça vit | État | Quoi faire | Source | Prio |
|--------|-----------|------|-----------|--------|------|
| **Cockpit (graphes + sorties + streams)** | `src/app.js` → const `_CK` | ⛔ Loïc | **Régénérer entièrement** depuis le Strava de Yannis (voir §4) | Strava | **P0** |
| **PALMARES** (Courses passées) | `data_src.json` → `PALMARES` | 🟥 `[]` | Remplir avec ses courses passées (schéma §5) | Intake B + Strava | **P0** |
| **GEAR** (chaussures) | `data_src.json` → `GEAR` | 🟥 placeholders | Remplacer par ses paires réelles + km + gear_id | Intake C + `get_gear` | **P1** |
| **RECORDS** | `data_src.json` → `RECORDS` | 🟡 estimés | Confirmer 5/10/semi/marathon réels | Intake D | P1 |
| **MONTHLY** (km/dénivelé par mois) | `data_src.json` → `MONTHLY` | 🟡 partiel (Jan-Fév à 0) | Compléter les mois manquants | Strava / Intake | P2 |
| **ZONES_FC** | `data_src.json` → `ZONES_FC` | 🟡 dérivé FCmax 180 | Valider seuils avec lui | Intake D | P2 |
| **PROJ** (projection charge) | `data_src.json` → `PROJ` | 🟡 | Vérifier la cohérence avec son plan | — | P3 |
| **RACES** (Courses à venir) | `data_src.json` → `RACES` | ✅ | RAS (3 courses ok) — vérifier dates/dossiers | — | — |
| **DOSSIERS** (fiches de course) | `data_src.json` → `DOSSIERS` | ✅ | RAS (sapins/semi/saintexpress détaillés) | — | — |
| **SBW** (plan, 29 sem.) | `data_src.json` → `SBW` | ✅ | RAS — **se logge au fil de l'eau** (voir §4.2) | Strava (au fil) | — |
| **PHASES / SEMAINES** | `data_src.json` | ✅ | RAS | — | — |
| **HIST / HEATMAP** | `data_src.json` | ✅ | RAS (historique réel) | — | — |
| **RECORDS_PERF** | `data_src.json` | ✅ | RAS (efforts Strava réels) | — | — |
| **VIGILANCE** | `data_src.json` | ✅ | Confirmer « ischios fragiles » | Intake E | P3 |
| **PROFIL** | `data_src.json` → `PROFIL` | ✅ | RAS (prénom dynamique partout) | — | — |
| **CHANGELOG / MAJ** | `data_src.json` | ✅ | Incrémenter à chaque livraison | — | — |

---

## 4. Le gros morceau : reconstruire le Cockpit (`_CK`)

### 4.1 Pourquoi c'est particulier
`_CK` n'est **pas** dans `data_src.json` : c'est une constante **dans `src/app.js`** (≈ ligne 1470),
partagée avec le shell de Running. Elle contient **les chiffres de Loïc** :
- séries hebdomadaires : `VOL` (volume), `RE` (charge/relative effort), `ACWR`, `DPLUS`, `Z2`, `DC` (décrassage), `PACE` (allures EF/AM/séance), `FCZ` (répartition zones FC), `CAD` (cadence), chacune déclinée en fenêtres 2 / 4 / 8 / 12 semaines ;
- `RUNS` : la liste des sorties récentes (titre, date, km, allure, FC, D+, calories…) → **ce sont les courses de Loïc** (ex. « Trail des Gypaètes ») ;
- `STREAMS` : les courbes de FC seconde par seconde de ces sorties → **la FC de Loïc**.

**Tant que ce n'est pas refait, le Cockpit de Yannis montre l'entraînement de Loïc.** C'est le point P0.

### 4.2 Méthodologie de régénération (avec les outils Strava)
Les outils Strava sont **deferred** : faire `tool_search("strava activities")` puis `tool_search("strava gear")` pour les charger à chaque session.

1. **Lister ses activités** sur la fenêtre voulue :
   `Strava:list_activities(first, range_start, range_end)` → id, date, distance, temps, allure, D+, cadence, gear_id.
2. Pour chaque activité utile : `Strava:get_activity_performance(activity_id)` → FC moy/max, laps, répartition zones.
3. Pour les sorties à streams : `Strava:get_activity_streams(activity_id, ["heartrate","velocity_smooth"...])` → courbes (pour `STREAMS`).
4. **Agréger par semaine** pour reconstruire les séries `VOL/RE/ACWR/DPLUS/Z2/DC/PACE/FCZ/CAD` (fenêtres 2/4/8/12). Reproduire **exactement la même structure** que `_CK` (cf. §4.3) pour que le rendu marche sans toucher au reste.
5. **Recommandation d'archi** (propre & pérenne) : sortir `_CK` du shell pour le mettre dans les données.
   - Ajouter une clé `CK` dans `data_src.json` (= l'objet régénéré de Yannis).
   - Dans `assemble.py`, l'émettre comme global (ajouter `("CK","CK")` à la liste).
   - Dans `app.js`, remplacer `const _CK={...}` par `const _CK=(typeof CK!=='undefined')?CK:{/* fallback */};`.
   - Avantage : le shell reste commun aux deux apps, et chaque app porte SON Cockpit dans SES données. (À défaut, solution rapide : remplacer en dur le bloc `_CK` dans **le `app.js` de RunY uniquement**.)

### 4.3 Forme de `_CK` (à reproduire à l'identique)
```js
_CK = {
  VOL:  { 2:{w:['S24','S25'], p:[plan...], a:[réalisé...]}, 4:{...}, 8:{...}, 12:{...} },
  RE:   { 2:{w:[...], v:[...]}, ... },     // charge
  ACWR: { 2:{w:[...], v:[...]}, ... },     // ratio aigu/chronique
  DPLUS:{ ... }, Z2:{ ... }, DC:{ ... }, CAD:{ ... },
  PACE: { 2:{w:[...], ef:[...], am:[...], se:[...]}, ... },  // allures, sec/km, null si absent
  FCZ:  { 2:[['Z1','#16a34a',10],['Z2',...],['Z3',...],['Z4+',...]], ... }, // % par zone
  RUNS: [ {id, title, date, type:'#hex', km, al, re, fcm, fcx, cad, dp, cal, hasStreams}, ... ],
  STREAMS: { '<activityId>': {hr:[...], /* + autres streams */}, ... }
}
```

### 4.4 Logger une séance au fil de l'eau (alimente Accueil, forme, SAISON2026)
Quand Yannis fait une séance, on remplit son `realise` dans `SBW` (même méthode que pour Loïc) :
```json
"realise": { "statut":"fait", "km":11.26, "temps":"1h06", "allure":"5:53/km",
             "fc_moy":148, "fc_max":169, "rpe_ressenti":3, "dplus":43,
             "commentaire":"…", "revue":"<strong>mot du coach…</strong>" }
```
Puis : récupérer le km chaussure via `get_gear`, mettre à jour `GEAR`, rebuild, push.
`SAISON2026` (sorties/km/D+ de l'année) est **recalculé automatiquement** par `gen.py` à partir des `realise` — rien à saisir.

---

## 5. Schémas de données (référence)

**RACES** (à venir) :
```json
{ "nom":"Trail des Sapins 24k / 900 m D+", "date":"2026-07-05", "dossier":"sapins" }
```
**PALMARES** (passées — à remplir) :
```json
{ "nom":"…", "date":"2026-05-01", "type":"trail|route", "distance":"21,1 km", "dplus":350,
  "temps":"1:44:00", "allure":"4:55/km", "lieu":"Ville (dép)", "fc_moy":162, "fc_max":178,
  "meteo":"12°C couvert", "classement_gen":"45e", "classement_cat":"8e M0",
  "chaussures":"Modèle", "bilan":"Une phrase de ressenti.", "accent":"#0d9488" }
```
**GEAR** (chaussures) :
```json
{ "marque":"ASICS", "modele":"Novablast 5", "km":312, "gear_id":"g1234567" }
```
**DOSSIERS** (fiche course, clé = valeur de `RACES.dossier`) : objet riche déjà rempli pour les 3 courses — s'en inspirer pour la structure si on en ajoute.

---

## 6. Méthodologie technique (pipeline, build, push)

**Pipeline** (détail dans `CLAUDE.md`) :
```
src/data_src.json  →  gen.py  →  data.json  →  assemble.py  →  index.html
```
Yannis met à jour ses données en éditant **`src/data_src.json`** (le Cockpit, lui, est dans `app.js` tant que la reco §4.2 n'est pas appliquée).

**Build** :
```bash
python3 gen.py && python3 assemble.py && node --check app.js   # node --check BLOQUANT
```
**Push** : commit atomique via Git Data API (GET ref → GET commit → POST tree → POST commit → PATCH ref).

⚠️ **Token** : le PAT de Running ne couvre **pas** RunY en écriture. Il faut un token avec
**Contents: write** sur `entzmannloic-blip/RunY` (ou étendre le fine-grained existant à ce repo).

⚠️ **Piège encodage** (hérité) : ne jamais écrire un emoji en **paire de surrogates**
(`\uD83D\uDC4D`) en Python : `open('w')` tronque puis `.write()` lève `UnicodeEncodeError`
→ fichier vidé. Utiliser le caractère littéral ou `\U0001F44D`. Récup : re-`curl` le dernier
build poussé depuis `raw.githubusercontent.com`.

⚠️ **Outils Strava deferred** : `tool_search` pour les charger à chaque session. `get_gear`
peut exiger une **approbation** côté app de Yannis.

---

## 7. État actuel précis (audit au build 1)

```
PROFIL        ✅  Yannis · Saint-Étienne · FCmax 180 · cibles 3h45 / ~1h44
RACES         ✅  3 courses à venir (Sapins 5/7 · Semi Lyon 4/10 · Sainté Express 28/11)
DOSSIERS      ✅  3 fiches détaillées
PHASES        ✅  7 phases · SEMAINES ✅ · SBW ✅ 29 sem. / 133 séances (1 loggée)
HIST          ✅  14 semaines réelles · HEATMAP ✅ 38 jours · RECORDS_PERF ✅ 5 efforts Strava
VIGILANCE     🟡  « ischios fragiles » (à confirmer)
PROJ          🟡  projection 6240→6300 (à vérifier)
ZONES_FC      🟡  dérivées FCmax 180 (à valider)
RECORDS       🟡  3, dont des estimés (« ~24:00 estimé »)
MONTHLY       🟡  6 mois, Jan-Fév à 0 (à compléter)
GEAR          🟥  2 paires « Non renseigné » (placeholder)
PALMARES      🟥  [] vide → onglet Courses « Passées » muet
_CK (Cockpit) ⛔  données de LOÏC dans app.js (graphes + sorties + streams)
```

**Ordre d'attaque conseillé** : intake §2 → `_CK` (P0) → `PALMARES` (P0) → `GEAR` (P1) →
`RECORDS` (P1) → `MONTHLY`/`ZONES_FC` (P2) → finitions.
