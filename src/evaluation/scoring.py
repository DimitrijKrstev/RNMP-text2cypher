from re import sub
from logging import getLogger
import sqlparse

from database.neo4j import query_neo4j
from database.sqlite import query_sqlite
from database.duckdb import query_duckdb
from models import Task, TaskResult, TaskType, SQLQueryAnalyzer, CypherQueryAnalyzer
from evaluation.utils import compute_component_f1, compute_result_f1, normalize_filters

logger = getLogger(__name__)

ANALYZERS = {
    TaskType.SQL: SQLQueryAnalyzer(),
    TaskType.CYPHER: CypherQueryAnalyzer()
}

QUERY_DB_BY_TASK_TYPE = {
    TaskType.SQL: query_duckdb,
    TaskType.CYPHER: query_neo4j,
}

def get_task_result(task: Task, model_response: str, task_type: TaskType, db_path: str) -> TaskResult:
    """Evaluate the model response for a given task and return TaskResult"""

    analyzer = ANALYZERS[task_type]
    expected_query = task.get_response_by_task_type(task_type)
    
    parse_success = analyzer.is_valid(model_response)
    
    entities = analyzer.get_entities(model_response)
    attributes = analyzer.get_attributes(model_response)
    relations = analyzer.get_relations(model_response)
    filters = analyzer.get_filters(model_response)
    filters = normalize_filters(filters) if task_type == TaskType.CYPHER else filters
    aggregations = analyzer.get_aggregations(model_response)
    return_columns = analyzer.get_return_columns(model_response)
    
    expected_entities = analyzer.get_entities(expected_query)
    expected_attributes = analyzer.get_attributes(expected_query)
    expected_relations = analyzer.get_relations(expected_query)
    expected_filters = analyzer.get_filters(expected_query)
    expected_filters = normalize_filters(expected_filters) if task_type == TaskType.CYPHER else filters
    expected_aggregations = analyzer.get_aggregations(expected_query)
    expected_return_columns = analyzer.get_return_columns(expected_query)
    
    entity_f1 = compute_component_f1(expected_entities, entities)
    attribute_f1 = compute_component_f1(expected_attributes, attributes)

    expected_relation_set = {
        (r['type'], r.get('source', ''), r.get('target', ''))
        for r in expected_relations
    }
    generated_relation_set = {
        (r['type'], r.get('source', ''), r.get('target', ''))
        for r in relations
    }
    relation_f1 = compute_component_f1(expected_relation_set, generated_relation_set)
    
    filter_f1 = compute_component_f1(expected_filters, filters)
    
    expected_agg_functions = set(expected_aggregations.get('functions', []))
    generated_agg_functions = set(aggregations.get('functions', []))
    aggregation_f1 = compute_component_f1(expected_agg_functions, generated_agg_functions)
    
    return_column_f1 = compute_component_f1(
        set(expected_return_columns),
        set(return_columns)
    )
    
    logger.info(
        f"Extracted - Tables: {entities}\n"
        f", Attributes: {attributes}\n"
        f", Relations: {relations}\n"
        f", Filters: {filters}\n"
        f", Aggregations: {aggregations}\n"
        f", Return Columns: {return_columns}\n"
    )
    
    logger.info(
        f"Component F1 - Entity: {entity_f1:.2f}, Attribute: {attribute_f1:.2f}, "
        f"Relation: {relation_f1:.2f}, Filter: {filter_f1:.2f}, "
        f"Aggregation: {aggregation_f1:.2f}, Return: {return_column_f1:.2f}"
    )
    
    execution_success = False
    execution_accuracy = False
    result_f1 = result_precision = result_recall = 0.0
    
    if parse_success:
        try:
            query_fn = QUERY_DB_BY_TASK_TYPE[task_type]
            
            generated_rows = query_fn(model_response, db_path)
            expected_rows = query_fn(expected_query, db_path)
            
            execution_success = True
            
            execution_accuracy = (generated_rows == expected_rows)
            
            result_metrics = compute_result_f1(expected_rows, generated_rows)
            result_f1 = result_metrics['f1']
            result_precision = result_metrics['precision']
            result_recall = result_metrics['recall']
            
            logger.info(
                f"Execution - Success: {execution_success}, "
                f"Exact Match: {execution_accuracy}, "
                f"F1: {result_f1:.2f}, "
                f"Precision: {result_precision:.2f}, "
                f"Recall: {result_recall:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            execution_success = False
    else:
        logger.info("Skipping execution (parse failed)")
    

    error_flags = []
    
    if not parse_success:
        error_flags.append('syntax_error')
    elif not execution_success:
        error_flags.append('runtime_error')
    else:
        if entity_f1 < 0.5:
            error_flags.append('wrong_entity')
        if attribute_f1 < 0.5:
            error_flags.append('wrong_attribute')
        if relation_f1 < 0.5 and task_type == TaskType.CYPHER:
            error_flags.append('wrong_relation')
        if filter_f1 < 0.5:
            error_flags.append('wrong_filter')
        if aggregation_f1 < 0.5:
            error_flags.append('wrong_aggregation')
        if return_column_f1 < 0.5:
            error_flags.append('wrong_return_columns')
        if not execution_accuracy:
            error_flags.append('result_mismatch')
    
    if not parse_success:
        error_category = 'SYNTAX_ERROR'
    elif not execution_success:
        error_category = 'RUNTIME_ERROR'
    elif execution_accuracy:
        error_category = 'CORRECT'
    elif entity_f1 < 0.5:
        error_category = 'WRONG_ENTITY'
    elif attribute_f1 < 0.5:
        error_category = 'WRONG_ATTRIBUTE'
    elif relation_f1 < 0.5 and task_type == TaskType.CYPHER:
        error_category = 'WRONG_RELATION'
    elif filter_f1 < 0.5:
        error_category = 'WRONG_FILTER'
    elif aggregation_f1 < 0.5:
        error_category = 'WRONG_AGGREGATION'
    elif return_column_f1 < 0.5:
        error_category = 'WRONG_RETURN_COLUMNS'
    else:
        error_category = 'RESULT_MISMATCH'
    
    logger.info(f"Error Category: {error_category}, Flags: {error_flags}")
    

    return TaskResult(
        task=task,
        response=model_response,
        parse_success=parse_success,
        execution_success=execution_success,
        entity_f1=entity_f1,
        attribute_f1=attribute_f1,
        relation_f1=relation_f1 if task_type == TaskType.CYPHER else None,
        filter_f1=filter_f1,
        aggregation_f1=aggregation_f1,
        return_column_f1=return_column_f1,
        execution_accuracy=execution_accuracy,
        result_f1=result_f1,
        result_precision=result_precision,
        result_recall=result_recall,
        error_category=error_category,
        error_flags=error_flags,
        task_type=task_type
    )


def normalize_query(query: str, task_type: TaskType) -> str:
    query = query.strip().lower()

    query = sub(r"\s+", " ", query)

    if task_type == TaskType.SQL:
        parsed = sqlparse.format(
            query,
            keyword_case="lower",
            identifier_case="lower",
            strip_comments=True,
            reindent=False,
        )
        query = sub(r"\s+", " ", parsed).strip()

    elif task_type == TaskType.CYPHER:
        query = sub(r"\s+as\s+\w+", "", query)
        query = query.strip()

    query = query.rstrip(";")

    return query
