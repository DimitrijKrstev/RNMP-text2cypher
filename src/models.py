import sqlglot

from sqlglot import parse_one, ParseError, exp
from dataclasses import dataclass
from enum import StrEnum
from functools import reduce
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, List, Set
from antlr4 import InputStream, CommonTokenStream
from antlr4 import *
from antlr4_cypher import CypherLexer, CypherParser, CypherParserListener
from antlr4.tree.Tree import TerminalNodeImpl
import re



@dataclass(slots=True, frozen=True)
class Task:
    question: str
    sql: str
    cypher: str
    cypher_result: str | None

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            question=data["question"],
            sql=data["sql"],
            cypher=data["cypher"],
            cypher_result=data.get("cypher_result"),
        )

    def to_dict(self):
        return {
            "question": self.question,
            "sql": self.sql,
            "cypher": self.cypher,
            "cypher_result": self.cypher_result,
        }

    def get_response_by_task_type(self, task_type: "TaskType") -> str:
        if task_type == TaskType.SQL:
            return self.sql
        elif task_type == TaskType.CYPHER:
            return self.cypher

    def __hash__(self):
        return hash(self.question)


@dataclass(slots=True, frozen=True)
class TaskResult:
    task: Task
    response: str
    parse_success: bool
    execution_success: bool
    entity_f1: float
    attribute_f1: float
    relation_f1: Optional[float]
    filter_f1: float
    aggregation_f1: float
    return_column_f1: float
    execution_accuracy: bool
    result_f1: float
    result_precision: float
    result_recall: float
    error_category: str
    error_flags: List[str]
    task_type: "TaskType"

    def to_dict(self) -> dict:
        return {
            "question": self.task.question,
            "expected_script": (
                self.task.sql if self.task_type == TaskType.SQL else self.task.cypher
            ),
            "generated_script": self.response,
            "syntaxically_correct": self.parse_success,
            "correct_result": self.execution_success,
            "entity_f1": self.entity_f1,
            "attribute_f1": self.attribute_f1,
            "relation_f1": self.relation_f1,
            "filter_f1": self.filter_f1,
            "aggregation_f1": self.aggregation_f1,
            "return_column_f1": self.return_column_f1,
            "execution_accuracy": self.execution_accuracy,
            "result_f1": self.result_f1,
            "result_precision": self.result_precision,
            "result_recall": self.result_recall,
            "error_category": self.error_category,
            "error_flags": self.error_flags,
        }
    
    @classmethod
    def from_dict(cls, data: dict, task_type: "TaskType") -> "TaskResult":
        """Reconstruct TaskResult from serialized dict"""
        
        task = Task(
            question=data["question"],
            sql=data["expected_script"] if task_type == TaskType.SQL else "",
            cypher=data["expected_script"] if task_type == TaskType.CYPHER else "",
            cypher_result=None
        )
        
        return cls(
            task=task,                                          
            response=data["generated_script"],                  
            parse_success=data["syntaxically_correct"],         
            execution_success=data["correct_result"],          
            entity_f1=data.get("entity_f1", 0.0),
            attribute_f1=data.get("attribute_f1", 0.0),
            relation_f1=data.get("relation_f1"),
            filter_f1=data.get("filter_f1", 0.0),
            aggregation_f1=data.get("aggregation_f1", 0.0),
            return_column_f1=data.get("return_column_f1", 0.0),
            execution_accuracy=data.get("execution_accuracy", False),
            result_f1=data.get("result_f1", 0.0),
            result_precision=data.get("result_precision", 0.0),
            result_recall=data.get("result_recall", 0.0),
            error_category=data.get("error_category", "UNKNOWN"),
            error_flags=data.get("error_flags", []),
            task_type=task_type
        )


class DatasetName(StrEnum):
    REL_F1 = "rel-f1"
    REL_STACK = "rel-stack"
    REL_TRIAL = "rel-trial"

class TaskDifficulty(StrEnum):
    EASY = "easy"
    INTERMEDIATE = "intermediate"
    HARD = "hard"


class TaskType(StrEnum):
    SQL = "SQL"
    CYPHER = "Cypher"


@dataclass(slots=True, frozen=True)
class SQLTableWithHeaders:
    table: str
    columns: list[str]

    def __repr__(self) -> str:
        cols = reduce(
            lambda acc, col: f"{acc},{col}", self.columns[1:], self.columns[0]
        )
        return f"{self.table}({cols})"


@dataclass
class GraphEntity:
    name: str
    properties: list[str]


class QueryAnalyzer(ABC):
    """Abstract base class for query analyzers."""

    @abstractmethod
    def is_valid(self, query: str) -> bool:
        """Check if the query is valid."""
        pass

    @abstractmethod
    def get_entities(self, query: str, ) -> set[str]:
        """Extract entities from the query."""
        pass

    @abstractmethod
    def get_attributes(self, query: str) -> set[str]:
        """Extract attributes from the query."""
        pass

    @abstractmethod
    def get_relations(self, query: str) -> any:
        """Extract relations from the query."""
        pass

    @abstractmethod
    def get_filters(self, query: str) -> set[str]:
        """Extract filters from the query."""
        pass

    @abstractmethod
    def get_aggregations(self, query: str) -> set[str]:
        """Extract aggregations from the query."""
        pass

    @abstractmethod
    def get_orderings(self, query: str) -> set[str]:
        """Extract orderings from the query."""
        pass

class SQLQueryAnalyzer(QueryAnalyzer):
    """SQL query analyzer implementation."""

    def __init__(self, dialect: str = "duckdb"):
        self.dialect = dialect

    def _parse(self, query: str) -> Optional[exp.Expression]:
            try:
                return parse_one(query, dialect=self.dialect)
            except ParseError:
                return None
    
    def is_valid(self, query: str) -> bool:
        return self._parse(query) is not None
        

    def get_entities(self, query: str) -> set[str]:
        parsed = self._parse(query)
        return {t.name.lower() for t in parsed.find_all(exp.Table)} if parsed else set()

    def get_attributes(self, query: str) -> set[str]:
        parsed = self._parse(query)
        if not parsed:
            return set()
        
        return {f"{c.table.lower()},{c.name.lower()}" if c.table is not None else c.name.lower() 
                for c in parsed.find_all(exp.Column)} if parsed else set()

    def get_relations(self, query: str) -> List[Dict]:
        parsed = self._parse(query)
        if not parsed:
            return set()
        
        return [
            {
                "type": j.side or "INNER",
                "target": j.this.name if isinstance(j.this, exp.Table) else str(j.this),
                "condition": j.args.get("on").sql() if j.args.get("on") else None
            }
            for j in parsed.find_all(exp.Join)
        ]

    def get_filters(self, query: str) -> set[str]:
        parsed = self._parse(query)
        if not parsed:
            return set()
        
        where = parsed.find(exp.Where)
        return {c.sql().lower() for c in where.find_all(exp.Condition)} if where else set()

    def get_aggregations(self, query: str) -> set[str]:
        parsed = self._parse(query)
        if not parsed:
            return {"functions": [], "group_by": [], "having": None}
        
        group = parsed.find(exp.Group)
        having = parsed.find(exp.Having)
        
        return {
            "functions": [a.__class__.__name__ for a in parsed.find_all(exp.AggFunc)],
            "group_by": [e.sql().lower() for e in group.expressions] if group else [],
            "having": having.sql().lower() if having else None
        }

    def get_orderings(self, query: str) -> set[str]:
        parsed = self._parse(query)
        if not parsed:
            return []
        
        order = parsed.find(exp.Order)
        if not order:
            return []
        
        return [
            {
                "column": e.this.sql().lower(),
                "direction": "DESC" if e.args.get("desc") else "ASC"
            }
            for e in order.expressions
        ]
    
    def get_return_columns(self, query: str) -> List[str]:
        """Get only SELECT columns"""
        try:
            tree = parse_one(query, read='duckdb')
            columns = []
            
            # Find the SELECT node
            for select in tree.find_all(exp.Select):
                # Everything in select.expressions is a return column
                for expression in select.expressions:
                    # Decide how to represent it:
                    if isinstance(expression, exp.Alias):
                        # It has an alias, use that (e.g., "COUNT(*) AS races" → "races")
                        columns.append(expression.alias)
                    else:
                        # No alias, use the full expression (e.g., "d.forename" → "d.forename")
                        columns.append(expression.sql())
                        
            return columns
        except Exception:
            return []


class SimpleCypherExtractor(CypherParserListener):
    """ANTLR4 listener for extracting semantic elements from Cypher queries."""
    
    def __init__(self, debug=False):
        # Core extraction
        self.entities = set()
        self.relationships = []
        self.attributes = set()
        self.filters = set()
        self.aggregations = set()
        self.orderings = []
        self.return_columns = [] 
        
        # State tracking
        self.var_to_label = {}
        self.current_pattern_labels = []
        self.pending_rel_type = None
        self.pending_rel_direction = None
        self.in_return_clause = False
        
        # Debug
        self.debug = debug
        
    def _debug(self, msg):
        if self.debug:
            print(f"[DEBUG] {msg}")
        
    def enterNodePattern(self, ctx):
        """
        Extract from NodePatternContext.
        Structure: (symbol?) (nodeLabels?) (properties?)
        """
        variable = None
        labels = []
        
        # Get variable name
        if ctx.symbol():
            variable = ctx.symbol().getText()
        
        # Get node labels
        if ctx.nodeLabels():
            labels_text = ctx.nodeLabels().getText()
            labels = [l.strip() for l in labels_text.split(':') if l.strip()]
            
            # Add to entities
            for label in labels:
                self.entities.add(label.lower())
            
            # Map variable to label for later reference
            if variable and labels:
                self.var_to_label[variable] = labels[0]
            
            # Track labels in pattern sequence
            if labels:
                self.current_pattern_labels.append(labels[0].lower())
        else:
            # Node has no label - check if it's a known variable
            if variable and variable in self.var_to_label:
                known_label = self.var_to_label[variable]
                self.current_pattern_labels.append(known_label.lower())
        
        # Build relationship if we have pending type and both nodes
        if self.pending_rel_type and len(self.current_pattern_labels) >= 2:
            left_node = self.current_pattern_labels[-2]
            right_node = self.current_pattern_labels[-1]
            
            # Determine source and target based on arrow direction
            if self.pending_rel_direction == 'left':
                source = right_node
                target = left_node
            elif self.pending_rel_direction == 'right':
                source = left_node
                target = right_node
            else:
                source = left_node
                target = right_node
            
            self.relationships.append({
                "type": self.pending_rel_type,
                "source": source,
                "target": target
            })
            self.pending_rel_type = None
            self.pending_rel_direction = None
        
        # Extract inline properties from node
        if ctx.properties():
            props_text = ctx.properties().getText()
            prop_names = re.findall(r'(\w+)\s*:', props_text)
            for prop in prop_names:
                entity = None
                if variable and variable in self.var_to_label:
                    entity = self.var_to_label[variable]
                elif labels:
                    entity = labels[0]
                    
                if entity:
                    self.attributes.add(f"{entity.lower()},{prop.lower()}")
    
    def enterPatternElem(self, ctx):
        """Reset pattern tracking for each pattern element."""
        self.current_pattern_labels = []
        self.pending_rel_type = None
        self.pending_rel_direction = None
    
    def enterRelationshipPattern(self, ctx):
        """
        Extract from RelationshipPatternContext with direction tracking.
        """
        full_text = ctx.getText()
        
        if full_text.startswith('<-'):
            self.pending_rel_direction = 'left'
        elif '->' in full_text:
            self.pending_rel_direction = 'right'
        else:
            self.pending_rel_direction = 'both'
        
        if ctx.relationDetail():
            detail = ctx.relationDetail()
            
            if detail.relationshipTypes():
                types_text = detail.relationshipTypes().getText()
                rel_types = [t.strip() for t in types_text.replace(':', '').split('|') if t.strip()]
                
                if rel_types:
                    self.pending_rel_type = rel_types[0]
                    
                    if detail.properties():
                        props_text = detail.properties().getText()
                        prop_names = re.findall(r'(\w+)\s*:', props_text)
                        for prop in prop_names:
                            self.attributes.add(f"{self.pending_rel_type.lower()},{prop.lower()}")
    
    def enterWhere(self, ctx):
        """
        Extract from WhereContext.
        Structure: WHERE expression
        """
        if ctx.expression():
            expr_text = ctx.expression().getText()
            
            # Add the FULL filter expression
            filter_expr = expr_text.strip()
            if filter_expr:
                self.filters.add(filter_expr)
            
            # Also extract individual property accesses for attributes
            prop_matches = re.findall(r'(\w+)\.(\w+)', expr_text)
            for var, prop in prop_matches:
                if var in self.var_to_label:
                    entity = self.var_to_label[var]
                    self.attributes.add(f"{entity.lower()},{prop.lower()}")
    
    def enterReturn(self, ctx):
        """Mark that we're entering a RETURN clause"""
        self._debug(f"enterReturn called, context: {ctx.getText()[:100]}")
        self.in_return_clause = True
        
        # ROBUST extraction: get text and parse it manually
        return_text = ctx.getText()
        self._debug(f"Full RETURN text: {return_text}")
        
        # Remove RETURN keyword and anything after ORDER/LIMIT/SKIP
        items_text = re.sub(r'^RETURN\s+(DISTINCT\s+)?', '', return_text, flags=re.IGNORECASE)
        items_text = re.split(r'\s+(ORDER\s+BY|LIMIT|SKIP)\s+', items_text, flags=re.IGNORECASE)[0]
        
        self._debug(f"Items text after cleanup: {items_text}")
        
        # Split by commas (but not inside parentheses or brackets)
        items = self._smart_split(items_text)
        
        self._debug(f"Split items: {items}")
        
        for item in items:
            item = item.strip()
            if not item:
                continue
            
            # Check for AS alias
            as_match = re.search(r'(.+?)\s+AS\s+(\w+)', item, re.IGNORECASE)
            if as_match:
                self.return_columns.append(as_match.group(2))
                self._debug(f"Added return column (with AS): {as_match.group(2)}")
            else:
                self.return_columns.append(item)
                self._debug(f"Added return column: {item}")
    
    def _smart_split(self, text):
        """Split by comma, but not inside parentheses, brackets, or braces."""
        items = []
        current = []
        depth = 0
        
        for char in text:
            if char in '([{':
                depth += 1
                current.append(char)
            elif char in ')]}':
                depth -= 1
                current.append(char)
            elif char == ',' and depth == 0:
                items.append(''.join(current))
                current = []
            else:
                current.append(char)
        
        if current:
            items.append(''.join(current))
        
        return items

    def exitReturn(self, ctx):
        """Mark that we're exiting a RETURN clause"""
        self._debug("exitReturn called")
        self.in_return_clause = False
    
    def enterProjectionBody(self, ctx):
        """
        Extract aggregations, orderings, and property accesses from ProjectionBodyContext.
        """
        body_text = ctx.getText()
        
        # Extract aggregation functions (including SIZE)
        agg_funcs = re.findall(r'\b(COUNT|SUM|AVG|MIN|MAX|COLLECT|SIZE)\s*\(', 
                              body_text, re.IGNORECASE)
        for func in agg_funcs:
            self.aggregations.add(func.upper())
        
        # Extract property accesses from projection items
        prop_matches = re.findall(r'(\w+)\.(\w+)', body_text)
        for var, prop in prop_matches:
            if var in self.var_to_label:
                entity = self.var_to_label[var]
                self.attributes.add(f"{entity.lower()},{prop.lower()}")
        
        # Check for ORDER BY
        if ctx.orderSt():
            order_text = ctx.orderSt().getText()
            
            # Remove ORDERBY keyword
            items_text = re.sub(r'ORDERBY', '', order_text, flags=re.IGNORECASE)
            
            # Split by comma for multiple items
            items = items_text.split(',')
            
            for item in items:
                item = item.strip()
                if not item:
                    continue
                
                # Check for DESC/ASC
                direction = "ASC"
                if re.search(r'DESC', item, re.IGNORECASE):
                    direction = "DESC"
                    item = re.sub(r'(DESC|ASC)', '', item, flags=re.IGNORECASE).strip()
                elif re.search(r'ASC', item, re.IGNORECASE):
                    direction = "ASC"
                    item = re.sub(r'(DESC|ASC)', '', item, flags=re.IGNORECASE).strip()
                
                if item:
                    self.orderings.append({
                        "column": item.lower(),
                        "direction": direction
                    })


class CypherQueryAnalyzer(QueryAnalyzer):
    """Cypher query analyzer using ANTLR4 listener pattern."""

    def __init__(self, debug=False):
        self.debug = debug
        self._cache = {}
    
    def _parse_and_extract(self, query: str) -> Optional[Dict[str, Any]]:
        """Parse query and extract metadata (with caching)."""
        
        if query in self._cache:
            return self._cache[query]
        
        try:
            lexer = CypherLexer(InputStream(query))
            parser = CypherParser(CommonTokenStream(lexer))
            tree = parser.script()
            
            extractor = SimpleCypherExtractor(debug=self.debug)
            walker = ParseTreeWalker()
            walker.walk(extractor, tree)
            
            result = {
                'entities': extractor.entities,
                'relationships': extractor.relationships,
                'attributes': extractor.attributes,
                'filters': extractor.filters,
                'aggregations': extractor.aggregations,
                'orderings': extractor.orderings,
                'return_columns': extractor.return_columns
            }
            
            self._cache[query] = result
            return result
            
        except Exception as e:
            if self.debug:
                print(f"Parse error: {e}")
            self._cache[query] = None  
            return None

    def is_valid(self, query: str) -> bool:
        """Check if query is syntactically valid."""
        try:
            input_stream = InputStream(query)
            lexer = CypherLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = CypherParser(token_stream)
            parser.removeErrorListeners()
            tree = parser.script()
            return parser.getNumberOfSyntaxErrors() == 0
        except Exception:
            return False

    def get_entities(self, query: str) -> Set[str]:
        """Get node labels (entities) from query."""
        result = self._parse_and_extract(query)  # Returns dict or None
        if result is None:
            return set()
        return result['entities']  # ← Access dict key

    def get_attributes(self, query: str) -> Set[str]:
        """Get ALL properties referenced anywhere in query."""
        result = self._parse_and_extract(query)
        if result is None:
            return set()
        return result['attributes']

    def get_relations(self, query: str) -> List[Dict]:
        """Get relationships from query."""
        result = self._parse_and_extract(query)
        if result is None:
            return []
        return result['relationships']

    def get_return_columns(self, query: str) -> List[str]:
        """
        Extract RETURN clause items using regex (ANTLR listener unreliable for this).
        """
        if not self.is_valid(query):
            return []
        
        clean = re.sub(r'//.*?$|/\*.*?\*/', '', query, flags=re.MULTILINE|re.DOTALL)
        clean = ' '.join(clean.split())
        
        parts = re.split(r'\bRETURN\b', clean, flags=re.IGNORECASE)
        if len(parts) < 2:
            return []
        
        return_part = parts[-1]
        return_part = re.split(r'\b(ORDER\s+BY|LIMIT|SKIP|UNION)\b', 
                               return_part, flags=re.IGNORECASE)[0]
        return_part = re.sub(r'^\s*DISTINCT\s+', '', return_part, flags=re.IGNORECASE)
        
        def _split_by_comma(text: str) -> List[str]:
            """Split by comma, respecting parentheses/brackets."""
            items, current, depth = [], [], 0
            for char in text:
                if char in '([{': depth += 1
                elif char in ')]}': depth -= 1
                elif char == ',' and depth == 0:
                    items.append(''.join(current).strip())
                    current = []
                    continue
                current.append(char)
            if current:
                items.append(''.join(current).strip())
            return items

        items = _split_by_comma(return_part)
        
        result = []
        for item in items:
            item = item.strip()
            if not item:
                continue
            # Handle AS aliases
            as_match = re.search(r'^(.+?)\s+AS\s+(\w+)$', item, re.IGNORECASE)
            result.append(as_match.group(2) if as_match else item)
        
        return result

    def get_filters(self, query: str) -> Set[str]:
        """Get WHERE clause filter expressions."""
        result = self._parse_and_extract(query)
        if result is None:
            return set()
        return result['filters']

    def get_aggregations(self, query: str) -> Dict[str, Any]:
        """Get aggregation functions used in query."""
        result = self._parse_and_extract(query)
        if result is None:
            return {"functions": [], "group_by": [], "having": None}
        return {
            "functions": sorted(list(result['aggregations'])),
            "group_by": [],
            "having": None
        }

    def get_orderings(self, query: str) -> List[Dict]:
        """Get ORDER BY clauses."""
        result = self._parse_and_extract(query)
        if result is None:
            return []
        return result['orderings']

    def analyze(self, query: str) -> Dict[str, Any]:
        """Get all metadata in a single call."""
        result = self._parse_and_extract(query)
        if result is None:
            return {
                "entities": [],
                "attributes": [],
                "return_columns": [],
                "relationships": [],
                "filters": [],
                "aggregations": {"functions": [], "group_by": [], "having": None},
                "orderings": [],
                "valid": False
            }
        
        return {
            "entities": list(result['entities']),
            "attributes": list(result['attributes']),
            "return_columns": self.get_return_columns(query),  # Use the regex method
            "relationships": result['relationships'],
            "filters": list(result['filters']),
            "aggregations": {
                "functions": sorted(list(result['aggregations'])),
                "group_by": [],
                "having": None
            },
            "orderings": result['orderings'],
            "valid": True
        }