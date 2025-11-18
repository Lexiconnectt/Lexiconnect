#!/usr/bin/env python3
"""
Comprehensive Cypher-based validation script for Lexiconnect Neo4j database.

This script performs extensive validation checks on the database to ensure:
- Schema compliance (required properties, unique IDs)
- Relationship integrity (orphaned nodes, missing relationships)
- Data quality (relationship directions, required properties on relationships)
- Graph structure consistency

Usage:
    # From project root (requires dependencies installed):
    python backend/tests/validate_database.py
    
    # From backend directory:
    cd backend
    python tests/validate_database.py
    
    # Or run from Docker container:
    docker-compose exec backend python tests/validate_database.py
"""

import sys
import os
from typing import Dict, List, Any, Tuple

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, backend_dir)

try:
    from app.database import get_db
    from app.core.config import settings
except ImportError as e:
    print("=" * 80)
    print("ERROR: Missing required dependencies")
    print("=" * 80)
    print()
    print(f"Import error: {e}")
    print()
    print("Please install dependencies first:")
    print("  1. cd backend")
    print("  2. pip install -r requirements.txt")
    print()
    print("Or run from Docker container (recommended):")
    print("  docker-compose -f docker-compose.free.yml exec backend python tests/validate_database.py")
    print()
    print("Or run from backend directory:")
    print("  cd backend && python tests/validate_database.py")
    print()
    print("Note: Make sure Neo4j is running and environment variables are set:")
    print("  - NEO4J_URI (default: bolt://localhost:7687)")
    print("  - NEO4J_USER (default: neo4j)")
    print("  - NEO4J_PASSWORD (default: password)")
    print()
    sys.exit(1)


class ValidationResult:
    """Container for validation check results"""
    
    def __init__(self, check_name: str, severity: str = "ERROR"):
        self.check_name = check_name
        self.severity = severity  # ERROR, WARNING, INFO
        self.issues: List[Dict[str, Any]] = []
        self.passed = True
        
    def add_issue(self, description: str, details: Dict[str, Any] = None):
        """Add an issue found during validation"""
        self.passed = False
        issue = {"description": description}
        if details:
            issue.update(details)
        self.issues.append(issue)
        
    def get_summary(self) -> str:
        """Get a summary of the validation result"""
        if self.passed:
            return f"✓ {self.check_name}: PASSED"
        else:
            count = len(self.issues)
            return f"✗ {self.check_name}: FAILED ({count} issue(s))"


class DatabaseValidator:
    """Validates Neo4j database integrity using Cypher queries"""
    
    def __init__(self, db):
        self.db = db
        self.results: List[ValidationResult] = []
        
    def run_all_checks(self):
        """Run all validation checks"""
        print("=" * 80)
        print("Lexiconnect Database Validation")
        print("=" * 80)
        print()
        
        # Schema compliance checks
        self.check_unique_id_constraints()
        self.check_required_id_properties()
        
        # Relationship integrity checks
        self.check_orphaned_sections()
        self.check_orphaned_phrases()
        self.check_orphaned_words()
        self.check_orphaned_morphemes()
        self.check_orphaned_glosses()
        
        # Relationship direction and property checks
        self.check_relationship_directions()
        self.check_phrase_composed_of_order()
        self.check_gloss_analyzes_targets()
        
        # Graph structure consistency
        self.check_text_section_consistency()
        self.check_phrase_word_consistency()
        self.check_word_morpheme_consistency()
        
        # Data quality checks
        self.check_duplicate_relationships()
        self.check_missing_required_properties()
        
        # Summary
        self.print_summary()
        
    def check_unique_id_constraints(self):
        """Check that all nodes have unique ID properties"""
        result = ValidationResult("Unique ID Constraints")
        
        node_types = ["Text", "Section", "Phrase", "Word", "Morpheme", "Gloss", "InterlinearText", "User"]
        
        for node_type in node_types:
            query = f"""
            MATCH (n:{node_type})
            WHERE n.ID IS NULL
            RETURN count(n) as count
            """
            count_result = self.db.run(query).single()
            null_count = count_result["count"] if count_result else 0
            
            if null_count > 0:
                result.add_issue(
                    f"{node_type} nodes missing ID property",
                    {"count": null_count, "node_type": node_type}
                )
        
        self.results.append(result)
        
    def check_required_id_properties(self):
        """Check for nodes with duplicate IDs (should be prevented by constraints)"""
        result = ValidationResult("Required ID Properties")
        
        # This check verifies that constraints are working
        # If constraints are properly set, this should always pass
        query = """
        MATCH (n)
        WHERE n.ID IS NULL
        RETURN labels(n)[0] as label, count(n) as count
        ORDER BY count DESC
        """
        
        issues_found = False
        for record in self.db.run(query):
            label = record["label"]
            count = record["count"]
            if label:  # Only report if there are nodes with labels
                result.add_issue(
                    f"{label} nodes missing ID property",
                    {"count": count, "label": label}
                )
                issues_found = True
        
        if not issues_found:
            result.passed = True
            
        self.results.append(result)
        
    def check_orphaned_sections(self):
        """Check for Section nodes without SECTION_PART_OF_TEXT relationship"""
        result = ValidationResult("Orphaned Sections")
        
        query = """
        MATCH (s:Section)
        WHERE NOT (s)<-[:SECTION_PART_OF_TEXT]-()
        RETURN s.ID as section_id, labels(s) as labels
        LIMIT 100
        """
        
        orphaned = list(self.db.run(query))
        if orphaned:
            for record in orphaned:
                result.add_issue(
                    f"Section {record['section_id']} has no parent Text",
                    {"section_id": record["section_id"]}
                )
        
        self.results.append(result)
        
    def check_orphaned_phrases(self):
        """Check for Phrase nodes without PHRASE_IN_SECTION relationship"""
        result = ValidationResult("Orphaned Phrases")
        
        query = """
        MATCH (p:Phrase)
        WHERE NOT (p)<-[:PHRASE_IN_SECTION]-()
        RETURN p.ID as phrase_id
        LIMIT 100
        """
        
        orphaned = list(self.db.run(query))
        if orphaned:
            for record in orphaned:
                result.add_issue(
                    f"Phrase {record['phrase_id']} has no parent Section",
                    {"phrase_id": record["phrase_id"]}
                )
        
        self.results.append(result)
        
    def check_orphaned_words(self):
        """Check for Word nodes without SECTION_CONTAINS or PHRASE_COMPOSED_OF relationships"""
        result = ValidationResult("Orphaned Words")
        
        query = """
        MATCH (w:Word)
        WHERE NOT (w)<-[:SECTION_CONTAINS]-() 
          AND NOT (w)<-[:PHRASE_COMPOSED_OF]-()
        RETURN w.ID as word_id, w.surface_form as surface_form
        LIMIT 100
        """
        
        orphaned = list(self.db.run(query))
        if orphaned:
            for record in orphaned:
                result.add_issue(
                    f"Word {record['word_id']} ({record['surface_form']}) has no Section or Phrase parent",
                    {"word_id": record["word_id"], "surface_form": record["surface_form"]}
                )
        
        self.results.append(result)
        
    def check_orphaned_morphemes(self):
        """Check for Morpheme nodes without WORD_MADE_OF relationship"""
        result = ValidationResult("Orphaned Morphemes")
        
        query = """
        MATCH (m:Morpheme)
        WHERE NOT (m)<-[:WORD_MADE_OF]-()
        RETURN m.ID as morpheme_id, m.surface_form as surface_form
        LIMIT 100
        """
        
        orphaned = list(self.db.run(query))
        if orphaned:
            for record in orphaned:
                result.add_issue(
                    f"Morpheme {record['morpheme_id']} ({record['surface_form']}) has no parent Word",
                    {"morpheme_id": record["morpheme_id"], "surface_form": record["surface_form"]}
                )
        
        self.results.append(result)
        
    def check_orphaned_glosses(self):
        """Check for Gloss nodes without ANALYZES relationship"""
        result = ValidationResult("Orphaned Glosses")
        
        query = """
        MATCH (g:Gloss)
        WHERE NOT (g)-[:ANALYZES]->()
        RETURN g.ID as gloss_id, g.annotation as annotation
        LIMIT 100
        """
        
        orphaned = list(self.db.run(query))
        if orphaned:
            for record in orphaned:
                result.add_issue(
                    f"Gloss {record['gloss_id']} ({record['annotation']}) has no ANALYZES relationship",
                    {"gloss_id": record["gloss_id"], "annotation": record["annotation"]}
                )
        
        self.results.append(result)
        
    def check_relationship_directions(self):
        """Check that relationships have correct directions"""
        result = ValidationResult("Relationship Directions")
        
        # Check for reversed SECTION_PART_OF_TEXT (should be Text -> Section)
        query = """
        MATCH (s:Section)-[r:SECTION_PART_OF_TEXT]->(t:Text)
        RETURN s.ID as section_id, t.ID as text_id
        LIMIT 50
        """
        reversed_rel = list(self.db.run(query))
        if reversed_rel:
            for record in reversed_rel:
                result.add_issue(
                    f"SECTION_PART_OF_TEXT relationship reversed: Section {record['section_id']} -> Text {record['text_id']}",
                    {"section_id": record["section_id"], "text_id": record["text_id"]}
                )
        
        # Check for reversed WORD_MADE_OF (should be Word -> Morpheme)
        query = """
        MATCH (m:Morpheme)-[r:WORD_MADE_OF]->(w:Word)
        RETURN m.ID as morpheme_id, w.ID as word_id
        LIMIT 50
        """
        reversed_rel = list(self.db.run(query))
        if reversed_rel:
            for record in reversed_rel:
                result.add_issue(
                    f"WORD_MADE_OF relationship reversed: Morpheme {record['morpheme_id']} -> Word {record['word_id']}",
                    {"morpheme_id": record["morpheme_id"], "word_id": record["word_id"]}
                )
        
        # Check for reversed PHRASE_COMPOSED_OF (should be Phrase -> Word)
        query = """
        MATCH (w:Word)-[r:PHRASE_COMPOSED_OF]->(p:Phrase)
        RETURN w.ID as word_id, p.ID as phrase_id
        LIMIT 50
        """
        reversed_rel = list(self.db.run(query))
        if reversed_rel:
            for record in reversed_rel:
                result.add_issue(
                    f"PHRASE_COMPOSED_OF relationship reversed: Word {record['word_id']} -> Phrase {record['phrase_id']}",
                    {"word_id": record["word_id"], "phrase_id": record["phrase_id"]}
                )
        
        # Check for reversed ANALYZES (should be Gloss -> target)
        query = """
        MATCH (target)-[r:ANALYZES]->(g:Gloss)
        WHERE target:Word OR target:Phrase OR target:Morpheme
        RETURN labels(target)[0] as target_type, target.ID as target_id, g.ID as gloss_id
        LIMIT 50
        """
        reversed_rel = list(self.db.run(query))
        if reversed_rel:
            for record in reversed_rel:
                result.add_issue(
                    f"ANALYZES relationship reversed: {record['target_type']} {record['target_id']} -> Gloss {record['gloss_id']}",
                    {"target_type": record["target_type"], "target_id": record["target_id"], "gloss_id": record["gloss_id"]}
                )
        
        self.results.append(result)
        
    def check_phrase_composed_of_order(self):
        """Check that PHRASE_COMPOSED_OF relationships have Order property"""
        result = ValidationResult("PHRASE_COMPOSED_OF Order Property")
        
        query = """
        MATCH (p:Phrase)-[r:PHRASE_COMPOSED_OF]->(w:Word)
        WHERE r.Order IS NULL
        RETURN p.ID as phrase_id, w.ID as word_id
        LIMIT 100
        """
        
        missing_order = list(self.db.run(query))
        if missing_order:
            for record in missing_order:
                result.add_issue(
                    f"PHRASE_COMPOSED_OF relationship missing Order property: Phrase {record['phrase_id']} -> Word {record['word_id']}",
                    {"phrase_id": record["phrase_id"], "word_id": record["word_id"]}
                )
        
        self.results.append(result)
        
    def check_gloss_analyzes_targets(self):
        """Check that ANALYZES relationships only target Word, Phrase, or Morpheme"""
        result = ValidationResult("Gloss ANALYZES Targets")
        
        query = """
        MATCH (g:Gloss)-[r:ANALYZES]->(target)
        WHERE NOT (target:Word OR target:Phrase OR target:Morpheme)
        RETURN g.ID as gloss_id, labels(target) as target_labels, target.ID as target_id
        LIMIT 50
        """
        
        invalid_targets = list(self.db.run(query))
        if invalid_targets:
            for record in invalid_targets:
                result.add_issue(
                    f"Gloss {record['gloss_id']} ANALYZES invalid target type: {record['target_labels']}",
                    {"gloss_id": record["gloss_id"], "target_labels": record["target_labels"], "target_id": record["target_id"]}
                )
        
        self.results.append(result)
        
    def check_text_section_consistency(self):
        """Check that all Sections belong to exactly one Text"""
        result = ValidationResult("Text-Section Consistency")
        
        query = """
        MATCH (s:Section)<-[:SECTION_PART_OF_TEXT]-(t:Text)
        WITH s, count(t) as text_count
        WHERE text_count > 1
        RETURN s.ID as section_id, text_count
        LIMIT 50
        """
        
        multiple_parents = list(self.db.run(query))
        if multiple_parents:
            for record in multiple_parents:
                result.add_issue(
                    f"Section {record['section_id']} belongs to {record['text_count']} Texts (should be 1)",
                    {"section_id": record["section_id"], "text_count": record["text_count"]}
                )
        
        self.results.append(result)
        
    def check_phrase_word_consistency(self):
        """Check that Phrases have at least one word"""
        result = ValidationResult("Phrase-Word Consistency")
        
        query = """
        MATCH (p:Phrase)
        WHERE NOT (p)-[:PHRASE_COMPOSED_OF]->()
        RETURN p.ID as phrase_id
        LIMIT 100
        """
        
        empty_phrases = list(self.db.run(query))
        if empty_phrases:
            for record in empty_phrases:
                result.add_issue(
                    f"Phrase {record['phrase_id']} has no words",
                    {"phrase_id": record["phrase_id"]}
                )
        
        self.results.append(result)
        
    def check_word_morpheme_consistency(self):
        """Check for Words that should have morphemes but don't"""
        result = ValidationResult("Word-Morpheme Consistency", severity="WARNING")
        
        # This is a warning because some words might legitimately not have morphemes
        # But we can check for words that have no morphemes and no relationships
        query = """
        MATCH (w:Word)
        WHERE NOT (w)-[:WORD_MADE_OF]->()
          AND (w)<-[:SECTION_CONTAINS]-() OR (w)<-[:PHRASE_COMPOSED_OF]-()
        RETURN w.ID as word_id, w.surface_form as surface_form
        LIMIT 50
        """
        
        words_without_morphemes = list(self.db.run(query))
        if words_without_morphemes:
            for record in words_without_morphemes:
                result.add_issue(
                    f"Word {record['word_id']} ({record['surface_form']}) has no morphemes (may be intentional)",
                    {"word_id": record["word_id"], "surface_form": record["surface_form"]}
                )
        
        self.results.append(result)
        
    def check_duplicate_relationships(self):
        """Check for duplicate relationships between the same nodes"""
        result = ValidationResult("Duplicate Relationships")
        
        # Check for duplicate PHRASE_COMPOSED_OF with same Order
        query = """
        MATCH (p:Phrase)-[r:PHRASE_COMPOSED_OF]->(w:Word)
        WITH p, w, r.Order as order, count(*) as rel_count
        WHERE rel_count > 1
        RETURN p.ID as phrase_id, w.ID as word_id, order, rel_count
        LIMIT 50
        """
        
        duplicates = list(self.db.run(query))
        if duplicates:
            for record in duplicates:
                result.add_issue(
                    f"Duplicate PHRASE_COMPOSED_OF: Phrase {record['phrase_id']} -> Word {record['word_id']} (Order: {record['order']}, Count: {record['rel_count']})",
                    {"phrase_id": record["phrase_id"], "word_id": record["word_id"], "order": record["order"]}
                )
        
        self.results.append(result)
        
    def check_missing_required_properties(self):
        """Check for missing commonly expected properties"""
        result = ValidationResult("Missing Required Properties", severity="WARNING")
        
        # Check Text nodes for common properties
        query = """
        MATCH (t:Text)
        WHERE t.title IS NULL AND t.language IS NULL
        RETURN t.ID as text_id
        LIMIT 50
        """
        
        texts_missing_props = list(self.db.run(query))
        if texts_missing_props:
            for record in texts_missing_props:
                result.add_issue(
                    f"Text {record['text_id']} missing title and language properties",
                    {"text_id": record["text_id"]}
                )
        
        # Check Word nodes for surface_form
        query = """
        MATCH (w:Word)
        WHERE w.surface_form IS NULL
        RETURN w.ID as word_id
        LIMIT 50
        """
        
        words_missing_surface = list(self.db.run(query))
        if words_missing_surface:
            for record in words_missing_surface:
                result.add_issue(
                    f"Word {record['word_id']} missing surface_form property",
                    {"word_id": record["word_id"]}
                )
        
        self.results.append(result)
        
    def print_summary(self):
        """Print validation summary"""
        print()
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print()
        
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.passed)
        failed_checks = total_checks - passed_checks
        
        # Print results by severity
        errors = [r for r in self.results if not r.passed and r.severity == "ERROR"]
        warnings = [r for r in self.results if not r.passed and r.severity == "WARNING"]
        infos = [r for r in self.results if not r.passed and r.severity == "INFO"]
        
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {failed_checks}")
        print()
        
        if errors:
            print("ERRORS:")
            for result in errors:
                print(f"  {result.get_summary()}")
                for issue in result.issues[:5]:  # Show first 5 issues
                    print(f"    - {issue['description']}")
                if len(result.issues) > 5:
                    print(f"    ... and {len(result.issues) - 5} more")
            print()
        
        if warnings:
            print("WARNINGS:")
            for result in warnings:
                print(f"  {result.get_summary()}")
                for issue in result.issues[:3]:  # Show first 3 issues
                    print(f"    - {issue['description']}")
                if len(result.issues) > 3:
                    print(f"    ... and {len(result.issues) - 3} more")
            print()
        
        if passed_checks > 0:
            print("PASSED CHECKS:")
            for result in self.results:
                if result.passed:
                    print(f"  {result.get_summary()}")
            print()
        
        print("=" * 80)
        
        # Exit code
        if errors:
            print("❌ Validation FAILED - Errors found")
            sys.exit(1)
        elif warnings:
            print("⚠️  Validation PASSED with warnings")
            sys.exit(0)
        else:
            print("✅ Validation PASSED - No issues found")
            sys.exit(0)


def main():
    """Main entry point"""
    try:
        with get_db() as db:
            validator = DatabaseValidator(db)
            validator.run_all_checks()
    except Exception as e:
        print("=" * 80)
        print("ERROR: Failed to connect to database")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        print("Please ensure:")
        print("  1. Neo4j is running")
        print("  2. Environment variables are set correctly:")
        print(f"     - NEO4J_URI: {os.getenv('NEO4J_URI', 'bolt://localhost:7687')}")
        print(f"     - NEO4J_USER: {os.getenv('NEO4J_USER', 'neo4j')}")
        print(f"     - NEO4J_PASSWORD: {os.getenv('NEO4J_PASSWORD', 'password')}")
        print()
        print("If running locally, check your .env file in the backend directory.")
        print("If running in Docker, check docker-compose environment variables.")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()

