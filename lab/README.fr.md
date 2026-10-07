# Research Squad (`lab`)

[English](README.md) · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · **Français** · [日本語](README.ja.md)

Un plugin Claude Code pour la recherche en IA/ML : un **Lead** (la session principale, pilotée par les skills `/lab:*`) coordonne **7 sous-agents** et utilise le dossier `research/` de votre dépôt comme cahier de laboratoire partagé. Les agents s'occupent du débit (lire, exécuter, vérifier, rédiger un brouillon) ; vous gardez le goût et les décisions, à cinq points de contrôle, G1 à G5.

Ce que le plugin apporte par rapport à une simple recherche « deep research » ponctuelle :

1. **Un registre des runs** et la règle « tout chiffre remonte à un run », appliquée par des scripts et un hook, pas par des prompts.
2. **`skeptic`**, un relecteur indépendant : il ne reçoit que des chemins d'artefacts, jamais le raisonnement de l'auteur.
3. **Une boucle d'apprentissage** qui mesure la calibration entre prédictions et résultats, et entre durées estimées et durées réelles.

Il fonctionne en **cinq langues** : English (par défaut), Tiếng Việt, 中文, Français, 日本語. Voir [Langue](#langue).

## Installation

Prérequis : Claude Code (v2.1.271 ou plus pour le sélecteur de langue ; les évaluations demandent v2.1.269+), `python3` ≥ 3.10 dans le `PATH`. Les scripts n'utilisent que la bibliothèque standard ; `pdftotext` (poppler) est facultatif pour obtenir le texte des PDF.

Depuis GitHub :

```text
/plugin marketplace add quocthai179/computer-science-squad-agents
/plugin install lab@computer-science-squad-agents
```

Développement local :

```bash
claude --plugin-dir ./lab        # modifiez les fichiers puis /reload-plugins
claude plugin validate ./lab
```

## Langue

| Code | Langue | Remarques |
|---|---|---|
| `en` | English | par défaut |
| `vi` | Tiếng Việt | termes techniques anglais conservés |
| `zh` | 中文 | caractères simplifiés |
| `fr` | Français | registre soutenu (vous) |
| `ja` | 日本語 | forme polie (です・ます) |

**Ce qui suit la langue :** tout ce qui est écrit dans `research/` (notes, fiches, plans, revues, rapports) et les modèles de départ (`templates/<lang>/`), ainsi que les réponses des agents. **Ce qui ne change jamais :** les clés du frontmatter et leurs valeurs fixes (`status: approved`, `verdict: reject`), les champs JSONL, les noms de fichiers, les identifiants et les ancres `[@paper-id, loc]` / `[run:id]`, afin que les scripts fonctionnent dans toutes les langues. Les instructions, les playbooks et la sortie des scripts sont en anglais ; le Lead vous les relaie dans votre langue.

**Choisir la langue**, la première correspondance l'emporte :

1. `language:` dans `research/PROJECT.md`. `/lab:setup` l'écrit selon la langue dans laquelle vous écrivez. Pour la changer plus tard : `python3 <plugin>/scripts/lang.py set fr`.
2. L'option du plugin (votre valeur personnelle par défaut pour les nouveaux projets) :
   ```bash
   claude plugin configure lab@computer-science-squad-agents --values-stdin <<< '{"language":"fr"}'
   ```
   ou `/plugin configure lab@computer-science-squad-agents` dans Claude Code. Tant qu'aucune valeur n'est enregistrée, l'option est « non définie » et l'anglais s'applique.
3. English.

Les réponses dans le chat suivent la langue dans laquelle vous écrivez, quelle que soit la langue du projet. Des demandes naturelles dans les cinq langues déclenchent le bon skill (« khảo sát… », « 文献综述… », « revue de littérature… », « 文献調査… »).

## Commandes

| Vous avez besoin de | Commande | Résultat |
|---|---|---|
| Démarrer un projet (G1) | `/lab:setup [titre]` | `research/`, `PROJECT.md` (note de cadrage Heilmeier) |
| Prendre rapidement un sujet en main | `/lab:survey <sujet> [--quick]` | une revue sourcée, les lacunes, les contradictions entre articles |
| Comprendre un article en profondeur | `/lab:read-paper <id arXiv \| URL \| fichier> [--deep]` | une fiche d'article, l'explain-back |
| Critiquer n'importe quel artefact | `/lab:critique <chemin>` | une revue indépendante |
| Trouver des idées (G2) | `/lab:ideate [thème]` | des fiches d'idées passées par le protocole de nouveauté |
| Concevoir une expérience (G3) | `/lab:design-exp <idea-id \| question>` | `PLAN.md` |
| Lancer une expérience | `/lab:run-exp <exp-id>` (uniquement quand vous le tapez) | le registre des runs |
| Analyser | `/lab:analyze <exp-id>` | `FINDINGS.md`, tableaux, figures |
| Rédiger (G4, G5) | `/lab:write-up <type> [slug]` | `claims.md` → `draft.md` → `final.md` |
| Bilan hebdomadaire | `/lab:retro [jours]` | une rétrospective, `LESSONS.md`, calibration |
| Que faire ensuite | `/lab:next` | une seule chose, et pourquoi |

Chaque skill a un plan B : si les sous-agents ne peuvent pas être appelés, le Lead travaille en séquence avec le même playbook et vous le dit.

## L'équipe

| Agent | Rôle | Outils | Modèle | Écrit dans |
|---|---|---|---|---|
| `scout` | éclaireur de littérature, 1re passe | Read, Glob, Grep, WebSearch, WebFetch, Write | sonnet | `surveys/<slug>/scout-*.jsonl` |
| `reader` | 2e passe sur le texte intégral | Read, Glob, Grep, Write | sonnet | `papers/cards/` |
| `writer` | le seul rédacteur | Read, Glob, Grep, Write, Edit | inherit | `surveys/`, `reports/` |
| `skeptic` | critique indépendant | Read, Glob, Grep, WebSearch, WebFetch, Write | opus | `reviews/` |
| `experimenter` | ingénieur d'expériences | Read, Glob, Grep, Edit, Write, Bash | sonnet | code, `experiments/<id>/` |
| `analyst` | analyse des résultats | Read, Glob, Grep, Bash, Write | sonnet | `FINDINGS.md`, tableaux, figures |
| `ideator` | générateur d'hypothèses | Read, Glob, Grep, Write | opus | `ideas/cards/` |

Aucun agent n'a l'outil `Agent`, la chaîne d'appels reste donc plate. `scout` et `reader` lisent du contenu non fiable : ils n'ont ni `Bash` ni `Edit`. `analyst` n'a pas `Edit` et ne peut donc pas modifier le code d'entraînement. Tous les échanges passent par des fichiers selon le contrat `TASK BRIEF` / `RECEIPT` (`playbooks/handoff.md`).

## Espace de travail

```text
research/
├── PROJECT.md          # note de cadrage Heilmeier, stage, profil de calcul, langue
├── notebook/           # AAAA-MM-JJ.md, ajout uniquement (scripts/notebook.py)
├── decisions.md        # décisions aux points de contrôle
├── papers/             # index.jsonl, refs.bib, cards/, raw/ (ignoré par git)
├── surveys/<slug>/     # angles.md, scout-*.jsonl, evidence.jsonl, gaps.md, survey.md
├── ideas/              # backlog.md, cards/
├── experiments/<id>/   # PLAN.md, runs.jsonl, runs/ (ignoré par git), FINDINGS.md, tables/, figures/
├── reports/<slug>/     # claims.md, draft.md, final.md
├── reviews/
└── lessons/            # LESSONS.md (≤ 50 lignes), calibration.jsonl, squad-issues.md, retros/
```

`/lab:setup` ajoute au `CLAUDE.md` du dépôt un bloc de règles communes (entre `<!-- lab:begin -->` et `<!-- lab:end -->`), car les sous-agents chargent `CLAUDE.md`.

## Garde-fous et leur mise en application

| Règle | Appliquée par |
|---|---|
| Aucun run si `PLAN.md` n'a pas de `prediction` ou de `kill_criteria` | `runwrap.py` refuse (exit 3) |
| Seuls les plans approuvés s'exécutent (G3) | `runwrap.py` exige `status: approved` ou `running` |
| Un smoke avant tout vrai run | `runwrap.py` exige un smoke `ok` |
| Budget de runs | `runwrap.py` compare à `max_runs` ; délai d'expiration selon `budget_minutes_per_run` |
| 3 tentatives de correction au plus | `runwrap.py` refuse après 3 runs échoués d'affilée, sauf si vous autorisez `--after-review` |
| Pas de modification manuelle du registre, de `tables/`, de `figures/` | hook `PreToolUse` (`scripts/guard_generated.py`) |
| Pas de changement d'évaluation, de métrique ou de données de test en cours d'exécution | le hook bloque les `protected_files` d'un plan `approved`/`running` |
| Les chiffres du texte doivent figurer dans un tableau, le registre ou une fiche | `lint_report.py` |
| Pas de marqueurs à compléter dans le texte final | `lint_report.py` |
| Pas de « novateur », « le premier », « SOTA » sans `closest_prior_work` vérifié | `lint_report.py`, dans les cinq langues |
| Les citations doivent se résoudre | `cite_check.py` (arXiv, doi.org, Semantic Scholar ; `--offline` ne vérifie qu'en local) |
| 2 tours de revue au plus, 1 tour de recherche supplémentaire, 5 scouts | dans les skills |

## Comment un script d'entraînement rapporte ses métriques

Chaque run passe par `runwrap.py` :

```bash
python3 <plugin>/scripts/runwrap.py --exp e001-ls --name baseline --tag baseline --seed 0 -- python train.py
```

Le script d'entraînement lit sa graine dans `$LAB_SEED` et rapporte ses métriques de l'une de deux façons : afficher une ligne `LAB_METRIC test_acc=0.8312`, ou écrire du JSON dans `$LAB_METRICS_FILE`. Le registre enregistre le SHA git, un indicateur « dirty », le hash de la configuration, la graine, la durée, le code de sortie et les métriques.

## Scripts

| Script | Rôle |
|---|---|
| `init_workspace.py` | crée `research/` (idempotent, `--lang`), ajoute le bloc de règles à `CLAUDE.md` |
| `lang.py` | affiche ou change la langue de l'espace de travail |
| `paper_fetch.py` | id arXiv, URL ou fichier → métadonnées, LaTeX aplati ou PDF, `index.jsonl`, `refs.bib` |
| `paper_index.py` | fusionne et dédoublonne la sortie des scouts ; liste ; modifie des champs |
| `runwrap.py` | enveloppe une commande d'entraînement, tient les points de contrôle, écrit le registre |
| `ledger.py` | liste les runs, génère des tableaux Markdown et des figures SVG, affiche le budget |
| `stats.py` | moyenne, écart type, IC t à 95 %, comparaison appariée par graine avec IC bootstrap |
| `cite_check.py` | vérifie les citations `[@id, loc]`, `\cite{}`, arXiv, DOI, `[run:id]` |
| `lint_report.py` | marqueurs à compléter, chiffres sans source, affirmations de nouveauté non vérifiées (en, vi, zh, fr, ja) |
| `calibration.py` | prédictions et résultats ; estimations et durées réelles ; score de Brier |
| `retro_digest.py` | la synthèse de la semaine pour `/lab:retro` et l'état pour `/lab:next` |
| `notebook.py` | ajoute au cahier |
| `guard_generated.py` | hook qui bloque les modifications manuelles des fichiers générés et protégés |

## Démonstration

Captures d'écran de vrais runs dans Claude Code (une session en vietnamien, donc les réponses sont en vietnamien). Les entrées sont des fixtures des évaluations ; vous pouvez les rejouer ([comment](../docs/screenshots/capture/README.md)).

**`/lab:critique` : revue indépendante.** Le Lead ne donne à `lab:skeptic` que des chemins, aucun raisonnement. Ce rapport d'expérience contient cinq défauts plantés, et le skeptic les nomme tous, avec les numéros de ligne.

![lab:skeptic relit FINDINGS.md](../docs/screenshots/critique-running.png)

![Verdict reject avec cinq problèmes bloquants](../docs/screenshots/critique-verdict.png)

**`/lab:read-paper` : lecture approfondie et explain-back.** `lab:reader` lit le texte intégral et écrit une fiche ; le Lead rend un résumé et trois questions pour tester votre propre compréhension. L'article est synthétique, écrit pour les évaluations, et le reader repère les preuves fragiles qui y ont été plantées (réglage inégal, best of 3 seeds).

![lab:reader tourne en arrière-plan](../docs/screenshots/read-running.png)

![La fiche d'article, le résumé et les questions d'explain-back](../docs/screenshots/read-card.png)

**Des garde-fous dans les scripts, pas dans les prompts.** `runwrap.py` refuse d'exécuter un plan non approuvé (G3) et refuse les vrais runs avant un smoke ; chaque run entre dans le registre avec son SHA git.

![runwrap refuse, puis un smoke et 6 runs principaux](../docs/screenshots/guardrails.png)

**Statistiques appariées par graine.** Sur une expérience jouet (régression logistique sur données synthétiques), le label smoothing ne change rien, et `stats.py compare` le dit parce que l'IC à 95 % de la différence contient 0.

![stats.py compare : l'IC contient 0](../docs/screenshots/stats.png)

## Tests

Tests unitaires des scripts (à la racine du dépôt) :

```bash
pip install pytest
pytest tests
```

Ils vérifient aussi que les cinq langues ont les 13 modèles avec les mêmes clés de frontmatter, le même nombre de titres et les mêmes listes de contrôle, et que le linter fonctionne sur des textes en anglais, vietnamien, chinois, français et japonais.

Évaluations du plugin (`evals/`, 9 cas). Chaque run est un vrai appel de modèle décompté de votre usage. Les cas construisent leurs fixtures avec `scaffold.sh` et demandent donc `--scaffold` :

```bash
# itération rapide : un run, sans branche de référence
claude plugin eval ./lab --scaffold --allow-tools Bash Write Edit Agent --runs 1 --ablation none
# confirmation : trois runs, avec la branche sans plugin pour voir le Δ
claude plugin eval ./lab --scaffold --allow-tools Bash Write Edit Agent
```

| Cas | Vérifie |
|---|---|
| `read-paper-card` | demande en anglais → fiche complète, citations localisées, explain-back |
| `critique-planted-bugs` | `skeptic` nomme les cinq défauts plantés |
| `design-exp-plan` | `PLAN.md` complet, prédiction enregistrée, plan non auto-approuvé (G3) |
| `no-trigger-simple-question` | une simple question factuelle n'invoque aucun skill |
| `next-step-analyze` | `/lab:next` recommande d'analyser les runs terminés |
| `setup-fr` | demande en français → espace de travail en français, `language: fr` |
| `read-paper-ja` | demande en japonais → fiche et réponse en japonais |
| `critique-zh` | demande en chinois → réponse en chinois nommant les cinq défauts |
| `read-paper-vi` | demande en vietnamien → fiche et explain-back en vietnamien |

Une revue de littérature a besoin du web et n'est pas déterministe ; elle n'a donc pas de cas d'évaluation. Évaluez-la avec des golden tasks.

## Choix par défaut

1. Surface principale : Claude Code. Les sous-agents et les hooks dans l'application Claude sont **non vérifiés**.
2. Nom et préfixe : `lab`.
3. Espace de travail : `research/` dans chaque dépôt.
4. Langue des artefacts : anglais par défaut ; `vi`, `zh`, `fr`, `ja` pris en charge ; un brouillon d'article peut être dans une autre langue que le projet.
5. Profil de calcul : renseigné pendant `/lab:setup` ; les budgets des plans en découlent.
6. `skeptic` utilise `opus` ; pas encore de seconde famille de modèles comme relecteur.

## Limites

- Coût en tokens : une revue complète lance 4 à 5 scouts et 5 à 8 readers. Utilisez `--quick` pour les questions étroites.
- `skeptic` appartient à la même famille de modèles que l'auteur et peut partager ses angles morts ; vous devez quand même lire le texte final.
- `cite_check.py` et `paper_fetch.py` ont besoin d'accéder à `export.arxiv.org`, `arxiv.org`, `doi.org` et `api.semanticscholar.org`.
- Les hooks appellent `python3` ; sous Windows, `python3` doit être dans le `PATH`.
- La qualité des textes dans les langues autres que l'anglais dépend du modèle ; la structure, les ancres et les chiffres sont indépendants de la langue et vérifiés par des scripts.
- Accélérer les parties mécaniques, pas la compréhension : c'est pourquoi `/lab:read-paper` comporte un explain-back et `/lab:write-up` se termine par G5.
