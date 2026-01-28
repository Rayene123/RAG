"""
Test simple: Donner juste du texte au Risk Agent
"""
import sys
import os

# Ajouter le répertoire du projet au path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from agents.risk_agent import RiskAgent

# Créer l'agent
risk_agent = RiskAgent()

# UTILISATION SIMPLE: Juste du texte!
print("="*80)
print("TEST RISK AGENT - INPUT TEXTE SIMPLE")
print("="*80)

query = "35-year-old client, mid-level job, $60k income, owns car, requesting $150k loan"
print(f"\n📝 Votre requête: {query}\n")

# Analyse automatique
result = risk_agent.analyze_from_text(query)

# Afficher les résultats
print("\n" + "="*80)
print("RÉSULTATS")
print("="*80)

print(f"\n📊 Contexte:")
print(f"   Cas similaires: {result['similar_cases_count']}")
print(f"   Similarité moyenne: {result['avg_similarity_score']:.4f}")
print(f"   Taux de défaut historique: {result['historical_default_rate']:.2%}")

print("\n" + "-"*80)
print("ANALYSE CONTREFACTUELLE:")
print("-"*80)
print(result['raw_output'])

print("\n" + "="*80)
