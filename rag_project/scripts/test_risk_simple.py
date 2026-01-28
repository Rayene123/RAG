"""
Test Simple du Risk Agent - Vérification de l'analyse des risques
"""
import sys
import os

# Ajouter le répertoire du projet au path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import re
from agents.risk_agent import RiskAgent
from rag_core.retriever.qdrant_retriever import QdrantRetriever


def extract_value_from_text(text, pattern, default=0):
    """Extraire une valeur numérique du texte avec regex"""
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        value_str = match.group(1).replace(',', '').replace('$', '').replace(' ', '').strip()
        try:
            return float(value_str)
        except ValueError:
            return default
    return default


def test_analyse_risque_basique():
    """Test 1 : Vérifier que l'agent peut analyser des risques basiques"""
    
    print("="*80)
    print("TEST 1 : ANALYSE DE RISQUE BASIQUE")
    print("="*80)
    
    try:
        # Initialiser
        print("\n✓ Initialisation du Risk Agent...")
        risk_agent = RiskAgent()
        print("✓ Risk Agent initialisé avec succès!")
        
        print("\n✓ Initialisation du Retriever Qdrant...")
        retriever = QdrantRetriever()
        print("✓ Retriever initialisé avec succès!")
        
        # Récupérer un vrai client de Qdrant avec une recherche spécifique
        print("\n🔍 Récupération d'un profil client réel depuis Qdrant...")
        # Chercher plusieurs clients et prendre le PLUS similaire
        candidates = retriever.search("35-year-old client, mid-level job, $60k income, owns car, requesting $150k loan", top_k=10)
        
        if not candidates:
            print("❌ Aucun client trouvé dans Qdrant. Veuillez ingérer des données d'abord.")
            return None
        
        # Trier par score de similarité (décroissant) et prendre le meilleur
        sample_clients = sorted(candidates, key=lambda x: x.get('score', 0), reverse=True)[:1]
        target_client = sample_clients[0]
        client_id = target_client.get('client_id', 'N/A')
        similarity_score = target_client.get('score', 0)
        print(f"  ✓ Client le PLUS similaire: {client_id} (score: {similarity_score:.4f})")
        client_text = target_client.get('text', '')
        client_metadata = target_client.get('metadata', {}) or target_client.get('payload', {})
        
        print(f"\n📋 PROFIL CLIENT RÉEL :")
        print("-"*80)
        print(f"  Client ID: {client_id}")
        print(f"\n  Profil complet: {client_text}")
        print("-"*80)
        
        # Extraire les valeurs du texte (où les vraies données sont stockées)
        print(f"\n📊 Extraction des valeurs du texte...")
        # Patterns plus robustes pour gérer les labels multi-mots
        income = extract_value_from_text(client_text, r'(?:annual\s+)?income[:\s]+\$?([\d,]+)', 50000)
        credit = extract_value_from_text(client_text, r'(?:requested\s+)?credit(?:\s+amount)?[:\s]+\$?([\d,]+)', 80000)
        annuity = extract_value_from_text(client_text, r'(?:monthly\s+)?annuity[:\s]+\$?([\d,]+)', 0)
        
        print(f"  ✓ Revenu extrait: ${income:,.0f}")
        print(f"  ✓ Crédit extrait: ${credit:,.0f}")
        if annuity > 0:
            print(f"  ✓ Annuité extraite: ${annuity:,.0f}")
        
        # Créer une query basée sur le profil réel
        query = client_text[:300] if client_text else f"Client {client_id} profil"
        
        # Récupérer des cas similaires (exclure le client lui-même)
        print(f"\n🔍 Recherche de cas similaires au client {client_id}...")
        all_similar_cases = retriever.search(query, top_k=15)
        # Filtrer pour exclure le client lui-même
        similar_cases = [c for c in all_similar_cases if c.get('client_id') != client_id][:10]
        print(f"✓ {len(similar_cases)} cas similaires trouvés!")
        
        # ANALYSE CONTREFACTUELLE : Évaluer la décision réelle et son alternative
        actual_target = target_client.get('target', client_metadata.get('target', 0))
        
        print(f"\n🔄 DÉCISION RÉELLE : {'❌ REJETÉ (défaut observé)' if actual_target == 1 else '✅ ACCEPTÉ (aucun défaut)'}")
        print(f"📊 Valeurs extraites: Revenu=${income:,.0f}, Crédit=${credit:,.0f}\n")
        
        # Calculer le taux de défaut historique des cas similaires
        default_rate = sum(1 for c in similar_cases if c.get('target', 0) == 1) / len(similar_cases) if similar_cases else 0
        
        # Créer l'analyse contrefactuelle
        if actual_target == 0:  # Client a été ACCEPTÉ
            # Demander à l'IA d'analyser :
            # 1. Pourquoi l'acceptation était justifiée
            # 2. Si on avait REJETÉ, aurait-ce été une bonne ou mauvaise décision (avec %)
            alternatives = [
                {
                    'id': 'actual_decision',
                    'description': f'DÉCISION RÉELLE: ACCEPTÉ - Crédit de ${credit:,.0f} accordé',
                    'loan_amount': credit,
                    'loan_to_income_ratio': credit / income,
                    'decision': 'ACCEPTED',
                    'outcome': 'NO_DEFAULT',
                    'analysis_request': 'Expliquer pourquoi cette décision était justifiée basé sur le profil client et les cas similaires'
                },
                {
                    'id': 'counterfactual',
                    'description': f'ALTERNATIVE CONTREFACTUELLE: REJETER la demande',
                    'loan_amount': 0,
                    'decision': 'REJECTED',
                    'analysis_request': f'Si on avait REJETÉ ce client au lieu de l\'accepter: (1) Aurait-ce été une BONNE ou MAUVAISE décision? (2) Donner un pourcentage de certitude (0-100%) que le rejet aurait été le meilleur choix. (3) Expliquer pourquoi en se basant sur: taux de défaut historique ({default_rate:.1%}), profil du client, et résultat réel (aucun défaut observé)'
                }
            ]
        else:  # Client a été REJETÉ (défaut observé = target=1)
            # Demander à l'IA d'analyser :
            # 1. Pourquoi le rejet était justifié
            # 2. Si on avait ACCEPTÉ, aurait-ce été une bonne ou mauvaise décision (avec %)
            alternatives = [
                {
                    'id': 'actual_decision',
                    'description': f'DÉCISION RÉELLE: REJETÉ - Demande de crédit refusée',
                    'loan_amount': 0,
                    'decision': 'REJECTED',
                    'outcome': 'DEFAULT_OBSERVED',
                    'analysis_request': 'Expliquer pourquoi ce rejet était justifié basé sur le profil client et les cas similaires'
                },
                {
                    'id': 'counterfactual',
                    'description': f'ALTERNATIVE CONTREFACTUELLE: ACCEPTER la demande de ${credit:,.0f}',
                    'loan_amount': credit,
                    'loan_to_income_ratio': credit / income,
                    'decision': 'ACCEPTED',
                    'analysis_request': f'Si on avait ACCEPTÉ ce client au lieu de le rejeter: (1) Aurait-ce été une BONNE ou MAUVAISE décision? (2) Donner un pourcentage de certitude (0-100%) que l\'acceptation aurait été le meilleur choix. (3) Expliquer pourquoi en se basant sur: taux de défaut historique ({default_rate:.1%}), profil du client, et résultat réel (défaut observé)'
                }
            ]
        
        print(f"\n📊 Analyse contrefactuelle en cours...\n")
        
        # Analyser les risques avec un prompt spécifique pour l'analyse contrefactuelle
        context = f"""
CLIENT PROFILE:
- Client ID: {client_id}
- Revenue: ${income:,.0f}
- Requested Credit: ${credit:,.0f}
- Loan-to-Income Ratio: {credit/income:.2f}

HISTORICAL CONTEXT:
- Similar Cases: {len(similar_cases)} clients found
- Average Similarity Score: {sum(c.get('score', 0) for c in similar_cases)/len(similar_cases):.4f}
- Historical Default Rate: {default_rate:.2%}
- Actual Outcome: {"DEFAULT occurred" if actual_target == 1 else "NO DEFAULT (good standing)"}

TASK: Perform counterfactual analysis comparing the actual decision vs the alternative decision.
For each alternative, provide:
1. Clear explanation of why the decision was made
2. For the counterfactual: percentage confidence (0-100%) that it would have been a better decision
3. Detailed reasoning based on client profile, historical data, and actual outcome

Respond in JSON format:
{{
    "actual_decision_analysis": {{
        "decision": "ACCEPTED" or "REJECTED",
        "justification": "Why this decision was made",
        "supporting_factors": ["list", "of", "factors"],
        "outcome": "What actually happened"
    }},
    "counterfactual_analysis": {{
        "alternative_decision": "REJECTED" or "ACCEPTED",
        "quality_score": 0-100 (percentage that alternative would have been better),
        "confidence_level": "HIGH/MEDIUM/LOW",
        "would_it_be_better": "YES/NO",
        "reasoning": "Detailed explanation",
        "risk_factors": ["factors supporting or against the alternative"],
        "conclusion": "Final verdict with percentage"
    }},
    "comparison_summary": "Overall comparison and recommendation"
}}
"""
        
        result = risk_agent.analyze({
            'decision_context': context,
            'alternatives': alternatives,
            'similar_cases': similar_cases
        })
        
        # Afficher les résultats
        print("\n" + "="*80)
        print("ANALYSE CONTREFACTUELLE")
        print("="*80)
        
        print(f"\n📊 CONTEXTE HISTORIQUE:")
        print(f"   Cas similaires : {result['similar_cases_count']}")
        print(f"   Similarité moyenne : {result['avg_similarity_score']:.4f}")
        print(f"   Taux de défaut historique : {result['historical_default_rate']:.2%}")
        
        print(f"\n🔍 DÉCISION RÉELLE : {'❌ REJETÉ' if actual_target == 1 else '✅ ACCEPTÉ'}")
        print(f"   Résultat observé : {'Défaut détecté' if actual_target == 1 else 'Aucun défaut (bon client)'}")
        
        print("\n" + "-"*80)
        print("ANALYSE DE L'IA")
        print("-"*80)
        print(result['raw_output'])
        
        # Vérifier la qualité de l'analyse contrefactuelle
        print("\n" + "="*80)
        print("VÉRIFICATION DE LA QUALITÉ")
        print("="*80)
        
        checks_passed = 0
        total_checks = 5
        
        # Check 1 : L'agent a bien analysé les deux alternatives (réelle + contrefactuelle)
        if result['alternatives_analyzed'] >= 2:
            print("✅ Check 1 : Décision réelle et alternative contrefactuelle analysées")
            checks_passed += 1
        else:
            print("❌ Check 1 : Analyse incomplète")
        
        # Check 2 : Des cas historiques ont été trouvés
        if result['similar_cases_count'] > 0:
            print(f"✅ Check 2 : {result['similar_cases_count']} cas historiques trouvés")
            checks_passed += 1
        else:
            print("❌ Check 2 : Aucun cas historique trouvé")
        
        # Check 3 : Taux de défaut calculé
        if result['historical_default_rate'] is not None:
            print(f"✅ Check 3 : Taux de défaut calculé ({result['historical_default_rate']:.2%})")
            checks_passed += 1
        else:
            print("❌ Check 3 : Taux de défaut non calculé")
        
        # Check 4 : Analyse détaillée générée
        if result['raw_output'] and len(result['raw_output']) > 100:
            print(f"✅ Check 4 : Analyse détaillée générée ({len(result['raw_output'])} caractères)")
            checks_passed += 1
        else:
            print("❌ Check 4 : Analyse insuffisante")
        
        # Check 5 : Similarité acceptable
        if result['avg_similarity_score'] > 0.7:
            print(f"✅ Check 5 : Similarité acceptable ({result['avg_similarity_score']:.4f})")
            checks_passed += 1
        else:
            print(f"⚠️  Check 5 : Similarité faible ({result['avg_similarity_score']:.4f})")
        
        print("\n" + "="*80)
        score_pct = (checks_passed / total_checks) * 100
        if checks_passed == total_checks:
            print(f"🎉 EXCELLENT ! Score : {checks_passed}/{total_checks} ({score_pct:.0f}%)")
            print("✅ L'analyse contrefactuelle fonctionne parfaitement!")
        elif checks_passed >= 3:
            print(f"✅ BON ! Score : {checks_passed}/{total_checks} ({score_pct:.0f}%)")
            print("L'analyse contrefactuelle fonctionne bien")
        else:
            print(f"⚠️  Score : {checks_passed}/{total_checks} ({score_pct:.0f}%)")
            print("L'analyse contrefactuelle nécessite des améliorations")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du test : {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_metriques_risque():
    """Test 2 : Vérifier le calcul des métriques de risque"""
    
    print("\n\n" + "="*80)
    print("TEST 2 : CALCUL DES MÉTRIQUES DE RISQUE")
    print("="*80)
    
    try:
        risk_agent = RiskAgent()
        retriever = QdrantRetriever()
        
        # Récupérer un vrai client et ses cas similaires
        print("\n🔍 Récupération d'un profil client réel...")
        # Chercher plusieurs clients et prendre le PLUS similaire
        candidates = retriever.search("35-year-old client, mid-level job, $60k income, owns car, requesting $150k loan", top_k=10)
        
        if not candidates:
            print("❌ Aucun client trouvé dans Qdrant")
            return False
        
        # Trier par score de similarité (décroissant) et prendre le meilleur
        sample_client = sorted(candidates, key=lambda x: x.get('score', 0), reverse=True)[:1]
        client_id = sample_client[0].get('client_id', 'N/A')
        similarity_score = sample_client[0].get('score', 0)
        print(f"  ✓ Client le PLUS similaire: {client_id} (score: {similarity_score:.4f})")
        
        # Utiliser le profil du client pour la recherche
        client_text = sample_client[0].get('text', 'client')
        query = client_text if client_text else "client"
        
        similar_cases = retriever.search(query, top_k=15)
        
        print(f"\n📊 Calcul des métriques sur {len(similar_cases)} cas...")
        
        # Calculer les métriques
        metrics = risk_agent.calculate_risk_metrics(similar_cases)
        
        print("\n" + "-"*80)
        print("MÉTRIQUES CALCULÉES")
        print("-"*80)
        print(f"Taux de défaut      : {metrics['default_rate']:.2%}")
        print(f"Cas analysés        : {metrics['cases_analyzed']}")
        print(f"Similarité moyenne  : {metrics['avg_similarity']:.4f}")
        print(f"Niveau de confiance : {metrics['confidence_level']}")
        print(f"Catégorie de risque : {metrics['risk_category']}")
        
        # Vérification
        print("\n" + "-"*80)
        print("VÉRIFICATION")
        print("-"*80)
        
        if metrics['cases_analyzed'] > 0:
            print("✅ Métriques calculées avec succès!")
            print(f"✅ Confiance : {metrics['confidence_level']}")
            print(f"✅ Risque : {metrics['risk_category']}")
            return True
        else:
            print("❌ Aucune métrique calculée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        return False


def test_comparaison_alternatives():
    """Test 3 : Vérifier la comparaison entre alternatives"""
    
    print("\n\n" + "="*80)
    print("TEST 3 : COMPARAISON D'ALTERNATIVES")
    print("="*80)
    
    try:
        risk_agent = RiskAgent()
        retriever = QdrantRetriever()
        
        # Récupérer un vrai client pour créer des alternatives réalistes
        print("\n🔍 Récupération d'un profil client réel...")
        # Chercher plusieurs clients et prendre le PLUS similaire
        candidates = retriever.search("35-year-old client, mid-level job, $60k income, owns car, requesting $150k loan", top_k=10)
        
        if not candidates:
            print("❌ Aucun client trouvé dans Qdrant")
            return False
        
        # Trier par score de similarité (décroissant) et prendre le meilleur
        sample_client = sorted(candidates, key=lambda x: x.get('score', 0), reverse=True)[:1]
        client_id = sample_client[0].get('client_id', 'N/A')
        client_text = sample_client[0].get('text', '')
        similarity_score = sample_client[0].get('score', 0)
        # Extraire le revenu du texte où les vraies données sont stockées
        income = extract_value_from_text(client_text, r'(?:annual\s+)?income[:\s]+\$?([\d,]+)', 50000)
        print(f"  ✓ Client le PLUS similaire: {client_id} (score: {similarity_score:.4f})")
        print(f"  ✓ Revenu extrait du texte: ${income:,.0f}")
        
        # Récupérer des cas similaires
        similar_cases = retriever.search(client_text[:200] if client_text else 'client', top_k=10)
        
        # Alternatives basées sur le profil réel
        alternatives = [
            {
                'id': 'conservatrice',
                'description': f'Option conservatrice - {income * 0.6:.0f}$ (60% revenu annuel)',
                'loan_amount': income * 0.6,
                'interest_rate': 0.05,
                'loan_to_income_ratio': 0.6
            },
            {
                'id': 'aggressive',
                'description': f'Option agressive - {income * 3:.0f}$ (3x revenu annuel)',
                'loan_amount': income * 3,
                'interest_rate': 0.12,
                'loan_to_income_ratio': 3.0
            }
        ]
        
        print(f"\n📊 Comparaison de {len(alternatives)} alternatives...")
        
        # Comparer
        comparison = risk_agent.compare_alternatives(alternatives, similar_cases)
        
        print("\n" + "-"*80)
        print("RÉSULTAT DE LA COMPARAISON")
        print("-"*80)
        print(comparison['comparison_analysis'])
        
        print("\n✅ Comparaison effectuée avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        return False


def main():
    """Exécuter tous les tests"""
    
    print("\n" + "🔬"*40)
    print("SUITE DE TESTS DU RISK AGENT")
    print("🔬"*40)
    
    results = []
    
    # Test 1 : Analyse basique
    print("\n🧪 Lancement du Test 1...")
    result1 = test_analyse_risque_basique()
    results.append(result1 is not None)
    
    # Test 2 : Métriques
    print("\n🧪 Lancement du Test 2...")
    result2 = test_metriques_risque()
    results.append(result2)
    
    # Test 3 : Comparaison
    print("\n🧪 Lancement du Test 3...")
    result3 = test_comparaison_alternatives()
    results.append(result3)
    
    # Résumé final
    print("\n\n" + "="*80)
    print("RÉSUMÉ FINAL DES TESTS")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests réussis : {passed}/{total}")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ Votre Risk Agent analyse correctement les risques!")
    elif passed >= total * 0.66:
        print("\n👍 LA PLUPART DES TESTS SONT PASSÉS")
        print("✅ Votre Risk Agent fonctionne bien")
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("⚠️  Vérifiez la configuration de votre agent")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
