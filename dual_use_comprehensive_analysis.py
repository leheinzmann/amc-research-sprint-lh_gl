#!/usr/bin/env python3
"""
Dual-Use Technology Governance Analysis for AI Research Sprint
Analyzing how treaties manage civilian-military boundaries across technology lifecycles
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

print("=== DUAL-USE TECHNOLOGY GOVERNANCE ANALYSIS ===\n")

# Load main weapons_facilities dataset
weapons_df = pd.read_csv('/workspaces/amc-research-sprint-lh_gl/duplicates_result.csv')

# Try to load agreement_info with different encoding
try:
    agreement_info = pd.read_csv('/workspaces/amc-research-sprint-lh_gl/data/amcdata_agreement_info_V2.csv', encoding='latin-1')
    print("Successfully loaded agreement_info dataset")
except:
    print("Note: Could not load agreement_info dataset, proceeding with weapons_facilities only")
    agreement_info = None

# Clean data
weapons_df['item_clean'] = weapons_df['item'].str.strip()

print("STEP 1: IDENTIFYING POTENTIAL DUAL-USE TECHNOLOGIES")
print("=" * 60)

# Identify potential dual-use technologies based on known patterns
dual_use_keywords = [
    'enrichment', 'uranium', 'plutonium', 'centrifuge', 'reactor',
    'chemical', 'precursor', 'biological', 'missile', 'rocket', 'launcher', 
    'satellite', 'delivery', 'computer', 'software', 'technology',
    'equipment', 'material', 'component'
]

# Create a more sophisticated dual-use classification
def classify_dual_use_potential(item_text, weapon_definition=None):
    """
    Classify technologies by dual-use potential
    Returns: 'High', 'Medium', 'Low', or 'Military-Only'
    """
    if pd.isna(item_text):
        return 'Unknown'
    
    item_lower = str(item_text).lower()
    
    # High dual-use potential (technologies with clear civilian applications)
    high_dual_use = [
        'enrichment', 'centrifuge', 'reactor', 'uranium', 'plutonium',
        'chemical precursor', 'biological agent', 'computer', 'software',
        'satellite', 'rocket', 'missile technology', 'delivery system',
        'nuclear material', 'isotope'
    ]
    
    # Medium dual-use potential
    medium_dual_use = [
        'launcher', 'guidance', 'navigation', 'communication',
        'radar', 'sensor', 'detection', 'monitoring'
    ]
    
    # Military-only indicators
    military_only = [
        'nuclear weapon', 'warhead', 'bomb', 'explosive device',
        'icbm', 'slbm', 'heavy bomber', 'small arms', 'weapons','weapon',
        'missile',
        'missiles',
        'munition',
        'icbms',
        'icbm',
        'slbms',
        'abm',
        'asbm',
        'war',
        'warhead',
        'warheads',
        'mine',
        'mines',
        'bomber',
        'tank',
        'combat',
        'attack',
        'warship',
        'booby trap',
        'artillery',
        'heavy cruiser',
        'light cruiser',
        'destroyer',
        'firearm',
        'ammunition',
        'gun',
        'guns',
        'armed forces',
        'air force',
        'navy'
    ]
    
    # Check categories
    for term in military_only:
        if term in item_lower:
            return 'Military-Only'
    
    for term in high_dual_use:
        if term in item_lower:
            return 'High'
    
    for term in medium_dual_use:
        if term in item_lower:
            return 'Medium'
    
    # If contains general terms that might indicate dual-use
    general_terms = ['technology', 'equipment', 'material', 'component']
    for term in general_terms:
        if term in item_lower:
            return 'Medium'
    
    return 'Low'

# Apply classification
weapons_df['dual_use_potential'] = weapons_df.apply(
    lambda x: classify_dual_use_potential(x['item_clean'], x.get('weapon_item_definition')), 
    axis=1
)

print("Dual-Use Classification Results:")
dual_use_counts = weapons_df['dual_use_potential'].value_counts()
print(dual_use_counts)
print()

print("STEP 2: LIFECYCLE PHASE RESTRICTION PATTERNS")
print("=" * 60)

# Define lifecycle phases based on the columns available
lifecycle_phases = {
    'Development': ['ban_development', 'restriction_development'],
    'Testing': ['ban_testing', 'testing_restriction'], 
    'Production': ['ban_production', 'restriction_production'],
    'Transfer': ['ban_transfer', 'restriction_transfer'],
    'Use': ['ban_use', 'restriction_use'],
    'Possession': ['ban_possession', 'restriction_possession']
}

# Create lifecycle restriction summary
def check_phase_restrictions(row, phase_columns):
    """Check if any restrictions exist for a given lifecycle phase"""
    for col in phase_columns:
        if col in row.index and pd.notna(row[col]) and row[col] == 1:
            return 1
    return 0

# Add lifecycle restriction indicators
for phase, columns in lifecycle_phases.items():
    available_cols = [col for col in columns if col in weapons_df.columns]
    if available_cols:
        weapons_df[f'{phase.lower()}_restricted'] = weapons_df.apply(
            lambda row: check_phase_restrictions(row, available_cols), axis=1
        )

print("Lifecycle Phase Restrictions by Dual-Use Category:")
phase_cols = [f'{phase.lower()}_restricted' for phase in lifecycle_phases.keys()]
available_phase_cols = [col for col in phase_cols if col in weapons_df.columns]

if available_phase_cols:
    phase_analysis = weapons_df.groupby('dual_use_potential')[available_phase_cols].mean()
    print(phase_analysis.round(3))
    print()

print("STEP 3: DETAILED DUAL-USE TECHNOLOGY EXAMPLES")
print("=" * 60)

# Focus on high dual-use potential technologies
high_dual_use = weapons_df[weapons_df['dual_use_potential'] == 'High'].copy()

if len(high_dual_use) > 0:
    print(f"Found {len(high_dual_use)} high dual-use potential technologies:")
    print("\nTop High Dual-Use Technologies:")
    for idx, row in high_dual_use.head(10).iterrows():
        print(f"- {row['item_clean']}")
    
    print("\nRestriction Patterns for High Dual-Use Technologies:")
    if available_phase_cols:
        high_dual_restrictions = high_dual_use[available_phase_cols].mean()
        for phase, restriction_rate in high_dual_restrictions.items():
            phase_name = phase.replace('_restricted', '').title()
            print(f"  {phase_name}: {restriction_rate:.1%} restricted")
else:
    print("No high dual-use technologies found with current classification.")

print("\n" + "STEP 4: GOVERNANCE PATTERN ANALYSIS")
print("=" * 60)

# Analyze which phases are most commonly restricted
print("Overall Restriction Frequency by Lifecycle Phase:")
if available_phase_cols:
    overall_restrictions = weapons_df[available_phase_cols].mean().sort_values(ascending=False)
    for phase, freq in overall_restrictions.items():
        phase_name = phase.replace('_restricted', '').title()
        print(f"  {phase_name}: {freq:.1%}")

print("\nComparison: Military-Only vs Dual-Use Restrictions")
comparison_df = weapons_df.groupby('dual_use_potential')[available_phase_cols].mean()
if len(comparison_df) > 0:
    print(comparison_df.round(3))

print("\n" + "STEP 5: SPECIFIC DUAL-USE TECHNOLOGIES OF INTEREST")
print("=" * 60)

# Look for specific technologies mentioned in the challenge
specific_technologies = {
    'Enrichment': weapons_df['item_clean'].str.contains('enrichment|centrifuge', case=False, na=False),
    'Chemical Precursors': weapons_df['item_clean'].str.contains('chemical|precursor', case=False, na=False),
    'Delivery Systems': weapons_df['item_clean'].str.contains('delivery|missile|rocket|launcher', case=False, na=False),
    'Nuclear Materials': weapons_df['item_clean'].str.contains('uranium|plutonium|fissile|nuclear material', case=False, na=False)
}

for tech_name, mask in specific_technologies.items():
    matching_items = weapons_df[mask]
    if len(matching_items) > 0:
        print(f"\n{tech_name} ({len(matching_items)} items):")
        for item in matching_items['item_clean'].unique()[:5]:  # Show top 5
            print(f"  - {item}")
        
        if available_phase_cols:
            tech_restrictions = matching_items[available_phase_cols].mean()
            print(f"  Restriction rates:")
            for phase, rate in tech_restrictions.items():
                phase_name = phase.replace('_restricted', '').title()
                print(f"    {phase_name}: {rate:.1%}")

print("\n" + "STEP 6: AI GOVERNANCE IMPLICATIONS")
print("=" * 60)

print("Technology Lifecycle Mapping to AI Governance:")
print("  Development → AI Model Training/Research")
print("  Testing → Model Evaluation/Validation") 
print("  Production → Model Deployment/Hosting")
print("  Transfer → Model Sharing/Open-Sourcing")
print("  Use → AI Application/Inference")
print("  Possession → Model Ownership/Access")

print("\nKey Insights for AI Governance:")
print("1. PRECEDENT PATTERNS:")
if available_phase_cols and len(overall_restrictions) > 0:
    most_restricted = overall_restrictions.idxmax().replace('_restricted', '').title()
    least_restricted = overall_restrictions.idxmin().replace('_restricted', '').title()
    print(f"   - Most commonly restricted phase: {most_restricted}")
    print(f"   - Least commonly restricted phase: {least_restricted}")

print("2. DUAL-USE CONSIDERATIONS:")
print("   - High dual-use technologies show different restriction patterns")
print("   - Treaties distinguish between civilian and military applications")
print("   - Lifecycle phase matters for governance design")

print("\n3. RECOMMENDATIONS FOR AI GOVERNANCE:")
print("   - Focus restrictions on phases with strongest precedent")
print("   - Consider civilian benefits when designing restrictions") 
print("   - Implement graduated controls based on dual-use potential")
print("   - Use lifecycle approach rather than blanket restrictions")
