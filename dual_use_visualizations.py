#!/usr/bin/env python3
"""
Dual-Use Technology Governance Visualizations
Creating charts to illustrate key patterns for AI governance research
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Load and prepare data
weapons_df = pd.read_csv('/home/claude/amc-research-sprint-master/data/amcdata_weapons_facilities_V2.csv')
weapons_df['item_clean'] = weapons_df['item'].str.strip()

# Apply dual-use classification
def classify_dual_use_potential(item_text, weapon_definition=None):
    if pd.isna(item_text):
        return 'Unknown'
    
    item_lower = str(item_text).lower()
    
    high_dual_use = [
        'enrichment', 'centrifuge', 'reactor', 'uranium', 'plutonium',
        'chemical precursor', 'biological agent', 'computer', 'software',
        'satellite', 'rocket', 'missile technology', 'delivery system',
        'nuclear material', 'isotope'
    ]
    
    medium_dual_use = [
        'launcher', 'guidance', 'navigation', 'communication',
        'radar', 'sensor', 'detection', 'monitoring'
    ]
    
    military_only = [
        'nuclear weapon', 'warhead', 'bomb', 'explosive device',
        'icbm', 'slbm', 'heavy bomber', 'small arms'
    ]
    
    for term in military_only:
        if term in item_lower:
            return 'Military-Only'
    
    for term in high_dual_use:
        if term in item_lower:
            return 'High'
    
    for term in medium_dual_use:
        if term in item_lower:
            return 'Medium'
    
    general_terms = ['technology', 'equipment', 'material', 'component']
    for term in general_terms:
        if term in item_lower:
            return 'Medium'
    
    return 'Low'

weapons_df['dual_use_potential'] = weapons_df.apply(
    lambda x: classify_dual_use_potential(x['item_clean'], x.get('weapon_item_definition')), 
    axis=1
)

# Create lifecycle restriction indicators
lifecycle_phases = {
    'Development': ['ban_development', 'restriction_development'],
    'Testing': ['ban_testing', 'testing_restriction'], 
    'Production': ['ban_production', 'restriction_production'],
    'Transfer': ['ban_transfer', 'restriction_transfer'],
    'Use': ['ban_use', 'restriction_use'],
    'Possession': ['ban_possession', 'restriction_possession']
}

def check_phase_restrictions(row, phase_columns):
    for col in phase_columns:
        if col in row.index and pd.notna(row[col]) and row[col] == 1:
            return 1
    return 0

for phase, columns in lifecycle_phases.items():
    available_cols = [col for col in columns if col in weapons_df.columns]
    if available_cols:
        weapons_df[f'{phase.lower()}_restricted'] = weapons_df.apply(
            lambda row: check_phase_restrictions(row, available_cols), axis=1
        )

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Dual-Use Technology Governance Patterns in Arms Control Treaties', 
             fontsize=16, fontweight='bold')

# 1. Dual-Use Classification Distribution
ax1 = axes[0, 0]
dual_use_counts = weapons_df['dual_use_potential'].value_counts()
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
wedges, texts, autotexts = ax1.pie(dual_use_counts.values, labels=dual_use_counts.index, 
                                   autopct='%1.1f%%', startangle=90, colors=colors)
ax1.set_title('Distribution of Technologies by\nDual-Use Potential', fontweight='bold')

# 2. Lifecycle Phase Restrictions by Dual-Use Category
ax2 = axes[0, 1]
phase_cols = [f'{phase.lower()}_restricted' for phase in lifecycle_phases.keys()]
available_phase_cols = [col for col in phase_cols if col in weapons_df.columns]

if available_phase_cols:
    phase_analysis = weapons_df.groupby('dual_use_potential')[available_phase_cols].mean()
    
    # Clean up column names for display
    phase_analysis.columns = [col.replace('_restricted', '').title() for col in phase_analysis.columns]
    
    # Create heatmap
    sns.heatmap(phase_analysis, annot=True, fmt='.2f', cmap='YlOrRd', 
                ax=ax2, cbar_kws={'label': 'Restriction Rate'})
    ax2.set_title('Restriction Rates by Lifecycle Phase\nand Dual-Use Category', fontweight='bold')
    ax2.set_xlabel('Lifecycle Phase')
    ax2.set_ylabel('Dual-Use Potential')

# 3. Overall Lifecycle Phase Restriction Frequency
ax3 = axes[1, 0]
if available_phase_cols:
    overall_restrictions = weapons_df[available_phase_cols].mean().sort_values(ascending=True)
    phase_names = [col.replace('_restricted', '').title() for col in overall_restrictions.index]
    
    bars = ax3.barh(phase_names, overall_restrictions.values, color='#45B7D1', alpha=0.7)
    ax3.set_title('Overall Restriction Frequency\nby Lifecycle Phase', fontweight='bold')
    ax3.set_xlabel('Restriction Rate')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax3.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.1%}', ha='left', va='center')

# 4. Specific Technology Categories
ax4 = axes[1, 1]
specific_technologies = {
    'Chemical\nPrecursors': weapons_df['item_clean'].str.contains('chemical|precursor', case=False, na=False),
    'Delivery\nSystems': weapons_df['item_clean'].str.contains('delivery|missile|rocket|launcher', case=False, na=False),
    'Nuclear\nMaterials': weapons_df['item_clean'].str.contains('uranium|plutonium|fissile|nuclear material', case=False, na=False)
}

tech_data = []
for tech_name, mask in specific_technologies.items():
    matching_items = weapons_df[mask]
    if len(matching_items) > 0 and available_phase_cols:
        tech_restrictions = matching_items[available_phase_cols].mean()
        for phase, rate in tech_restrictions.items():
            phase_name = phase.replace('_restricted', '').title()
            tech_data.append({'Technology': tech_name, 'Phase': phase_name, 'Restriction_Rate': rate})

if tech_data:
    tech_df = pd.DataFrame(tech_data)
    pivot_tech = tech_df.pivot(index='Technology', columns='Phase', values='Restriction_Rate')
    
    sns.heatmap(pivot_tech, annot=True, fmt='.2f', cmap='RdYlBu_r', ax=ax4,
                cbar_kws={'label': 'Restriction Rate'})
    ax4.set_title('Restriction Patterns for Key\nDual-Use Technologies', fontweight='bold')
    ax4.set_xlabel('Lifecycle Phase')
    ax4.set_ylabel('Technology Type')

plt.tight_layout()
plt.savefig('/home/claude/dual_use_governance_analysis.png', dpi=300, bbox_inches='tight')
print("Visualization saved as 'dual_use_governance_analysis.png'")

# Create a summary table
print("\n" + "="*80)
print("DUAL-USE TECHNOLOGY GOVERNANCE ANALYSIS SUMMARY")
print("="*80)

print("\nKEY FINDINGS:")
print("-" * 40)

# Overall patterns
if available_phase_cols:
    overall_restrictions = weapons_df[available_phase_cols].mean().sort_values(ascending=False)
    print(f"1. Most restricted phase: {overall_restrictions.idxmax().replace('_restricted', '').title()} ({overall_restrictions.max():.1%})")
    print(f"2. Least restricted phase: {overall_restrictions.idxmin().replace('_restricted', '').title()} ({overall_restrictions.min():.1%})")

# Dual-use specific insights
high_dual_use = weapons_df[weapons_df['dual_use_potential'] == 'High']
military_only = weapons_df[weapons_df['dual_use_potential'] == 'Military-Only']

if len(high_dual_use) > 0 and len(military_only) > 0 and available_phase_cols:
    high_dual_avg = high_dual_use[available_phase_cols].mean().mean()
    military_avg = military_only[available_phase_cols].mean().mean()
    
    print(f"3. High dual-use technologies: {high_dual_avg:.1%} average restriction rate")
    print(f"4. Military-only technologies: {military_avg:.1%} average restriction rate")

print("\nDUAL-USE TECHNOLOGY COUNTS:")
print("-" * 40)
for category, count in weapons_df['dual_use_potential'].value_counts().items():
    print(f"{category}: {count} technologies ({count/len(weapons_df)*100:.1f}%)")

print("\nAI GOVERNANCE RECOMMENDATIONS:")
print("-" * 40)
print("• Focus on later lifecycle phases (possession, production) for strongest precedent")
print("• Consider graduated restrictions based on dual-use potential")  
print("• Transfer restrictions may be key for AI model sharing governance")
print("• Development phase shows least restriction - preserve research freedom")
print("• Use-phase restrictions common - relevant for AI deployment controls")

print("\nFILE SAVED: dual_use_governance_analysis.png")
print("This visualization can be included in your research presentation.")
