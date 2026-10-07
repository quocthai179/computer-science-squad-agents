---
exp_id: <exp-id>
question: <la question à laquelle répond l'expérience>
status: draft             # draft | approved | running | closed  (G3 : seul l'utilisateur passe à approved)
idea: <idea-id ou vide>
hypothesis: <hypothèse>
prediction: <sens et ampleur, p. ex. « B dépasse A d'au moins 2 points d'exactitude »>
confidence: <0-100>
kill_criteria: <si ... après ... alors arrêter>
primary_metric: <nom exactement tel qu'enregistré par runwrap, p. ex. val_acc>
metric_direction: max     # max | min
protected_files: []       # évaluation, métrique, données de test : le hook bloque les modifications quand status vaut approved/running
seeds: 3
budget_minutes_per_run: 30
budget_total_hours: 4
max_runs: 20
estimate_hours: <votre estimation du temps humain>
smoke_required: true
approved_at:
---

# <exp-id> : <question>

## Protocole d'évaluation

<données d'entraînement/validation/test, découpage, métriques principale et secondaires, mode de calcul>

## Lignes de base

- la plus simple (indépendante de l'entrée) : <p. ex. classe majoritaire, moyenne du jeu d'entraînement>
- standard (de l'article le plus proche) : <...>

## Plafond (ceiling)

<quelle variante « tricheuse » donne la borne supérieure : caractéristiques oracle, entraînement sur le test, modèle plus grand...>

## Hyperparamètres

| type | paramètre | valeur / plage |
|---|---|---|
| scientific (étudié) | | |
| nuisance (à régler pour une comparaison équitable) | | |
| fixed (fixé) | | |

## Liste de vérification « smoke » (Karpathy)

- [ ] regarder soi-même 20 échantillons et leurs étiquettes
- [ ] le squelette de bout en bout tourne avec la ligne de base la plus simple
- [ ] la perte à l'initialisation correspond à l'attendu (p. ex. ln(nombre de classes))
- [ ] on sait surapprendre un petit lot
- [ ] la ligne de base indépendante de l'entrée donne le chiffre attendu
- [ ] une graine fixée donne deux fois le même résultat

## Ordre de réduction des risques

> Steinhardt : l'étape qui apporte le plus d'information par unité de temps — la plus susceptible d'échouer et la moins chère — passe en premier.

1.
2.
3.

## Résultats attendus

> Esquissez avant l'exécution le tableau et les figures qui apparaîtront dans FINDINGS.md.

| variant | primary_metric (moyenne ± IC, 3 graines) |
|---|---|
| baseline | |
| method | |

## Menaces

- fuite de données (Kapoor & Narayanan) :
- ligne de base mal réglée :
- métrique mal alignée sur l'objectif :
