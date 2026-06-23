# CLAUDE.md — RunY (coaching running de Yannis)
> Lu en premier par Claude Code. Base = shell refondu de l'app Running, données = Yannis.
> 🎯 **Pour adapter l'app à Yannis : lire `docs/INDIVIDUALISATION.md`** (intake à lui faire passer, carte brique par brique, méthodo Strava pour le Cockpit).

## Identité
**App** : RunY — plan d'entraînement personnel de **Yannis**
**Repo** : entzmannloic-blip/RunY (GitHub Pages) · branche main
**Build** : 1 (refonte UX/UI portée depuis Running)

## Athlète
- **Yannis** · Saint-Étienne · FCmax 180 · 84 kg
- Cible marathon 3h45 (projeté ~3h39-3h43) · cible semi ~1h44
- **Courses 2026** : Trail des Sapins 24k/900m D+ (5 juil) · Semi-marathon de Lyon (4 oct) · Sainté Express 45 km (28 nov)

## ⭐ Pipeline (différent de Running : données en JSON, pas en gen.py)
```
src/data_src.json   ← LES DONNÉES DE YANNIS (plan, courses, zones…). C'est CE fichier qu'on édite pour mettre à jour.
src/gen.py          → lit data_src.json, calcule SAISON2026, écrit data.json
src/assemble.py     → data.json + css.txt + css_extra.txt + app.js + body.html → index.html
```
Build (tout dans /tmp/runy, avec css_extra/app/body du shell dans /tmp) :
```bash
python3 gen.py && python3 assemble.py && node --check app.js
# → /mnt/user-data/outputs/plan-entrainement.html  (renommer en index.html)
```
Push : commit atomique via Git Data API (GET ref → GET commit → POST tree → POST commit → PATCH ref). Le PAT de Loïc couvre RunY.

## Shell (générique, identique à Running)
`app.js`, `css.txt`, `css_extra.txt`, `body.html` = shell refondu commun. **Aucune donnée perso en dur** : le prénom vient de `PROFIL.prenom`. Navigation = Accueil · Séances · Coach · Cockpit · Courses (voir CLAUDE.md de Running pour le détail/pièges : Suivi dissous dans Cockpit, Courses garde l'id interne `palmares`).

## Pour mettre à jour le plan / les données de Yannis
Éditer `src/data_src.json` (clés : SBW = plan par semaine, RACES, SEMAINES, GEAR, ZONES_FC, ALLURES, DOSSIERS, PROFIL, HIST, RECORDS…), puis rebuild + push. Une séance loggée = remplir `realise:{statut:"fait",km,temps,allure,fc_moy,fc_max,...}` sur la séance concernée dans SBW.

## À individualiser (laissé en squelette) — détail complet dans docs/INDIVIDUALISATION.md
> ⚠️ Point P0 : le **Cockpit** (`_CK` dans app.js) affiche encore les données de **Loïc** — à régénérer depuis le Strava de Yannis (méthodo dans le guide).
- `PALMARES` = [] (courses passées à remplir)
- Chaussures `GEAR` et zones `ZONES_FC` : vérifier/ajuster pour Yannis
- `CHANGELOG` : historique propre à RunY

## ⚠️ Piège encodage (hérité de Running)
Ne jamais écrire un emoji en paire de surrogates `\uD83D\uDC4D` en Python (tronque + UnicodeEncodeError → fichier vidé). Caractère littéral ou `\U0001F44D`.
