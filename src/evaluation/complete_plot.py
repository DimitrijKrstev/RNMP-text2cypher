# src/evaluation/thesis_plots.py

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from models import TaskResult, TaskType

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ThesisPlotter:
    def __init__(self, results_dir: Path, output_dir: Path):
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Style configuration
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = {
            'sql': '#2E86AB',
            'cypher': '#A23B72',
            'easy': '#06A77D',
            'intermediate': '#F18F01',
            'hard': '#C73E1D'
        }
    
    def load_all_results(self, model: str = 'claude-sonnet-4-20250514') -> Dict:
        """Load all results organized by dataset/language/difficulty"""
        results = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        datasets = ['rel-f1', 'rel-stack', 'rel-trial']
        languages = ['sql', 'cypher']
        difficulties = ['easy', 'intermediate', 'hard']
        
        for dataset in datasets:
            for language in languages:
                task_type = TaskType.SQL if language == 'sql' else TaskType.CYPHER
                
                for difficulty in difficulties:
                    result_file = self.results_dir / dataset / language / model / f'{difficulty}.json'
                    if result_file.exists():
                        with open(result_file, 'r') as f:
                            data = json.load(f)
                            results[dataset][language][difficulty] = [
                                TaskResult.from_dict(item, task_type) for item in data
                            ]
        
        return results
    
    def calculate_aggregates(self, results: List[TaskResult]) -> Dict:
        """Calculate aggregate metrics for a list of results with robust None handling"""
        
        # Return zeros if no results
        if not results:
            return {
                'parse_success': 0.0,
                'execution_accuracy': 0.0,
                'correct_result': 0.0,
                'entity_f1': 0.0,
                'attribute_f1': 0.0,
                'relation_f1': 0.0,
                'filter_f1': 0.0,
                'aggregation_f1': 0.0,
                'return_column_f1': 0.0,
                'result_f1': 0.0,
                'result_precision': 0.0,
                'result_recall': 0.0,
            }
        
        total = len(results)
        
        # Helper function to safely calculate mean, filtering out None values
        def safe_mean(values):
            """Calculate mean while filtering out None values"""
            filtered = [v for v in values if v is not None]
            return float(np.mean(filtered)) if filtered else 0.0
        
        return {
            # Boolean success metrics (percentage of True values)
            'parse_success': sum(1 for r in results if r.parse_success) / total,
            'execution_accuracy': sum(1 for r in results if r.execution_accuracy) / total,
            'correct_result': sum(1 for r in results if r.execution_success) / total,
            
            # Structural F1 metrics (averages with None filtering)
            'entity_f1': safe_mean([r.entity_f1 for r in results]),
            'attribute_f1': safe_mean([r.attribute_f1 for r in results]),
            'relation_f1': safe_mean([r.relation_f1 for r in results]),  # Can be None
            'filter_f1': safe_mean([r.filter_f1 for r in results]),
            'aggregation_f1': safe_mean([r.aggregation_f1 for r in results]),
            'return_column_f1': safe_mean([r.return_column_f1 for r in results]),
            
            # Result accuracy metrics (averages)
            'result_f1': safe_mean([r.result_f1 for r in results]),
            'result_precision': safe_mean([r.result_precision for r in results]),
            'result_recall': safe_mean([r.result_recall for r in results]),
        }
    
    def _safe_mean_attribute(self, results: List[TaskResult], attribute: str) -> float:
        """Safely get mean of an attribute, handling None values"""
        values = [getattr(r, attribute) for r in results]
        filtered = [v for v in values if v is not None]
        return float(np.mean(filtered)) if filtered else 0.0
    
    # ==================== Section 1: Aggregate Results ====================
    
    def plot_overall_comparison(self, all_results: Dict):
        """SQL vs Cypher overall comparison"""
        sql_all = []
        cypher_all = []
        
        for dataset in all_results:
            for difficulty in all_results[dataset]['sql']:
                sql_all.extend(all_results[dataset]['sql'][difficulty])
            for difficulty in all_results[dataset]['cypher']:
                cypher_all.extend(all_results[dataset]['cypher'][difficulty])
        
        sql_agg = self.calculate_aggregates(sql_all)
        cypher_agg = self.calculate_aggregates(cypher_all)
        
        metrics = ['parse_success', 'correct_result', 'result_f1']
        metric_labels = ['Parse Success', 'Executable', 'Result F1']
        
        x = np.arange(len(metrics))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sql_vals = [sql_agg[m] for m in metrics]
        cypher_vals = [cypher_agg[m] for m in metrics]
        
        bars1 = ax.bar(x - width/2, sql_vals, width, label='SQL', color=self.colors['sql'])
        bars2 = ax.bar(x + width/2, cypher_vals, width, label='Cypher', color=self.colors['cypher'])
        
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Overall SQL vs Cypher Performance', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_labels)
        ax.legend()
        ax.set_ylim(0, 1.0)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '1_overall_sql_vs_cypher.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generate LaTeX table
        self._generate_latex_table_overall(sql_agg, cypher_agg)
    
    def _generate_latex_table_overall(self, sql_agg: Dict, cypher_agg: Dict):
        """Generate LaTeX table for overall results"""
        latex = r"""\begin{table}[h]
\centering
\caption{Overall SQL vs Cypher Performance}
\begin{tabular}{lcc}
\hline
\textbf{Metric} & \textbf{SQL} & \textbf{Cypher} \\
\hline
"""
        metrics = {
            'Parse Success': 'parse_success',
            'Execution Accuracy': 'execution_accuracy',
            'Correct Result': 'correct_result',
            'Result F1': 'result_f1',
            'Entity F1': 'entity_f1',
            'Attribute F1': 'attribute_f1',
            'Relation F1': 'relation_f1',
            'Filter F1': 'filter_f1',
            'Aggregation F1': 'aggregation_f1',
            'Return Column F1': 'return_column_f1',
        }
        
        for label, key in metrics.items():
            sql_val = sql_agg[key]
            cypher_val = cypher_agg[key]
            latex += f"{label} & {sql_val:.3f} & {cypher_val:.3f} \\\\\n"
        
        latex += r"""\hline
\end{tabular}
\end{table}
"""
        
        with open(self.output_dir / '1_overall_table.tex', 'w') as f:
            f.write(latex)
    
    # ==================== Section 2: Results by Dataset ====================
    
    def plot_dataset_comparison(self, all_results: Dict, dataset: str):
        """Plot SQL vs Cypher for a specific dataset"""
        sql_combined = []
        cypher_combined = []
        
        for difficulty in ['easy', 'intermediate', 'hard']:
            sql_combined.extend(all_results[dataset]['sql'].get(difficulty, []))
            cypher_combined.extend(all_results[dataset]['cypher'].get(difficulty, []))
        
        sql_agg = self.calculate_aggregates(sql_combined)
        cypher_agg = self.calculate_aggregates(cypher_combined)
        
        metrics = ['parse_success', 'execution_accuracy', 'entity_f1', 'relation_f1', 'result_f1']
        metric_labels = ['Parse', 'Exec', 'Entity F1', 'Relation F1', 'Result F1']
        
        x = np.arange(len(metrics))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        sql_vals = [sql_agg[m] for m in metrics]
        cypher_vals = [cypher_agg[m] for m in metrics]
        
        bars1 = ax.bar(x - width/2, sql_vals, width, label='SQL', color=self.colors['sql'])
        bars2 = ax.bar(x + width/2, cypher_vals, width, label='Cypher', color=self.colors['cypher'])
        
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(f'SQL vs Cypher Performance: {dataset}', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_labels, rotation=15, ha='right')
        ax.legend()
        ax.set_ylim(0, 1.0)
        ax.grid(axis='y', alpha=0.3)
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f'2_{dataset}_sql_vs_cypher.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_dataset_difficulty_breakdown(self, all_results: Dict, dataset: str):
        """Plot difficulty breakdown for a dataset"""
        difficulties = ['easy', 'intermediate', 'hard']
        metrics = ['parse_success', 'execution_accuracy', 'result_f1']
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        for idx, language in enumerate(['sql', 'cypher']):
            ax = axes[idx]
            data = []
            
            for difficulty in difficulties:
                results = all_results[dataset][language].get(difficulty, [])
                agg = self.calculate_aggregates(results)
                data.append([agg[m] for m in metrics])
            
            x = np.arange(len(metrics))
            width = 0.25
            
            for i, difficulty in enumerate(difficulties):
                offset = (i - 1) * width
                bars = ax.bar(x + offset, data[i], width, 
                            label=difficulty.capitalize(),
                            color=self.colors[difficulty])
                
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=8)
            
            ax.set_xlabel('Metrics', fontsize=11)
            ax.set_ylabel('Score', fontsize=11)
            ax.set_title(f'{language.upper()} - {dataset}', fontsize=12, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(['Parse', 'Exec', 'Result F1'], rotation=15, ha='right')
            ax.legend()
            ax.set_ylim(0, 1.0)
            ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f'2_{dataset}_difficulty_breakdown.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # ==================== Section 3: Results by Difficulty ====================
    
    def plot_difficulty_across_datasets(self, all_results: Dict, difficulty: str):
        """Plot SQL vs Cypher across all datasets for a specific difficulty"""
        datasets = ['rel-f1', 'rel-stack', 'rel-trial']
        metrics = ['parse_success', 'execution_accuracy', 'entity_f1', 'relation_f1', 'result_f1']
        metric_labels = ['Parse', 'Exec', 'Entity', 'Relation', 'Result']
        
        fig, axes = plt.subplots(1, len(datasets), figsize=(18, 5))
        
        for idx, dataset in enumerate(datasets):
            ax = axes[idx]
            
            sql_results = all_results[dataset]['sql'].get(difficulty, [])
            cypher_results = all_results[dataset]['cypher'].get(difficulty, [])
            
            sql_agg = self.calculate_aggregates(sql_results)
            cypher_agg = self.calculate_aggregates(cypher_results)
            
            x = np.arange(len(metrics))
            width = 0.35
            
            sql_vals = [sql_agg[m] for m in metrics]
            cypher_vals = [cypher_agg[m] for m in metrics]
            
            bars1 = ax.bar(x - width/2, sql_vals, width, label='SQL', color=self.colors['sql'])
            bars2 = ax.bar(x + width/2, cypher_vals, width, label='Cypher', color=self.colors['cypher'])
            
            ax.set_xlabel('Metrics', fontsize=10)
            ax.set_ylabel('Score', fontsize=10)
            ax.set_title(f'{dataset}', fontsize=11, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(metric_labels, rotation=15, ha='right', fontsize=9)
            if idx == 0:
                ax.legend()
            ax.set_ylim(0, 1.0)
            ax.grid(axis='y', alpha=0.3)
            
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}', ha='center', va='bottom', fontsize=7)
        
        fig.suptitle(f'SQL vs Cypher - {difficulty.capitalize()} Queries Across Datasets', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(self.output_dir / f'3_{difficulty}_across_datasets.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # ==================== Section 4: Structural Analysis ====================
    
    def plot_structural_component(self, all_results: Dict, component: str, component_label: str):
        """Plot a specific structural component (entity_f1, relation_f1, etc.) with None handling"""
        datasets = ['rel-f1', 'rel-stack', 'rel-trial']
        difficulties = ['easy', 'intermediate', 'hard']
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(f'{component_label} Performance', fontsize=16, fontweight='bold')
        
        for d_idx, dataset in enumerate(datasets):
            # SQL subplot
            ax_sql = axes[0, d_idx]
            sql_data = []
            for difficulty in difficulties:
                results = all_results[dataset]['sql'].get(difficulty, [])
                avg = self._safe_mean_attribute(results, component) if results else 0.0
                sql_data.append(avg)
            
            bars = ax_sql.bar(difficulties, sql_data, color=self.colors['sql'], alpha=0.8)
            ax_sql.set_title(f'SQL - {dataset}', fontsize=11, fontweight='bold')
            ax_sql.set_ylabel('F1 Score', fontsize=10)
            ax_sql.set_ylim(0, 1.0)
            ax_sql.grid(axis='y', alpha=0.3)
            
            for bar in bars:
                height = bar.get_height()
                ax_sql.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=9)
            
            # Cypher subplot
            ax_cypher = axes[1, d_idx]
            cypher_data = []
            for difficulty in difficulties:
                results = all_results[dataset]['cypher'].get(difficulty, [])
                avg = self._safe_mean_attribute(results, component) if results else 0.0
                cypher_data.append(avg)
            
            bars = ax_cypher.bar(difficulties, cypher_data, color=self.colors['cypher'], alpha=0.8)
            ax_cypher.set_title(f'Cypher - {dataset}', fontsize=11, fontweight='bold')
            ax_cypher.set_ylabel('F1 Score', fontsize=10)
            ax_cypher.set_xlabel('Difficulty', fontsize=10)
            ax_cypher.set_ylim(0, 1.0)
            ax_cypher.grid(axis='y', alpha=0.3)
            
            for bar in bars:
                height = bar.get_height()
                ax_cypher.text(bar.get_x() + bar.get_width()/2., height,
                              f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f'4_{component}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_structural_radar(self, all_results: Dict):
        """Radar chart comparing all structural components with None handling"""
        from math import pi
        
        components = ['entity_f1', 'attribute_f1', 'relation_f1', 
                     'filter_f1', 'aggregation_f1', 'return_column_f1']
        labels = ['Entity', 'Attribute', 'Relation', 'Filter', 'Aggregation', 'Return Column']
        
        # Aggregate all results
        sql_all = []
        cypher_all = []
        for dataset in all_results:
            for difficulty in all_results[dataset]['sql']:
                sql_all.extend(all_results[dataset]['sql'][difficulty])
            for difficulty in all_results[dataset]['cypher']:
                cypher_all.extend(all_results[dataset]['cypher'][difficulty])
        
        # Calculate means with None filtering
        sql_vals = [self._safe_mean_attribute(sql_all, comp) for comp in components]
        cypher_vals = [self._safe_mean_attribute(cypher_all, comp) for comp in components]
        
        # Number of variables
        num_vars = len(labels)
        angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
        sql_vals += sql_vals[:1]
        cypher_vals += cypher_vals[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, sql_vals, 'o-', linewidth=2, label='SQL', color=self.colors['sql'])
        ax.fill(angles, sql_vals, alpha=0.25, color=self.colors['sql'])
        
        ax.plot(angles, cypher_vals, 'o-', linewidth=2, label='Cypher', color=self.colors['cypher'])
        ax.fill(angles, cypher_vals, alpha=0.25, color=self.colors['cypher'])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=11)
        ax.set_ylim(0, 1.0)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=9)
        ax.grid(True)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
        ax.set_title('Structural Components Comparison\n(SQL vs Cypher)', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '4_structural_radar.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # ==================== Section 5: Result Accuracy ====================
    
    def plot_execution_accuracy_heatmap(self, all_results: Dict):
        """Heatmap of execution accuracy (dataset x difficulty x language)"""
        datasets = ['rel-f1', 'rel-stack', 'rel-trial']
        difficulties = ['easy', 'intermediate', 'hard']
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        for idx, language in enumerate(['sql', 'cypher']):
            data = np.zeros((len(datasets), len(difficulties)))
            
            for i, dataset in enumerate(datasets):
                for j, difficulty in enumerate(difficulties):
                    results = all_results[dataset][language].get(difficulty, [])
                    if results:
                        data[i, j] = sum(1 for r in results if r.execution_accuracy) / len(results)
            
            ax = axes[idx]
            im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
            
            ax.set_xticks(np.arange(len(difficulties)))
            ax.set_yticks(np.arange(len(datasets)))
            ax.set_xticklabels([d.capitalize() for d in difficulties])
            ax.set_yticklabels(datasets)
            ax.set_xlabel('Difficulty', fontsize=11)
            ax.set_ylabel('Dataset', fontsize=11)
            ax.set_title(f'{language.upper()} Execution Accuracy', fontsize=12, fontweight='bold')
            
            # Add text annotations
            for i in range(len(datasets)):
                for j in range(len(difficulties)):
                    text = ax.text(j, i, f'{data[i, j]:.2f}',
                                 ha="center", va="center", color="black", fontsize=10)
            
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '5_execution_accuracy_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_precision_recall_analysis(self, all_results: Dict):
        """Precision vs Recall scatter plot and grouped bars"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Scatter plot
        ax = axes[0]
        sql_all = []
        cypher_all = []
        
        for dataset in all_results:
            for difficulty in all_results[dataset]['sql']:
                sql_all.extend(all_results[dataset]['sql'][difficulty])
            for difficulty in all_results[dataset]['cypher']:
                cypher_all.extend(all_results[dataset]['cypher'][difficulty])
        
        sql_precision = [r.result_precision for r in sql_all]
        sql_recall = [r.result_recall for r in sql_all]
        cypher_precision = [r.result_precision for r in cypher_all]
        cypher_recall = [r.result_recall for r in cypher_all]
        
        ax.scatter(sql_recall, sql_precision, alpha=0.5, s=30, 
                  color=self.colors['sql'], label='SQL', edgecolors='black', linewidth=0.5)
        ax.scatter(cypher_recall, cypher_precision, alpha=0.5, s=30,
                  color=self.colors['cypher'], label='Cypher', edgecolors='black', linewidth=0.5)
        
        ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Perfect P=R')
        ax.set_xlabel('Recall', fontsize=12)
        ax.set_ylabel('Precision', fontsize=12)
        ax.set_title('Precision vs Recall Distribution', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        
        # Grouped bar chart - average by difficulty
        ax = axes[1]
        difficulties = ['easy', 'intermediate', 'hard']
        x = np.arange(len(difficulties))
        width = 0.2
        
        sql_prec_by_diff = []
        sql_rec_by_diff = []
        cypher_prec_by_diff = []
        cypher_rec_by_diff = []
        
        for difficulty in difficulties:
            sql_diff_results = []
            cypher_diff_results = []
            for dataset in all_results:
                sql_diff_results.extend(all_results[dataset]['sql'].get(difficulty, []))
                cypher_diff_results.extend(all_results[dataset]['cypher'].get(difficulty, []))
            
            sql_prec_by_diff.append(self._safe_mean_attribute(sql_diff_results, 'result_precision'))
            sql_rec_by_diff.append(self._safe_mean_attribute(sql_diff_results, 'result_recall'))
            cypher_prec_by_diff.append(self._safe_mean_attribute(cypher_diff_results, 'result_precision'))
            cypher_rec_by_diff.append(self._safe_mean_attribute(cypher_diff_results, 'result_recall'))
        
        ax.bar(x - width*1.5, sql_prec_by_diff, width, label='SQL Precision', color=self.colors['sql'], alpha=0.8)
        ax.bar(x - width*0.5, sql_rec_by_diff, width, label='SQL Recall', color=self.colors['sql'], alpha=0.5)
        ax.bar(x + width*0.5, cypher_prec_by_diff, width, label='Cypher Precision', color=self.colors['cypher'], alpha=0.8)
        ax.bar(x + width*1.5, cypher_rec_by_diff, width, label='Cypher Recall', color=self.colors['cypher'], alpha=0.5)
        
        ax.set_xlabel('Difficulty', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Precision & Recall by Difficulty', fontsize=13, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([d.capitalize() for d in difficulties])
        ax.legend(fontsize=9)
        ax.set_ylim(0, 1.0)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '5_precision_recall.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # ==================== Section 6: Error Analysis ====================
    
    def plot_error_distribution(self, all_results: Dict):
        """Error category distribution (SQL vs Cypher)"""
        error_counts_sql = defaultdict(int)
        error_counts_cypher = defaultdict(int)
        total_sql = 0
        total_cypher = 0
        
        for dataset in all_results:
            for difficulty in all_results[dataset]['sql']:
                for result in all_results[dataset]['sql'][difficulty]:
                    total_sql += 1
                    if result.error_category != 'NONE' and result.error_category != 'CORRECT':
                        error_counts_sql[result.error_category] += 1
            
            for difficulty in all_results[dataset]['cypher']:
                for result in all_results[dataset]['cypher'][difficulty]:
                    total_cypher += 1
                    if result.error_category != 'NONE' and result.error_category != 'CORRECT':
                        error_counts_cypher[result.error_category] += 1
        
        # Get all error categories
        all_categories = sorted(set(list(error_counts_sql.keys()) + list(error_counts_cypher.keys())))
        
        if not all_categories:
            print("No errors found to plot")
            return
        
        # Calculate percentages
        sql_percentages = [error_counts_sql[cat] / total_sql * 100 if total_sql > 0 else 0 for cat in all_categories]
        cypher_percentages = [error_counts_cypher[cat] / total_cypher * 100 if total_cypher > 0 else 0 for cat in all_categories]
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # SQL pie chart
        ax = axes[0]
        colors_pie = plt.cm.Set3(np.linspace(0, 1, len(all_categories)))
        wedges, texts, autotexts = ax.pie(sql_percentages, labels=all_categories, autopct='%1.1f%%',
                                          colors=colors_pie, startangle=90)
        ax.set_title('SQL Error Distribution', fontsize=13, fontweight='bold')
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontsize(9)
        
        # Cypher pie chart
        ax = axes[1]
        wedges, texts, autotexts = ax.pie(cypher_percentages, labels=all_categories, autopct='%1.1f%%',
                                          colors=colors_pie, startangle=90)
        ax.set_title('Cypher Error Distribution', fontsize=13, fontweight='bold')
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontsize(9)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '6_error_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generate LaTeX table
        self._generate_error_table(all_categories, error_counts_sql, error_counts_cypher, total_sql, total_cypher)
    
    def _generate_error_table(self, categories, sql_counts, cypher_counts, total_sql, total_cypher):
        """Generate LaTeX table for error distribution"""
        latex = r"""\begin{table}[h]
\centering
\caption{Error Category Distribution}
\begin{tabular}{lcccc}
\hline
\textbf{Error Category} & \textbf{SQL Count} & \textbf{SQL \%} & \textbf{Cypher Count} & \textbf{Cypher \%} \\
\hline
"""
        for cat in categories:
            sql_count = sql_counts[cat]
            cypher_count = cypher_counts[cat]
            sql_pct = (sql_count / total_sql * 100) if total_sql > 0 else 0
            cypher_pct = (cypher_count / total_cypher * 100) if total_cypher > 0 else 0
            latex += f"{cat.replace('_', ' ').title()} & {sql_count} & {sql_pct:.1f}\\% & {cypher_count} & {cypher_pct:.1f}\\% \\\\\n"
        
        latex += r"""\hline
\end{tabular}
\end{table}
"""
        with open(self.output_dir / '6_error_table.tex', 'w') as f:
            f.write(latex)
    
    def plot_error_by_dataset_heatmap(self, all_results: Dict):
        """Error heatmap (dataset x error_category x language)"""
        datasets = ['rel-f1', 'rel-stack', 'rel-trial']
        
        # Collect all error categories
        all_errors = set()
        for dataset in all_results:
            for lang in ['sql', 'cypher']:
                for diff in all_results[dataset][lang]:
                    for result in all_results[dataset][lang][diff]:
                        if result.error_category not in ['NONE', 'CORRECT']:
                            all_errors.add(result.error_category)
        
        error_categories = sorted(list(all_errors))
        
        if not error_categories:
            print("No errors found for heatmap")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        for idx, language in enumerate(['sql', 'cypher']):
            data = np.zeros((len(datasets), len(error_categories)))
            
            for i, dataset in enumerate(datasets):
                total_queries = 0
                error_counts = defaultdict(int)
                
                for difficulty in all_results[dataset][language]:
                    for result in all_results[dataset][language][difficulty]:
                        total_queries += 1
                        if result.error_category not in ['NONE', 'CORRECT']:
                            error_counts[result.error_category] += 1
                
                for j, error_cat in enumerate(error_categories):
                    data[i, j] = (error_counts[error_cat] / total_queries * 100) if total_queries > 0 else 0
            
            ax = axes[idx]
            im = ax.imshow(data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=50)
            
            ax.set_xticks(np.arange(len(error_categories)))
            ax.set_yticks(np.arange(len(datasets)))
            ax.set_xticklabels([e.replace('_', '\n') for e in error_categories], fontsize=9, rotation=45, ha='right')
            ax.set_yticklabels(datasets)
            ax.set_xlabel('Error Category', fontsize=11)
            ax.set_ylabel('Dataset', fontsize=11)
            ax.set_title(f'{language.upper()} Error Distribution by Dataset (%)', fontsize=12, fontweight='bold')
            
            for i in range(len(datasets)):
                for j in range(len(error_categories)):
                    text = ax.text(j, i, f'{data[i, j]:.1f}',
                                 ha="center", va="center", color="black", fontsize=9)
            
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '6_error_by_dataset_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_error_by_difficulty(self, all_results: Dict):
        """Error distribution change with difficulty"""
        difficulties = ['easy', 'intermediate', 'hard']
        
        # Collect all error categories
        all_errors = set()
        for dataset in all_results:
            for lang in ['sql', 'cypher']:
                for diff in all_results[dataset][lang]:
                    for result in all_results[dataset][lang][diff]:
                        if result.error_category not in ['NONE', 'CORRECT']:
                            all_errors.add(result.error_category)
        
        error_categories = sorted(list(all_errors))
        
        if not error_categories:
            print("No errors found for difficulty plot")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        for idx, language in enumerate(['sql', 'cypher']):
            data = {cat: [] for cat in error_categories}
            
            for difficulty in difficulties:
                total_queries = 0
                error_counts = defaultdict(int)
                
                for dataset in all_results:
                    for result in all_results[dataset][language].get(difficulty, []):
                        total_queries += 1
                        if result.error_category not in ['NONE', 'CORRECT']:
                            error_counts[result.error_category] += 1
                
                for cat in error_categories:
                    pct = (error_counts[cat] / total_queries * 100) if total_queries > 0 else 0
                    data[cat].append(pct)
            
            ax = axes[idx]
            x = np.arange(len(difficulties))
            width = 0.8 / len(error_categories)
            
            for i, cat in enumerate(error_categories):
                offset = (i - len(error_categories)/2) * width + width/2
                bars = ax.bar(x + offset, data[cat], width, label=cat.replace('_', ' ').title())
            
            ax.set_xlabel('Difficulty', fontsize=12)
            ax.set_ylabel('Error Rate (%)', fontsize=12)
            ax.set_title(f'{language.upper()} Errors by Difficulty', fontsize=13, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels([d.capitalize() for d in difficulties])
            ax.legend(fontsize=9, loc='upper left')
            ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '6_error_by_difficulty.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # ==================== Section 7: Comparative Synthesis ====================
    
    def plot_parse_success_comparison(self, all_results: Dict):
        """Parse success rate comparison"""
        datasets = ['rel-f1', 'rel-stack', 'rel-trial']
        difficulties = ['easy', 'intermediate', 'hard']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(datasets))
        width = 0.15
        
        for i, difficulty in enumerate(difficulties):
            sql_rates = []
            cypher_rates = []
            
            for dataset in datasets:
                sql_results = all_results[dataset]['sql'].get(difficulty, [])
                cypher_results = all_results[dataset]['cypher'].get(difficulty, [])
                
                sql_rate = sum(1 for r in sql_results if r.parse_success) / len(sql_results) if sql_results else 0
                cypher_rate = sum(1 for r in cypher_results if r.parse_success) / len(cypher_results) if cypher_results else 0
                
                sql_rates.append(sql_rate)
                cypher_rates.append(cypher_rate)
            
            offset_sql = (i - 1.5) * width
            offset_cypher = (i - 1) * width
            
            ax.bar(x + offset_sql, sql_rates, width, 
                  label=f'SQL {difficulty.capitalize()}' if i < 3 else '', 
                  color=self.colors['sql'], alpha=0.4 + i*0.2)
            ax.bar(x + offset_cypher, cypher_rates, width,
                  label=f'Cypher {difficulty.capitalize()}' if i < 3 else '',
                  color=self.colors['cypher'], alpha=0.4 + i*0.2)
        
        ax.set_xlabel('Dataset', fontsize=12)
        ax.set_ylabel('Parse Success Rate', fontsize=12)
        ax.set_title('Parse Success Comparison (SQL vs Cypher)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(datasets)
        ax.legend(ncol=2, fontsize=9)
        ax.set_ylim(0, 1.0)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '7_parse_success_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_final_synthesis_table(self, all_results: Dict):
        """Final synthesis: SQL wins vs Cypher wins by metric"""
        metrics = ['parse_success', 'execution_accuracy', 'entity_f1', 'attribute_f1',
                  'relation_f1', 'filter_f1', 'aggregation_f1', 'return_column_f1', 'result_f1']
        
        wins = {'sql': 0, 'cypher': 0, 'tie': 0}
        details = {}
        
        for metric in metrics:
            sql_all = []
            cypher_all = []
            
            for dataset in all_results:
                for difficulty in all_results[dataset]['sql']:
                    sql_all.extend(all_results[dataset]['sql'][difficulty])
                for difficulty in all_results[dataset]['cypher']:
                    cypher_all.extend(all_results[dataset]['cypher'][difficulty])
            
            if metric == 'parse_success':
                sql_val = sum(1 for r in sql_all if r.parse_success) / len(sql_all) if sql_all else 0
                cypher_val = sum(1 for r in cypher_all if r.parse_success) / len(cypher_all) if cypher_all else 0
            elif metric == 'execution_accuracy':
                sql_val = sum(1 for r in sql_all if r.execution_accuracy) / len(sql_all) if sql_all else 0
                cypher_val = sum(1 for r in cypher_all if r.execution_accuracy) / len(cypher_all) if cypher_all else 0
            else:
                sql_val = self._safe_mean_attribute(sql_all, metric)
                cypher_val = self._safe_mean_attribute(cypher_all, metric)
            
            details[metric] = {'sql': sql_val, 'cypher': cypher_val}
            
            if abs(sql_val - cypher_val) < 0.01:
                wins['tie'] += 1
            elif sql_val > cypher_val:
                wins['sql'] += 1
            else:
                wins['cypher'] += 1
        
        # Plot wins
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Pie chart of wins
        ax = axes[0]
        labels = ['SQL Wins', 'Cypher Wins', 'Ties']
        sizes = [wins['sql'], wins['cypher'], wins['tie']]
        colors_pie = [self.colors['sql'], self.colors['cypher'], '#888888']
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.0f%%',
                                          colors=colors_pie, startangle=90)
        ax.set_title('Overall Performance Comparison\n(SQL vs Cypher Wins by Metric)', 
                    fontsize=13, fontweight='bold')
        
        # Detailed comparison
        ax = axes[1]
        metric_labels = [m.replace('_', ' ').title() for m in metrics]
        sql_vals = [details[m]['sql'] for m in metrics]
        cypher_vals = [details[m]['cypher'] for m in metrics]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = ax.barh(x - width/2, sql_vals, width, label='SQL', color=self.colors['sql'])
        bars2 = ax.barh(x + width/2, cypher_vals, width, label='Cypher', color=self.colors['cypher'])
        
        ax.set_yticks(x)
        ax.set_yticklabels(metric_labels, fontsize=9)
        ax.set_xlabel('Score', fontsize=12)
        ax.set_title('Metric-by-Metric Comparison', fontsize=13, fontweight='bold')
        ax.legend()
        ax.set_xlim(0, 1.0)
        ax.grid(axis='x', alpha=0.3)
        
        for bars in [bars1, bars2]:
            for bar in bars:
                width_val = bar.get_width()
                ax.text(width_val, bar.get_y() + bar.get_height()/2.,
                       f'{width_val:.2f}', ha='left', va='center', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '7_final_synthesis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generate LaTeX summary table
        self._generate_synthesis_table(details, wins)
    
    def _generate_synthesis_table(self, details: Dict, wins: Dict):
        """Generate LaTeX synthesis table"""
        latex = r"""\begin{table}[h]
\centering
\caption{SQL vs Cypher Performance Synthesis}
\begin{tabular}{lccc}
\hline
\textbf{Metric} & \textbf{SQL} & \textbf{Cypher} & \textbf{Winner} \\
\hline
"""
        for metric, values in details.items():
            sql_val = values['sql']
            cypher_val = values['cypher']
            if abs(sql_val - cypher_val) < 0.01:
                winner = 'Tie'
            elif sql_val > cypher_val:
                winner = 'SQL'
            else:
                winner = 'Cypher'
            
            metric_label = metric.replace('_', ' ').title()
            latex += f"{metric_label} & {sql_val:.3f} & {cypher_val:.3f} & {winner} \\\\\n"
        
        latex += r"""\hline
\multicolumn{4}{l}{\textbf{Summary:}} \\
"""
        latex += f"SQL Wins & \\multicolumn{{3}}{{l}}{{{wins['sql']}}} \\\\\n"
        latex += f"Cypher Wins & \\multicolumn{{3}}{{l}}{{{wins['cypher']}}} \\\\\n"
        latex += f"Ties & \\multicolumn{{3}}{{l}}{{{wins['tie']}}} \\\\\n"
        
        latex += r"""\hline
\end{tabular}
\end{table}
"""
        with open(self.output_dir / '7_synthesis_table.tex', 'w') as f:
            f.write(latex)
    
    # ==================== Main Generation Method ====================
    
    def generate_all_plots(self):
        """Generate all plots and tables for the thesis"""
        print("Loading all results...")
        all_results = self.load_all_results()
        
        print("\n=== Section 1: Aggregate Results ===")
        self.plot_overall_comparison(all_results)
        
        print("\n=== Section 2: Results by Dataset ===")
        for dataset in ['rel-f1', 'rel-stack', 'rel-trial']:
            print(f"  Processing {dataset}...")
            self.plot_dataset_comparison(all_results, dataset)
            self.plot_dataset_difficulty_breakdown(all_results, dataset)
        
        print("\n=== Section 3: Results by Difficulty ===")
        for difficulty in ['easy', 'intermediate', 'hard']:
            print(f"  Processing {difficulty}...")
            self.plot_difficulty_across_datasets(all_results, difficulty)
        
        print("\n=== Section 4: Structural Analysis ===")
        components = {
            'entity_f1': 'Entity F1',
            'attribute_f1': 'Attribute F1',
            'relation_f1': 'Relation F1',
            'filter_f1': 'Filter F1',
            'aggregation_f1': 'Aggregation F1',
            'return_column_f1': 'Return Column F1'
        }
        for comp, label in components.items():
            print(f"  Processing {label}...")
            self.plot_structural_component(all_results, comp, label)
        
        print("  Generating radar chart...")
        self.plot_structural_radar(all_results)
        
        print("\n=== Section 5: Result Accuracy ===")
        self.plot_execution_accuracy_heatmap(all_results)
        self.plot_precision_recall_analysis(all_results)
        
        print("\n=== Section 6: Error Analysis ===")
        self.plot_error_distribution(all_results)
        self.plot_error_by_dataset_heatmap(all_results)
        self.plot_error_by_difficulty(all_results)
        
        print("\n=== Section 7: Comparative Synthesis ===")
        self.plot_parse_success_comparison(all_results)
        self.plot_final_synthesis_table(all_results)
        
        print(f"\n✅ All plots saved to: {self.output_dir}")
        print(f"✅ LaTeX tables saved to: {self.output_dir}")


def main():
    """Main entry point"""
    results_dir = PROJECT_ROOT / "results"
    output_dir = PROJECT_ROOT / "thesis_plots"
    
    plotter = ThesisPlotter(results_dir, output_dir)
    plotter.generate_all_plots()


if __name__ == "__main__":
    main()