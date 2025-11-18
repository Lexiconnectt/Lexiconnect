from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, Query
from typing import List, Optional, Any, Tuple
from pydantic import ValidationError
from app.database import get_db_dependency
from app.models.linguistic import (
    InterlinearTextCreate,
    InterlinearTextResponse,
    WordCreate,
    WordSearchQuery,
    WordResponse,
    MorphemeCreate,
    MorphemeSearchQuery,
    MorphemeResponse,
    SectionCreate,
    PhraseCreate,
    ConcordanceQuery,
    ConcordanceResult,
    GlossTarget,
)
from app.parsers.flextext_parser import parse_flextext_file, get_file_stats
from app.parsers.elan_parser import (
    parse_eaf_file as parse_elan_eaf_file,
    parse_eaf_to_json_string as parse_elan_eaf_to_json_string,
    parse_elan_file,
    get_elan_file_stats,
)
import tempfile
import os
import traceback
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

GRAPH_DATA_MIN_LIMIT = 10
GRAPH_DATA_MAX_LIMIT = 1000
GRAPH_DATA_DEFAULT_LIMIT = 200


@router.post("/upload-flextext")
async def upload_flextext_file(
    file: UploadFile = File(...), db=Depends(get_db_dependency)
):
    """Upload and parse a FLEx .flextext file and store in Neo4j using DATABASE.md schema"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".flextext") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Parse the file
            texts = parse_flextext_file(temp_file_path)
            stats = get_file_stats(temp_file_path)

            # Store in graph database using correct schema
            processed_texts = []
            skipped_texts = []
            for text in texts:
                text_id, was_created = await _store_interlinear_text(text, db)
                processed_texts.append(text_id)
                if not was_created:
                    skipped_texts.append(
                        {"id": text_id, "title": text.title or text_id}
                    )

            message = f"Successfully uploaded and processed {file.filename}"
            if skipped_texts:
                skipped_count = len(skipped_texts)
                message += f". {skipped_count} text(s) were skipped because they already exist in the database."

            return {
                "message": message,
                "file_stats": stats,
                "processed_texts": processed_texts,
                "skipped_texts": skipped_texts,
                "skipped_count": len(skipped_texts),
            }

        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

    except ValidationError as e:
        error_msg = f"Validation error: {e.errors()}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=error_msg)


@router.post("/upload-elan")
async def upload_elan_file(file: UploadFile = File(...), db=Depends(get_db_dependency)):
    """Upload and parse an ELAN .eaf file and store in Neo4j using DATABASE.md schema (matching Flex model)"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".eaf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Parse the file using the new ELAN parser (returns InterlinearTextCreate objects)
            texts = parse_elan_file(temp_file_path)
            stats = get_elan_file_stats(temp_file_path)

            # Store in graph database using correct schema (same as Flex)
            processed_texts = []
            skipped_texts = []
            for text in texts:
                text_id, was_created = await _store_interlinear_text(text, db)
                processed_texts.append(text_id)
                if not was_created:
                    skipped_texts.append(
                        {"id": text_id, "title": text.title or text_id}
                    )

            message = f"Successfully uploaded and processed {file.filename}"
            if skipped_texts:
                skipped_count = len(skipped_texts)
                message += f". {skipped_count} text(s) were skipped because they already exist in the database."

            return {
                "message": message,
                "file_stats": stats,
                "processed_texts": processed_texts,
                "skipped_texts": skipped_texts,
                "skipped_count": len(skipped_texts),
            }

        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

    except ValidationError as e:
        error_msg = f"Validation error: {e.errors()}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Error processing ELAN file: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=error_msg)


def _store_elan_graph(parsed_doc: Any, db) -> dict:
    """Persist ELAN JSON into Neo4j as ElanDoc/ElanTier/ElanAnnotation nodes.

    Returns counts of created/merged nodes and relationships.
    """
    file_name = parsed_doc.get("file") or ""
    author = parsed_doc.get("author")
    date = parsed_doc.get("date")

    # Use the file name as a stable ID for the document
    doc_id = f"elan:{file_name}"

    # Create/merge ElanDoc
    db.run(
        """
        MERGE (d:ElanDoc {ID: $ID})
          ON CREATE SET d.created_at = datetime()
        SET d.file = $file,
            d.author = $author,
            d.date = $date,
            d.updated_at = datetime()
        """,
        ID=doc_id,
        file=file_name,
        author=author,
        date=date,
    )

    tier_count = 0
    ann_count = 0

    for tier in parsed_doc.get("tiers", []):
        tier_id = tier.get("tier_id") or ""
        node_id = f"{doc_id}#tier:{tier_id}"

        db.run(
            """
            MATCH (d:ElanDoc {ID: $doc_id})
            MERGE (t:ElanTier {ID: $ID})
              ON CREATE SET t.created_at = datetime()
            SET t.tier_id = $tier_id,
                t.participant = $participant,
                t.linguistic_type_ref = $linguistic_type_ref,
                t.parent_ref = $parent_ref,
                t.updated_at = datetime()
            MERGE (d)-[:HAS_TIER]->(t)
            """,
            doc_id=doc_id,
            ID=node_id,
            tier_id=tier_id,
            participant=tier.get("participant"),
            linguistic_type_ref=tier.get("linguistic_type_ref"),
            parent_ref=tier.get("parent_ref"),
        )
        tier_count += 1

        for ann in tier.get("annotations", []):
            ann_id = ann.get("id") or ""
            ann_node_id = f"{node_id}#ann:{ann_id}"

            db.run(
                """
                MATCH (t:ElanTier {ID: $tier_node_id})
                MERGE (a:ElanAnnotation {ID: $ID})
                  ON CREATE SET a.created_at = datetime()
                SET a.value = $value,
                    a.start_ms = $start_ms,
                    a.end_ms = $end_ms,
                    a.ref_id = $ref_id,
                    a.updated_at = datetime()
                MERGE (t)-[:HAS_ANNOTATION]->(a)
                """,
                tier_node_id=node_id,
                ID=ann_node_id,
                value=ann.get("value"),
                start_ms=ann.get("start_ms"),
                end_ms=ann.get("end_ms"),
                ref_id=ann.get("ref_id"),
            )
            ann_count += 1

    return {"tiers": tier_count, "annotations": ann_count}


async def _store_interlinear_text(text: InterlinearTextCreate, db) -> Tuple[str, bool]:
    """Store an interlinear text using DATABASE.md schema relationships

    Returns:
        tuple: (text_id, was_created) where was_created is True if the text was newly created,
               False if it already existed in the database
    """
    # Check if text already exists
    existing_text = db.run(
        """
        MATCH (t:Text {ID: $ID})
        RETURN t.ID as ID, t.title as title
        """,
        ID=text.id,
    ).single()

    was_created = existing_text is None

    # Create the Text node with ID property (matching schema)
    # Use MERGE directly without MATCH to avoid Cartesian products
    db.run(
        """
        MERGE (t:Text {ID: $ID})
          ON CREATE SET t.created_at = datetime()
        SET t.title = $title,
            t.source = $source,
            t.comment = $comment,
            t.language = $language,
            t.updated_at = datetime()
        """,
        ID=text.id,
        title=text.title,
        source=text.source,
        comment=text.comment,
        language=text.language,
    )

    # Only store sections if this is a new text (to avoid duplicating sections)
    if was_created:
        # Store sections and their components using correct relationships
        for section in text.sections:
            await _store_section(section, text.id, db)

    return (text.id, was_created)


async def _store_section(section: SectionCreate, text_id: str, db):
    """Store a Section node with SECTION_PART_OF_TEXT relationship"""

    # Create Section node and link to Text in one query to avoid Cartesian products
    db.run(
        """
        MATCH (t:Text {ID: $text_id})
        MERGE (s:Section {ID: $ID})
          ON CREATE SET s.created_at = datetime()
        SET s.order = $order,
            s.updated_at = datetime()
        MERGE (t)-[:SECTION_PART_OF_TEXT]->(s)
        """,
        text_id=text_id,
        ID=section.id,
        order=section.order,
    )

    # Store phrases with PHRASE_IN_SECTION relationship
    for phrase in section.phrases:
        await _store_phrase(phrase, section.id, db)

    # Store words with SECTION_CONTAINS relationship
    for word in section.words:
        await _store_word_in_section(word, section.id, db)


async def _store_phrase(phrase: PhraseCreate, section_id: str, db):
    """Store a Phrase node with PHRASE_IN_SECTION relationship"""

    # Create Phrase node and link to Section in one query to avoid Cartesian products
    db.run(
        """
        MATCH (s:Section {ID: $section_id})
        MERGE (p:Phrase {ID: $ID})
          ON CREATE SET p.created_at = datetime()
        SET p.segnum = $segnum,
            p.surface_text = $surface_text,
            p.language = $language,
            p.updated_at = datetime()
        MERGE (s)-[:PHRASE_IN_SECTION]->(p)
        """,
        section_id=section_id,
        ID=phrase.id,
        segnum=phrase.segnum,
        surface_text=phrase.surface_text,
        language=phrase.language,
    )

    # Store words in phrase with PHRASE_COMPOSED_OF relationship (includes Order property)
    for idx, word in enumerate(phrase.words):
        await _store_word_in_phrase(word, phrase.id, idx, db)


async def _store_word_in_section(word: WordCreate, section_id: str, db):
    """Store word with SECTION_CONTAINS relationship"""

    # Create Word node and link to Section - avoid Cartesian products
    # Convert pos list to string for storage (or handle as list if Neo4j supports it)
    pos_value = ",".join(word.pos) if isinstance(word.pos, list) else word.pos

    db.run(
        """
        MATCH (s:Section {ID: $section_id})
        MERGE (w:Word {ID: $ID})
          ON CREATE SET w.created_at = datetime()
        SET w.surface_form = $surface_form,
            w.gloss = $gloss,
            w.pos = $pos,
            w.language = $language,
            w.updated_at = datetime()
        MERGE (s)-[:SECTION_CONTAINS]->(w)
        """,
        section_id=section_id,
        ID=word.id,
        surface_form=word.surface_form,
        gloss=word.gloss,
        pos=pos_value,
        language=word.language,
    )

    # Store morphemes
    for morpheme in word.morphemes:
        await _store_morpheme(morpheme, word.id, db)

    # Create Gloss node if word has gloss annotation
    if word.gloss:
        await _store_gloss_for_word(word.id, word.gloss, db)


async def _store_word_in_phrase(word: WordCreate, phrase_id: str, order: int, db):
    """Store word with PHRASE_COMPOSED_OF relationship (with Order property)"""

    # Create Word node and link to Phrase - avoid Cartesian products
    # Convert pos list to string for storage
    pos_value = ",".join(word.pos) if isinstance(word.pos, list) else word.pos

    db.run(
        """
        MATCH (p:Phrase {ID: $phrase_id})
        MERGE (w:Word {ID: $ID})
          ON CREATE SET w.created_at = datetime()
        SET w.surface_form = $surface_form,
            w.gloss = $gloss,
            w.pos = $pos,
            w.language = $language,
            w.updated_at = datetime()
        MERGE (p)-[:PHRASE_COMPOSED_OF {Order: $order}]->(w)
        """,
        phrase_id=phrase_id,
        ID=word.id,
        order=order,
        surface_form=word.surface_form,
        gloss=word.gloss,
        pos=pos_value,
        language=word.language,
    )

    # Store morphemes
    for morpheme in word.morphemes:
        await _store_morpheme(morpheme, word.id, db)

    # Create Gloss node if word has gloss annotation
    if word.gloss:
        await _store_gloss_for_word(word.id, word.gloss, db)


async def _store_morpheme(morpheme: MorphemeCreate, word_id: str, db):
    """Store a Morpheme node with WORD_MADE_OF relationship"""

    # Convert msa to string if it's a dict or list
    msa_value = morpheme.msa
    if isinstance(morpheme.msa, dict):
        msa_value = ",".join(f"{k}:{v}" for k, v in morpheme.msa.items())
    elif isinstance(morpheme.msa, list):
        msa_value = ",".join(morpheme.msa)

    db.run(
        """
        MATCH (w:Word {ID: $word_id})
        MERGE (m:Morpheme {ID: $ID})
          ON CREATE SET m.created_at = datetime()
        SET m.type = $type,
            m.surface_form = $surface_form,
            m.citation_form = $citation_form,
            m.gloss = $gloss,
            m.msa = $msa,
            m.language = $language,
            m.original_guid = $original_guid,
            m.updated_at = datetime()
        MERGE (w)-[:WORD_MADE_OF]->(m)
        """,
        word_id=word_id,
        ID=morpheme.id,
        type=morpheme.type.value,
        surface_form=morpheme.surface_form,
        citation_form=morpheme.citation_form,
        gloss=morpheme.gloss,
        msa=str(msa_value),
        language=morpheme.language,
        original_guid=morpheme.original_guid,
    )

    # Create Gloss node if morpheme has gloss
    if morpheme.gloss:
        await _store_gloss_for_morpheme(morpheme.id, morpheme.gloss, db)


async def _store_gloss_for_word(word_id: str, annotation: str, db):
    """Create a Gloss node linked to a Word with ANALYZES relationship"""

    gloss_id = f"gloss-word-{word_id}"

    db.run(
        """
        MATCH (w:Word {ID: $word_id})
        MERGE (g:Gloss {ID: $gloss_id})
          ON CREATE SET g.created_at = datetime()
        SET g.annotation = $annotation,
            g.gloss_type = 'word',
            g.language = 'en',
            g.updated_at = datetime()
        MERGE (g)-[:ANALYZES]->(w)
        """,
        word_id=word_id,
        gloss_id=gloss_id,
        annotation=annotation,
    )


async def _store_gloss_for_morpheme(morpheme_id: str, annotation: str, db):
    """Create a Gloss node linked to a Morpheme with ANALYZES relationship"""

    gloss_id = f"gloss-morph-{morpheme_id}"

    db.run(
        """
        MATCH (m:Morpheme {ID: $morpheme_id})
        MERGE (g:Gloss {ID: $gloss_id})
          ON CREATE SET g.created_at = datetime()
        SET g.annotation = $annotation,
            g.gloss_type = 'morpheme',
            g.language = 'en',
            g.updated_at = datetime()
        MERGE (g)-[:ANALYZES]->(m)
        """,
        morpheme_id=morpheme_id,
        gloss_id=gloss_id,
        annotation=annotation,
    )


@router.post("/search/words", response_model=List[WordResponse])
async def search_words(
    query: WordSearchQuery, response: Response, db=Depends(get_db_dependency)
):
    """Search for words based on various criteria"""
    try:
        base = ["MATCH (w:Word)"]
        params = {}
        conditions = []

        if query.surface_form:
            conditions.append("w.surface_form CONTAINS $surface_form")
            params["surface_form"] = query.surface_form

        if query.gloss:
            conditions.append("w.gloss CONTAINS $gloss")
            params["gloss"] = query.gloss

        if query.pos:
            conditions.append("w.pos = $pos")
            params["pos"] = query.pos

        if query.language:
            conditions.append("w.language = $language")
            params["language"] = query.language

        if query.contains_morpheme:
            base.append("MATCH (w)-[:WORD_MADE_OF]->(m:Morpheme)")
            conditions.append(
                "(m.surface_form CONTAINS $morpheme OR m.citation_form CONTAINS $morpheme)"
            )
            params["morpheme"] = query.contains_morpheme

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        count_cypher = (
            "".join(base) + where_clause + " RETURN count(DISTINCT w) AS total"
        )
        total = db.run(count_cypher, **params).single()["total"]

        cypher_query = (
            "".join(base)
            + where_clause
            + """
            OPTIONAL MATCH (w)-[:WORD_MADE_OF]->(m2:Morpheme)
            WITH w, COUNT(m2) AS morpheme_count
            RETURN w.ID as ID, w.surface_form as surface_form,
                   w.gloss as gloss, w.pos as pos, w.language as language,
                   morpheme_count, toString(w.created_at) as created_at
            ORDER BY w.surface_form
            SKIP $offset
            LIMIT $limit
        """
        )
        params.update({"limit": query.limit, "offset": query.offset})

        result = db.run(cypher_query, **params)
        words = [WordResponse(**dict(record)) for record in result]

        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Limit"] = str(query.limit)
        response.headers["X-Offset"] = str(query.offset)

        return words

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/search/morphemes", response_model=List[MorphemeResponse])
async def search_morphemes(
    query: MorphemeSearchQuery, response: Response, db=Depends(get_db_dependency)
):
    """Search for morphemes based on various criteria"""
    try:
        base = ["MATCH (m:Morpheme)"]
        params = {}
        conditions = []

        if query.surface_form:
            conditions.append("m.surface_form CONTAINS $surface_form")
            params["surface_form"] = query.surface_form

        if query.citation_form:
            conditions.append("m.citation_form CONTAINS $citation_form")
            params["citation_form"] = query.citation_form

        if query.gloss:
            conditions.append("m.gloss CONTAINS $gloss")
            params["gloss"] = query.gloss

        if query.type:
            conditions.append("m.type = $type")
            params["type"] = query.type.value

        if query.language:
            conditions.append("m.language = $language")
            params["language"] = query.language

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        count_cypher = (
            "".join(base) + where_clause + " RETURN count(DISTINCT m) AS total"
        )
        total = db.run(count_cypher, **params).single()["total"]

        cypher_query = (
            "".join(base)
            + where_clause
            + """
            RETURN m.ID as ID, m.type as type,
                   m.surface_form as surface_form, m.citation_form as citation_form,
                   m.gloss as gloss, m.msa as msa, m.language as language,
                   toString(m.created_at) as created_at
            ORDER BY m.citation_form
            SKIP $offset
            LIMIT $limit
        """
        )
        params.update({"limit": query.limit, "offset": query.offset})

        result = db.run(cypher_query, **params)
        morphemes = [MorphemeResponse(**dict(record)) for record in result]

        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Limit"] = str(query.limit)
        response.headers["X-Offset"] = str(query.offset)

        return morphemes

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/concordance", response_model=List[ConcordanceResult])
async def concordance_search(
    query: ConcordanceQuery, response: Response, db=Depends(get_db_dependency)
):
    """Concordance search: find patterns across texts with context window (KWIC format)"""
    try:
        results = []

        if query.target_type == GlossTarget.MORPHEME:
            # Search for morphemes matching the pattern
            # First, find all matching morphemes and their words
            cypher_query = """
            MATCH (m:Morpheme)
            WHERE (m.surface_form CONTAINS $target OR m.citation_form CONTAINS $target OR m.gloss CONTAINS $target)
            AND ($language IS NULL OR m.language = $language)
            MATCH (w:Word)-[:WORD_MADE_OF]->(m)
            MATCH (ph:Phrase)-[r:PHRASE_COMPOSED_OF]->(w)
            MATCH (t:Text)-[:SECTION_PART_OF_TEXT]->(s:Section)-[:PHRASE_IN_SECTION]->(ph)
            WITH ph, w, m, r.Order as word_order, t, s
            ORDER BY word_order
            OPTIONAL MATCH (g:Gloss)-[:ANALYZES]->(m)
            WITH ph, w, m, word_order, t, s, collect(DISTINCT g.annotation) as glosses
            RETURN 
                ph.ID as phrase_id,
                COALESCE(t.title, '') as text_title,
                COALESCE(s.ID, '') as segnum,
                m.surface_form as target,
                word_order as word_index,
                [g IN glosses WHERE g IS NOT NULL] as glosses
            ORDER BY t.title, segnum, word_order
            LIMIT $limit
            """

            params = {
                "target": query.target,
                "language": query.language,
                "limit": query.limit,
            }

            result = db.run(cypher_query, **params)
            for record in result:
                # Get context words for this phrase
                phrase_id = record["phrase_id"]
                word_order = record["word_index"]

                # Get all words in the phrase for context
                context_query = """
                MATCH (ph:Phrase {ID: $phrase_id})-[r:PHRASE_COMPOSED_OF]->(w:Word)
                WITH w, r.Order as order
                ORDER BY order
                RETURN collect(w.surface_form) as words, collect(order) as orders
                """
                context_result = db.run(context_query, phrase_id=phrase_id).single()

                if context_result:
                    words = context_result["words"] or []
                    orders = context_result["orders"] or []
                    try:
                        target_idx = orders.index(word_order)
                        left_context = (
                            words[max(0, target_idx - query.context_size) : target_idx]
                            if target_idx > 0
                            else []
                        )
                        right_context = (
                            words[target_idx + 1 : target_idx + 1 + query.context_size]
                            if target_idx < len(words) - 1
                            else []
                        )
                    except ValueError:
                        left_context = []
                        right_context = []
                else:
                    left_context = []
                    right_context = []

                glosses = record.get("glosses") or []
                results.append(
                    ConcordanceResult(
                        target=record["target"],
                        left_context=left_context,
                        right_context=right_context,
                        phrase_id=phrase_id,
                        text_title=record["text_title"],
                        segnum=record["segnum"],
                        word_index=word_order,
                        glosses=glosses if glosses else None,
                    )
                )

        elif query.target_type == GlossTarget.WORD:
            # Search for words matching the pattern
            cypher_query = """
            MATCH (w:Word)
            WHERE (w.surface_form CONTAINS $target OR w.gloss CONTAINS $target)
            AND ($language IS NULL OR w.language = $language)
            MATCH (ph:Phrase)-[r:PHRASE_COMPOSED_OF]->(w)
            MATCH (t:Text)-[:SECTION_PART_OF_TEXT]->(s:Section)-[:PHRASE_IN_SECTION]->(ph)
            WITH ph, w, r.Order as word_order, t, s
            ORDER BY word_order
            OPTIONAL MATCH (g:Gloss)-[:ANALYZES]->(w)
            WITH ph, w, word_order, t, s, collect(DISTINCT g.annotation) as glosses
            RETURN 
                ph.ID as phrase_id,
                COALESCE(t.title, '') as text_title,
                COALESCE(s.ID, '') as segnum,
                w.surface_form as target,
                word_order as word_index,
                [g IN glosses WHERE g IS NOT NULL] as glosses
            ORDER BY t.title, segnum, word_order
            LIMIT $limit
            """

            params = {
                "target": query.target,
                "language": query.language,
                "limit": query.limit,
            }

            result = db.run(cypher_query, **params)
            for record in result:
                # Get context words for this phrase
                phrase_id = record["phrase_id"]
                word_order = record["word_index"]

                # Get all words in the phrase for context
                context_query = """
                MATCH (ph:Phrase {ID: $phrase_id})-[r:PHRASE_COMPOSED_OF]->(w:Word)
                WITH w, r.Order as order
                ORDER BY order
                RETURN collect(w.surface_form) as words, collect(order) as orders
                """
                context_result = db.run(context_query, phrase_id=phrase_id).single()

                if context_result:
                    words = context_result["words"] or []
                    orders = context_result["orders"] or []
                    try:
                        target_idx = orders.index(word_order)
                        left_context = (
                            words[max(0, target_idx - query.context_size) : target_idx]
                            if target_idx > 0
                            else []
                        )
                        right_context = (
                            words[target_idx + 1 : target_idx + 1 + query.context_size]
                            if target_idx < len(words) - 1
                            else []
                        )
                    except ValueError:
                        left_context = []
                        right_context = []
                else:
                    left_context = []
                    right_context = []

                glosses = record.get("glosses") or []
                results.append(
                    ConcordanceResult(
                        target=record["target"],
                        left_context=left_context,
                        right_context=right_context,
                        phrase_id=phrase_id,
                        text_title=record["text_title"],
                        segnum=record["segnum"],
                        word_index=word_order,
                        glosses=glosses if glosses else None,
                    )
                )

        total = len(results)
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Limit"] = str(query.limit)

        return results

    except Exception as e:
        logger.error(f"Error in concordance search: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/texts", response_model=List[InterlinearTextResponse])
async def get_texts(
    language: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    response: Response = None,
    db=Depends(get_db_dependency),
):
    """Get list of interlinear texts"""
    try:
        total = db.run(
            """
            MATCH (t:Text)
            WHERE ($language IS NULL OR t.language = $language)
            RETURN count(t) AS total
            """,
            language=language,
        ).single()["total"]

        cypher_query = """
            MATCH (t:Text)
            WHERE ($language IS NULL OR t.language = $language)
            OPTIONAL MATCH (t)-[:SECTION_PART_OF_TEXT]->(s:Section)
            OPTIONAL MATCH (s)-[:SECTION_CONTAINS]->(w:Word)
            OPTIONAL MATCH (w)-[:WORD_MADE_OF]->(m:Morpheme)
            WITH t, 
                 COUNT(DISTINCT s) AS section_count,
                 COUNT(DISTINCT w) AS word_count,
                 COUNT(DISTINCT m) AS morpheme_count
            RETURN
              COALESCE(t.ID, toString(id(t)))                     AS ID,
              COALESCE(t.title, '')                               AS title,
              COALESCE(t.source, '')                              AS source,
              COALESCE(t.comment, '')                             AS comment,
              COALESCE(t.language, '')                       AS language,
              section_count, word_count, morpheme_count,
              toString(COALESCE(t.created_at, datetime()))        AS created_at
            ORDER BY COALESCE(t.created_at, datetime()) DESC
            SKIP $skip
            LIMIT $limit
        """
        result = db.run(cypher_query, language=language, skip=skip, limit=limit)

        texts = [InterlinearTextResponse(**dict(record)) for record in result]

        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Limit"] = str(limit)
        response.headers["X-Offset"] = str(skip)

        return texts

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
async def get_database_stats(db=Depends(get_db_dependency)):
    """Get overall database statistics"""
    try:
        # Use separate queries to avoid timeout issues
        text_count = (
            db.run("MATCH (t:Text) RETURN count(t) as count").single()["count"] or 0
        )
        section_count = (
            db.run("MATCH (s:Section) RETURN count(s) as count").single()["count"] or 0
        )
        phrase_count = (
            db.run("MATCH (p:Phrase) RETURN count(p) as count").single()["count"] or 0
        )
        word_count = (
            db.run("MATCH (w:Word) RETURN count(w) as count").single()["count"] or 0
        )
        morpheme_count = (
            db.run("MATCH (m:Morpheme) RETURN count(m) as count").single()["count"] or 0
        )
        gloss_count = (
            db.run("MATCH (g:Gloss) RETURN count(g) as count").single()["count"] or 0
        )

        # Count relationships - this can be expensive, so we'll make it optional
        try:
            relationship_count = (
                db.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                or 0
            )
        except Exception:
            # If counting all relationships times out, estimate or skip
            relationship_count = None

        return {
            "text_count": text_count,
            "section_count": section_count,
            "phrase_count": phrase_count,
            "word_count": word_count,
            "morpheme_count": morpheme_count,
            "gloss_count": gloss_count,
            "relationship_count": relationship_count,
        }

    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/schema-visualization")
async def get_schema_visualization(db=Depends(get_db_dependency)):
    """Get a sample of the graph structure for visualization"""
    try:
        return {
            "message": "Schema visualization data",
            "note": "Connect to Neo4j Browser at http://localhost:7474 for full visualization",
            "schema_url": "http://localhost:7474",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/graph-filters")
async def get_graph_filters(db=Depends(get_db_dependency)):
    """Get available filter options for graph visualization"""
    try:
        # Get available texts
        texts_query = """
            MATCH (t:Text)
            RETURN t.ID as id, 
                   COALESCE(t.title, t.ID, 'Untitled') as title,
                   t.language as language
            ORDER BY t.title
            LIMIT 50
        """
        texts_result = db.run(texts_query)
        texts = [dict(record) for record in texts_result]

        # Get available languages
        languages_query = """
            MATCH (t:Text)
            WHERE t.language IS NOT NULL
            RETURN DISTINCT t.language as code
            ORDER BY code
        """
        lang_result = db.run(languages_query)
        languages = [record["code"] for record in lang_result if record["code"]]

        return {
            "texts": texts,
            "languages": languages,
            "node_types": ["Text", "Section", "Phrase", "Word", "Morpheme", "Gloss"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/graph-data")
async def get_graph_data(
    text_id: Optional[str] = None,
    language: Optional[str] = None,
    node_types: Optional[str] = None,  # Comma-separated: "Text,Word,Gloss"
    limit: int = GRAPH_DATA_DEFAULT_LIMIT,
    db=Depends(get_db_dependency),
):
    """Get graph data for visualization with nodes and edges

    Args:
        text_id: Filter to specific text (shows all related nodes)
        language: Filter by language code
        node_types: Comma-separated node types to include (e.g. "Word,Gloss,Morpheme")
        limit: Max nodes per type (default 200, clamped between 10 and 1000)
    """
    limit = max(GRAPH_DATA_MIN_LIMIT, min(limit, GRAPH_DATA_MAX_LIMIT))

    # Helper class for creating record objects
    class GraphRecord:
        def __init__(self, nodes, edges):
            self.data = {"allNodes": nodes, "allEdges": edges}

        def __getitem__(self, key):
            return self.data[key]

    try:
        nodes = []
        edges = []

        # Query to get all nodes and relationships
        # If text_id is provided, filter by that text, otherwise get a sample
        if text_id:
            # Much simpler query - get nodes and edges separately
            # First get all nodes related to this text
            cypher_query = """
                MATCH path = (t:Text {ID: $text_id})-[*0..3]->(n)
                WITH DISTINCT n as node
                LIMIT $limit
                RETURN collect(node) as allNodes
            """

            nodes_result = db.run(cypher_query, text_id=text_id, limit=limit * 5)
            nodes_record = nodes_result.single()

            if not nodes_record or not nodes_record["allNodes"]:
                return {"nodes": [], "edges": []}

            all_node_objects = nodes_record["allNodes"]
            node_ids = [node.id for node in all_node_objects if node is not None]

            # Now get edges between these nodes
            edges_query = """
                MATCH (n1)-[r]->(n2)
                WHERE id(n1) IN $node_ids AND id(n2) IN $node_ids
                RETURN collect({
                    source: id(n1),
                    target: id(n2),
                    type: type(r)
                }) as allEdges
            """
            edges_result = db.run(edges_query, node_ids=node_ids)
            edges_record = edges_result.single()

            all_edges = edges_record["allEdges"] if edges_record else []

            # Create a record structure for compatibility with rest of code
            record = GraphRecord(all_node_objects, all_edges)
        else:
            # Parse node types filter - use simple query to get sample nodes
            allowed_types = set()
            if node_types:
                allowed_types = set(t.strip() for t in node_types.split(","))

            # Get sample nodes of each type separately (much simpler and faster)
            all_node_objects = []

            if not node_types or "Text" in allowed_types:
                lang_filter = "WHERE t.language = $language" if language else ""
                query = f"MATCH (t:Text) {lang_filter} RETURN t LIMIT $limit"
                result = db.run(query, limit=limit, language=language)
                all_node_objects.extend([record["t"] for record in result])

            if not node_types or "Section" in allowed_types:
                query = "MATCH (s:Section) RETURN s LIMIT $limit"
                result = db.run(query, limit=limit)
                all_node_objects.extend([record["s"] for record in result])

            if not node_types or "Phrase" in allowed_types:
                query = "MATCH (ph:Phrase) RETURN ph LIMIT $limit"
                result = db.run(query, limit=limit)
                all_node_objects.extend([record["ph"] for record in result])

            if not node_types or "Word" in allowed_types:
                lang_filter = "WHERE w.language = $language" if language else ""
                query = f"MATCH (w:Word) {lang_filter} RETURN w LIMIT $limit"
                result = db.run(query, limit=limit, language=language)
                all_node_objects.extend([record["w"] for record in result])

            if not node_types or "Morpheme" in allowed_types:
                lang_filter = "WHERE m.language = $language" if language else ""
                query = f"MATCH (m:Morpheme) {lang_filter} RETURN m LIMIT $limit"
                result = db.run(query, limit=limit, language=language)
                all_node_objects.extend([record["m"] for record in result])

            if not node_types or "Gloss" in allowed_types:
                query = "MATCH (g:Gloss) RETURN g LIMIT $limit"
                result = db.run(query, limit=limit)
                all_node_objects.extend([record["g"] for record in result])

            if not all_node_objects:
                return {"nodes": [], "edges": []}

            # Get node IDs for edge query
            node_ids = [node.id for node in all_node_objects if node is not None]

            # Get edges between these nodes (simple query)
            edges_query = """
                MATCH (n1)-[r]->(n2)
                WHERE id(n1) IN $node_ids AND id(n2) IN $node_ids
                RETURN collect({
                    source: id(n1),
                    target: id(n2),
                    type: type(r)
                }) as allEdges
            """
            edges_result = db.run(edges_query, node_ids=node_ids)
            edges_record = edges_result.single()

            all_edges = edges_record["allEdges"] if edges_record else []

            # Create a record structure for compatibility with rest of code
            record = GraphRecord(all_node_objects, all_edges)

        if not record:
            # Return empty graph if no data
            return {"nodes": [], "edges": []}

        # Define colors for each node type
        node_colors = {
            "Text": "#f59e0b",  # amber
            "Section": "#8b5cf6",  # purple
            "Phrase": "#06b6d4",  # cyan
            "Word": "#0ea5e9",  # blue
            "Morpheme": "#10b981",  # green
            "Gloss": "#ec4899",  # pink
        }

        # Define sizes for each node type (larger = more important in hierarchy)
        node_sizes = {
            "Text": 30,
            "Section": 22,
            "Phrase": 16,
            "Word": 8,
            "Morpheme": 6,
            "Gloss": 7,
        }

        # Process nodes (track seen IDs to avoid duplicates)
        all_nodes = record["allNodes"]
        seen_node_ids = set()

        for node in all_nodes:
            if node is None:
                continue

            # Skip duplicates
            node_id = str(node.id)
            if node_id in seen_node_ids:
                continue
            seen_node_ids.add(node_id)

            labels = list(node.labels)
            if not labels:
                continue

            node_type = labels[0]
            node_props = dict(node)

            # Get label text
            label_text = node_props.get("ID", "")
            if node_type == "Text":
                label_text = node_props.get("title", label_text)
            elif node_type == "Word":
                label_text = node_props.get("surface_form", label_text)
            elif node_type == "Morpheme":
                label_text = node_props.get(
                    "surface_form", node_props.get("citation_form", label_text)
                )
            elif node_type == "Gloss":
                label_text = node_props.get("annotation", label_text)[
                    :20
                ]  # Truncate long glosses
            elif node_type == "Phrase":
                label_text = node_props.get("surface_text", label_text)[:30]

            nodes.append(
                {
                    "id": node_id,
                    "label": label_text,
                    "type": node_type,
                    "color": node_colors.get(node_type, "#64748b"),
                    "size": node_sizes.get(node_type, 10),
                    "properties": node_props,
                }
            )

        # Process edges
        all_edges = record["allEdges"]
        for idx, edge in enumerate(all_edges):
            if edge is None or edge.get("source") is None or edge.get("target") is None:
                continue

            edges.append(
                {
                    "id": f"edge-{idx}",
                    "source": str(edge["source"]),
                    "target": str(edge["target"]),
                    "type": edge.get("type", ""),
                    "size": 2,
                    "color": "#94a3b8",
                }
            )

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {"node_count": len(nodes), "edge_count": len(edges)},
        }

    except Exception as e:
        logger.error(f"Error fetching graph data: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=400, detail=f"Error fetching graph data: {str(e)}"
        )


@router.get("/word-graph-data")
async def get_word_graph_data(
    word: str,
    language: Optional[str] = None,
    db=Depends(get_db_dependency),
):
    """Get morphological graph data for a specific word

    This endpoint returns:
    - The searched word node
    - Its parent text, section, and phrase
    - Its morphemes (prefix, stem, suffix)
    - Related words that share the same morphemes
    - Glosses for the morphemes

    Args:
        word: The surface form of the word to search
        language: Optional language filter
    """
    try:
        nodes = []
        edges = []

        # Define colors for each node type
        node_colors = {
            "Text": "#f59e0b",  # amber
            "Section": "#8b5cf6",  # purple
            "Phrase": "#06b6d4",  # cyan
            "Word": "#0ea5e9",  # blue
            "Morpheme": "#10b981",  # green
            "Gloss": "#ec4899",  # pink
        }

        node_sizes = {
            "Text": 30,
            "Section": 22,
            "Phrase": 16,
            "Word": 10,
            "Morpheme": 8,
            "Gloss": 7,
        }

        # Find the word and its context
        lang_filter = "AND w.language = $language" if language else ""

        # Simple, direct query that gets everything step by step
        cypher_query = f"""
        MATCH (w:Word {{surface_form: $word}})
        WHERE 1=1 {lang_filter}
        
        // Get context
        OPTIONAL MATCH (t:Text)-[:SECTION_PART_OF_TEXT]->(s:Section)-[:PHRASE_IN_SECTION]->(ph:Phrase)-[:PHRASE_COMPOSED_OF]->(w)
        
        // Get target word morphemes
        OPTIONAL MATCH (w)-[:WORD_MADE_OF]->(m:Morpheme)
        
        // Get target word glosses
        OPTIONAL MATCH (w)-[:WORD_MADE_OF]->(m2:Morpheme)<-[:ANALYZES]-(g:Gloss)
        
        WITH w, t, s, ph, collect(DISTINCT m) as target_morphemes, collect(DISTINCT g) as target_glosses
        
        // Find related words - any word that shares at least one morpheme
        OPTIONAL MATCH (w)-[:WORD_MADE_OF]->(shared:Morpheme)<-[:WORD_MADE_OF]-(related:Word)
        WHERE related.ID <> w.ID
        
        WITH w, t, s, ph, target_morphemes, target_glosses, collect(DISTINCT related) as related_words
        
        RETURN w as target_word, 
               t as text, 
               s as section, 
               ph as phrase,
               target_morphemes,
               target_glosses,
               related_words
        """

        result = db.run(cypher_query, word=word, language=language)
        record = result.single()

        if not record or not record.get("target_word"):
            logger.warning(f"Word '{word}' not found in database")
            return {
                "nodes": [],
                "edges": [],
                "stats": {"node_count": 0, "edge_count": 0},
                "message": f"Word '{word}' not found",
            }

        # Debug logging
        target_morphemes = record.get("target_morphemes", [])
        target_glosses = record.get("target_glosses", [])
        related_words = record.get("related_words", [])

        logger.info(f"Found word '{word}'")
        logger.info(
            f"Target morphemes: {len(target_morphemes)} - {[m.get('surface_form', '') if hasattr(m, 'get') else str(m) for m in target_morphemes[:5]]}"
        )
        logger.info(f"Target glosses: {len(target_glosses)}")
        logger.info(
            f"Related words: {len(related_words)} - {[w.get('surface_form', '') if hasattr(w, 'get') else str(w) for w in related_words[:5]]}"
        )

        seen_node_ids = set()
        node_id_map = {}  # Map neo4j internal id to our string id

        def add_node(node_obj, node_type):
            """Helper to add a node if not already seen"""
            if node_obj is None:
                return None

            node_id = str(node_obj.id)
            if node_id in seen_node_ids:
                return node_id

            seen_node_ids.add(node_id)
            node_props = dict(node_obj)

            # Get label text
            label_text = node_props.get("ID", "")
            if node_type == "Text":
                label_text = node_props.get("title", label_text)
            elif node_type == "Word":
                label_text = node_props.get("surface_form", label_text)
            elif node_type == "Morpheme":
                label_text = node_props.get(
                    "surface_form", node_props.get("citation_form", label_text)
                )
            elif node_type == "Gloss":
                label_text = node_props.get("annotation", label_text)[:20]
            elif node_type == "Phrase":
                label_text = node_props.get("surface_text", label_text)[:30]
            elif node_type == "Section":
                label_text = node_props.get("ID", label_text)

            nodes.append(
                {
                    "id": node_id,
                    "label": label_text,
                    "type": node_type,
                    "color": node_colors.get(node_type, "#64748b"),
                    "size": node_sizes.get(node_type, 10),
                    "properties": node_props,
                }
            )

            node_id_map[node_obj.id] = node_id
            return node_id

        def add_edge(source_id, target_id, rel_type):
            """Helper to add an edge"""
            if source_id and target_id:
                # Ensure IDs are strings
                source_str = str(source_id)
                target_str = str(target_id)
                edge_id = f"edge-{len(edges)}"

                edge_data = {
                    "id": edge_id,
                    "source": source_str,
                    "target": target_str,
                    "type": str(rel_type) if rel_type else "",
                    "size": 2,
                    "color": "#94a3b8",
                }
                edges.append(edge_data)
                logger.debug(
                    f"Created edge: {edge_id} from {source_str} to {target_str}"
                )

        # Add the target word (center node, make it larger)
        target_word = record["target_word"]
        word_id = add_node(target_word, "Word")
        if word_id:
            # Make the searched word larger
            for node in nodes:
                if node["id"] == word_id:
                    node["size"] = 15
                    node["color"] = "#3b82f6"  # Brighter blue for focus

        # Add context nodes (Text, Section, Phrase)
        text_node = record.get("text")
        section_node = record.get("section")
        phrase_node = record.get("phrase")

        text_id = add_node(text_node, "Text") if text_node else None
        section_id = add_node(section_node, "Section") if section_node else None
        phrase_id = add_node(phrase_node, "Phrase") if phrase_node else None

        # Add edges for context hierarchy
        if text_id and section_id:
            add_edge(text_id, section_id, "SECTION_PART_OF_TEXT")
        if section_id and phrase_id:
            add_edge(section_id, phrase_id, "PHRASE_IN_SECTION")
        if phrase_id and word_id:
            add_edge(phrase_id, word_id, "PHRASE_COMPOSED_OF")

        # Add target word morphemes and glosses
        morpheme_ids = []
        morpheme_id_map = {}  # neo4j id -> graph node id

        for morpheme in target_morphemes:
            if morpheme:
                m_id = add_node(morpheme, "Morpheme")
                if m_id and word_id:
                    morpheme_ids.append(m_id)
                    morpheme_id_map[morpheme.id] = m_id
                    add_edge(word_id, m_id, "WORD_MADE_OF")
                    logger.info(
                        f"Added morpheme: {morpheme.get('surface_form', 'unknown')}, edge from word {word_id} to morpheme {m_id}"
                    )

        # Add glosses - query to find correct morpheme relationships
        for gloss in target_glosses:
            if gloss:
                g_id = add_node(gloss, "Gloss")
                if g_id:
                    # Query which morpheme(s) this gloss analyzes
                    gloss_morph_query = """
                    MATCH (g:Gloss)-[:ANALYZES]->(m:Morpheme)
                    WHERE id(g) = $gloss_id
                    RETURN id(m) as morph_id
                    """
                    gm_result = db.run(gloss_morph_query, gloss_id=gloss.id)
                    for gm_rec in gm_result:
                        morph_graph_id = morpheme_id_map.get(gm_rec["morph_id"])
                        if morph_graph_id:
                            add_edge(g_id, morph_graph_id, "ANALYZES")
                            logger.info(
                                f"Added gloss edge from {g_id} to morpheme {morph_graph_id}"
                            )

        # Process related words - get their full data
        related_word_count = 0
        for rel_word in related_words:
            if not rel_word or related_word_count >= 10:
                break

            # Add related word node
            rw_id = add_node(rel_word, "Word")
            if not rw_id:
                continue

            logger.info(
                f"Adding related word: {rel_word.get('surface_form', 'unknown')}"
            )
            related_word_count += 1

            # Query to get this word's morphemes and glosses
            rel_word_query = """
            MATCH (w:Word)-[:WORD_MADE_OF]->(m:Morpheme)
            WHERE id(w) = $word_id
            OPTIONAL MATCH (g:Gloss)-[:ANALYZES]->(m)
            RETURN collect(DISTINCT m) as morphemes, collect(DISTINCT g) as glosses
            """
            rw_result = db.run(rel_word_query, word_id=rel_word.id)
            rw_record = rw_result.single()

            if rw_record:
                rw_morphemes = rw_record.get("morphemes", [])
                rw_glosses = rw_record.get("glosses", [])
                rw_morph_id_map = {}

                # Add morphemes for this related word
                for rw_morph in rw_morphemes:
                    if rw_morph:
                        rwm_id = add_node(rw_morph, "Morpheme")
                        if rwm_id:
                            rw_morph_id_map[rw_morph.id] = rwm_id
                            add_edge(rw_id, rwm_id, "WORD_MADE_OF")
                            logger.info(
                                f"Added morpheme for related word: {rw_morph.get('surface_form', 'unknown')}"
                            )

                # Add glosses for this related word
                for rw_gloss in rw_glosses:
                    if rw_gloss:
                        rwg_id = add_node(rw_gloss, "Gloss")
                        if rwg_id:
                            # Find which morpheme this gloss analyzes
                            rwg_morph_query = """
                            MATCH (g:Gloss)-[:ANALYZES]->(m:Morpheme)
                            WHERE id(g) = $gloss_id
                            RETURN id(m) as morph_id
                            """
                            rwgm_result = db.run(rwg_morph_query, gloss_id=rw_gloss.id)
                            for rwgm_rec in rwgm_result:
                                rwm_graph_id = rw_morph_id_map.get(rwgm_rec["morph_id"])
                                if rwm_graph_id:
                                    add_edge(rwg_id, rwm_graph_id, "ANALYZES")

        # Validate edges before returning
        node_id_set = {n["id"] for n in nodes}
        valid_edges = []

        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")

            if source in node_id_set and target in node_id_set:
                valid_edges.append(edge)
            else:
                logger.warning(
                    f"Skipping invalid edge: {edge['id']} - source={source} (exists={source in node_id_set}), target={target} (exists={target in node_id_set})"
                )

        logger.info(
            f"Returning {len(nodes)} nodes and {len(valid_edges)} valid edges (filtered {len(edges) - len(valid_edges)} invalid) for word '{word}'"
        )
        logger.info(f"Node types: {[n['type'] for n in nodes]}")
        logger.info(f"Sample edges: {valid_edges[:3] if valid_edges else 'none'}")

        return {
            "nodes": nodes,
            "edges": valid_edges,
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(valid_edges),
                "searched_word": word,
                "morpheme_count": len([n for n in nodes if n["type"] == "Morpheme"]),
                "related_word_count": len([n for n in nodes if n["type"] == "Word"])
                - 1,  # -1 for target word
            },
        }

    except Exception as e:
        logger.error(f"Error fetching word graph data: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=400, detail=f"Error fetching word graph data: {str(e)}"
        )


@router.get("/morpheme-graph-data")
async def get_morpheme_graph_data(
    morpheme: str,
    language: Optional[str] = None,
    db=Depends(get_db_dependency),
):
    """Get graph data for a specific morpheme

    This endpoint returns:
    - The searched morpheme node
    - All words that contain this morpheme
    - Parent phrases, sections, and texts for context
    - Glosses for the morpheme

    Args:
        morpheme: The form of the morpheme to search
        language: Optional language filter
    """
    try:
        nodes = []
        edges = []

        # Define colors for each node type
        node_colors = {
            "Text": "#f59e0b",  # amber
            "Section": "#8b5cf6",  # purple
            "Phrase": "#06b6d4",  # cyan
            "Word": "#0ea5e9",  # blue
            "Morpheme": "#10b981",  # green
            "Gloss": "#ec4899",  # pink
        }

        node_sizes = {
            "Text": 30,
            "Section": 22,
            "Phrase": 16,
            "Word": 10,
            "Morpheme": 8,
            "Gloss": 7,
        }

        # Find the morpheme and related data
        # Search in both surface_form and citation_form fields (case-insensitive)
        if language:
            lang_filter = "AND m.language = $language"
        else:
            lang_filter = ""

        cypher_query = f"""
        // Find all morpheme nodes matching the search term
        MATCH (m:Morpheme)
        WHERE (toLower(m.surface_form) CONTAINS toLower($morpheme) 
           OR toLower(m.citation_form) CONTAINS toLower($morpheme))
        {lang_filter}
        
        WITH collect(DISTINCT m) as all_morphemes
        
        // Take first morpheme as target
        WITH all_morphemes[0] as target_morpheme, all_morphemes
        
        // Get glosses for the target morpheme
        OPTIONAL MATCH (target_morpheme)<-[:ANALYZES]-(g:Gloss)
        WITH target_morpheme, all_morphemes, collect(DISTINCT g) as morpheme_glosses
        
        // Get all words containing ANY of these morphemes
        UNWIND all_morphemes as m
        OPTIONAL MATCH (w:Word)-[:WORD_MADE_OF]->(m)
        WITH target_morpheme, morpheme_glosses, collect(DISTINCT w) as related_words
        
        // Return just the essential data for sunburst visualization
        RETURN target_morpheme,
               morpheme_glosses,
               related_words
        """

        result = db.run(cypher_query, morpheme=morpheme, language=language)
        record = result.single()

        if not record or not record.get("target_morpheme"):
            logger.warning(f"Morpheme '{morpheme}' not found in database")
            return {
                "nodes": [],
                "edges": [],
                "stats": {"node_count": 0, "edge_count": 0},
                "message": f"Morpheme '{morpheme}' not found",
            }

        # Get data from record
        target_morpheme = record.get("target_morpheme")
        morpheme_glosses = record.get("morpheme_glosses", [])
        related_words = record.get("related_words", [])

        logger.info(f"Found morpheme '{morpheme}'")
        logger.info(f"Related words: {len(related_words)}")
        logger.info(f"Glosses: {len(morpheme_glosses)}")
        logger.info(
            f"Sample related words: {[w.get('surface_form', 'N/A') for w in related_words[:5]]}"
        )

        # Build nodes list
        node_id_set = set()

        # Add target morpheme
        if target_morpheme:
            morpheme_id = str(target_morpheme.get("ID"))
            # Use surface_form or citation_form for the label
            morpheme_form = (
                target_morpheme.get("surface_form")
                or target_morpheme.get("citation_form")
                or morpheme
            )
            nodes.append(
                {
                    "id": morpheme_id,
                    "label": morpheme_form,
                    "type": "Morpheme",
                    "color": node_colors["Morpheme"],
                    "size": node_sizes["Morpheme"] * 1.5,  # Make target larger
                    "properties": dict(target_morpheme),
                }
            )
            node_id_set.add(morpheme_id)

        # Add glosses
        for gloss_node in morpheme_glosses:
            if gloss_node:
                gloss_id = str(gloss_node.get("ID"))
                if gloss_id not in node_id_set:
                    # Glosses might have "annotation", "value", or "gloss" property
                    gloss_label = (
                        gloss_node.get("annotation")
                        or gloss_node.get("value")
                        or gloss_node.get("gloss")
                        or ""
                    )
                    nodes.append(
                        {
                            "id": gloss_id,
                            "label": gloss_label,
                            "type": "Gloss",
                            "color": node_colors["Gloss"],
                            "size": node_sizes["Gloss"],
                            "properties": dict(gloss_node),
                        }
                    )
                    node_id_set.add(gloss_id)

                    # Add edge from gloss to morpheme
                    edges.append(
                        {
                            "id": f"{gloss_id}-analyzes-{morpheme_id}",
                            "source": gloss_id,
                            "target": morpheme_id,
                            "type": "ANALYZES",
                            "color": "#60a5fa",
                            "size": 2,
                        }
                    )

        # Add related words (show all up to 50)
        logger.info(f"Adding {len(related_words[:50])} words to graph")
        for word_node in related_words[:50]:
            if word_node:
                word_id = str(word_node.get("ID"))
                if word_id not in node_id_set:
                    nodes.append(
                        {
                            "id": word_id,
                            "label": word_node.get("surface_form", ""),
                            "type": "Word",
                            "color": node_colors["Word"],
                            "size": node_sizes["Word"],
                            "properties": dict(word_node),
                        }
                    )
                    node_id_set.add(word_id)

                    # Add edge from word to morpheme
                    edges.append(
                        {
                            "id": f"{word_id}-made-of-{morpheme_id}",
                            "source": word_id,
                            "target": morpheme_id,
                            "type": "WORD_MADE_OF",
                            "color": "#60a5fa",
                            "size": 2,
                        }
                    )

        # Skip context nodes (texts, sections, phrases) for simpler visualization
        # Only show Words, Morpheme, and Glosses

        # Validate edges
        valid_edges = []
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")

            if source in node_id_set and target in node_id_set:
                valid_edges.append(edge)
            else:
                logger.warning(f"Skipping invalid edge: {edge['id']}")

        logger.info(
            f"Returning {len(nodes)} nodes and {len(valid_edges)} valid edges for morpheme '{morpheme}'"
        )

        return {
            "nodes": nodes,
            "edges": valid_edges,
            "stats": {
                "node_count": len(nodes),
                "edge_count": len(valid_edges),
                "searched_morpheme": morpheme,
                "related_word_count": len([n for n in nodes if n["type"] == "Word"]),
                "gloss_count": len([n for n in nodes if n["type"] == "Gloss"]),
            },
        }

    except Exception as e:
        logger.error(f"Error fetching morpheme graph data: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=400, detail=f"Error fetching morpheme graph data: {str(e)}"
        )


@router.delete("/wipe-database")
async def wipe_database(db=Depends(get_db_dependency)):
    """Wipe all linguistic data from the database

    WARNING: This will permanently delete all texts, sections, phrases, words,
    morphemes, and glosses from the database. This action cannot be undone.
    """
    try:
        # Delete all nodes and relationships in the correct order to avoid constraint violations
        wipe_queries = [
            # Delete all relationships first
            "MATCH ()-[r]-() DELETE r",
            # Delete all nodes
            "MATCH (n) DELETE n",
        ]

        deleted_counts = {}

        # Get counts before deletion for reporting
        count_queries = {
            "texts": "MATCH (t:Text) RETURN count(t) as count",
            "sections": "MATCH (s:Section) RETURN count(s) as count",
            "phrases": "MATCH (p:Phrase) RETURN count(p) as count",
            "words": "MATCH (w:Word) RETURN count(w) as count",
            "morphemes": "MATCH (m:Morpheme) RETURN count(m) as count",
            "glosses": "MATCH (g:Gloss) RETURN count(g) as count",
            "relationships": "MATCH ()-[r]-() RETURN count(r) as count",
        }

        for entity_type, query in count_queries.items():
            result = db.run(query)
            record = result.single()
            deleted_counts[entity_type] = record["count"] if record else 0

        # Execute wipe queries
        for query in wipe_queries:
            db.run(query)

        return {
            "message": "Database wiped successfully",
            "deleted_counts": deleted_counts,
            "warning": "All linguistic data has been permanently deleted",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error wiping database: {str(e)}")
