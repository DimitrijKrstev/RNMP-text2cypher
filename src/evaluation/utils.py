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
    """
    F1 for actual query results (rows returned from DB)
    Input: Lists of tuples (rows)
    """
    ref_set = set(map(tuple, expected_rows))
    gen_set = set(map(tuple, generated_rows))
    
    tp = len(ref_set & gen_set)
    fp = len(gen_set - ref_set)
    fn = len(ref_set - gen_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {'f1': f1, 'precision': precision, 'recall': recall}

