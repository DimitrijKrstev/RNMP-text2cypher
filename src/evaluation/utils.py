import re
from typing import Set
from logging import getLogger
from models import Task, TaskType, TaskResult

logger = getLogger(__name__)

def compute_component_f1(expected_set, generated_set):
    """
    F1 for query components (entities, attributes, relations, etc.)
    Input: Sets of strings
    """
    tp = len(expected_set & generated_set)
    fp = len(generated_set - expected_set)
    fn = len(expected_set - generated_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return f1

def compute_result_f1(expected_rows, generated_rows):
    """F1 on query results with normalized comparison."""
    
    def normalize_value(value):
        """Normalize to comparable primitive."""
        if value is None or value == '\\N' or value == 'null':
            return None
        elif isinstance(value, float):
            return int(value) if value == int(value) else round(value, 6)
        elif isinstance(value, str):
            try:
                f = float(value)
                return int(f) if f == int(f) else round(f, 6)
            except ValueError:
                return value.strip()
        return value
    
    def extract_values(row):
        """Extract leaf values from nested structures."""
        values = []
        
        def recurse(obj):
            if obj is None:
                values.append(None)
            elif isinstance(obj, dict):
                skip_keys = {'element_id', 'labels', 'id'}  
                for k, v in sorted(obj.items()):
                    if k.lower() not in skip_keys:
                        recurse(v)
            elif isinstance(obj, (list, tuple)):
                for item in obj:
                    recurse(item)
            else:
                values.append(normalize_value(obj))
        
        recurse(row)
        return tuple(sorted(str(v) for v in values if v is not None))
    
    def to_set(rows):
        if not rows:
            return set()
        return {extract_values(row) for row in rows}
    
    ref_set = to_set(expected_rows)
    gen_set = to_set(generated_rows)
    
    tp = len(ref_set & gen_set)
    fp = len(gen_set - ref_set)
    fn = len(ref_set - gen_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {'f1': f1, 'precision': precision, 'recall': recall}

def normalize_filters(filters: Set[str]) -> Set[str]:
    """
    Split compound filter expressions into atomic predicates.
    
    'A AND B AND C' → {'A', 'B', 'C'}
    """

    atomic_predicates = set()
    
    for filter_expr in filters:
        parts = re.split(r'\s+(?:AND|OR)\s+', filter_expr, flags=re.IGNORECASE)
        
        for part in parts:
            part = part.strip()
            while part.startswith('(') and part.endswith(')'):
                part = part[1:-1].strip()
            
            if part:
                normalized = ' '.join(part.lower().split())
                atomic_predicates.add(normalized)
    
    return atomic_predicates


def build_user_prompt(question: str) -> str:
    return f"Write a query to: {question}"


def build_sql_system_prompt(schema: str) -> str:
    return (
        "You are a Text-to-SQL expert. Return ONLY valid SQL.\n"
        "No explanations, no markdown, no code fences.\n\n"
        "FORMAT RULES:\n"
        "• NO table aliases: FROM drivers JOIN results ON drivers.driverId = results.driverId\n"
        "• NO AS keyword for column aliases: SELECT COUNT(*) (NOT COUNT(*) AS total)\n"
        "• ALWAYS prefix columns with table name: SELECT drivers.forename, results.points\n"
        "• Use single quotes for strings: WHERE drivers.nationality = 'British'\n"
        "• Date format: 'YYYY-MM-DD HH:MM:SS'\n"
        "• Use LIKE '%term%' for partial string matching\n"
        "• Use IN ('val1', 'val2') for multiple values\n"
        "• Use BETWEEN x AND y for ranges\n"
        "• GROUP BY must include all non-aggregated SELECT columns\n\n"
        f"Schema:\n{schema}"
    )


def build_cypher_system_prompt(schema: str) -> str:
    return (
        "You are a Text-to-Cypher expert. Return ONLY valid Cypher.\n"
        "No explanations, no markdown, no code fences.\n\n"
        "FORMAT RULES:\n"
        "• Variables are singular lowercase, labels are plural from schema: (driver:drivers), (study:studies)\n"
        "• NO AS keyword in RETURN: RETURN count(*) (NOT count(*) AS total)\n"
        "• AS is REQUIRED in WITH clause for aggregations: WITH driver, count(*) AS cnt\n"
        "• DON'T return bare node variables: RETURN driver.forename, driver.surname (NOT RETURN driver)\n"
        "• ALWAYS prefix properties with variable in both WHERE and RETURN clauses\n"
        "• Use single quotes for strings: WHERE driver.nationality = 'British'\n"
        "• Use CONTAINS for partial string matching: WHERE name CONTAINS 'term'\n"
        "• Use IN with square brackets: WHERE x IN ['val1', 'val2']\n"
        "• No BETWEEN - expand to: WHERE x >= val1 AND x <= val2\n"
        "• Aggregation functions are lowercase: count(*), sum(x), avg(x)\n"
        "• For STRING fields storing numbers, use toInteger() or toFloat()\n"
        "• Relationship patterns: -[:REL]-> or <-[:REL]-\n\n"
        f"Schema:\n{schema}"
    )
