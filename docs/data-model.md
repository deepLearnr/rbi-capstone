# RBI Saathi data model (ER diagram)

This ER diagram is derived from the SQLAlchemy models and Alembic migrations. It documents the database shape, not a claim that every table is populated in every environment. For readability, timestamp columns and a few descriptive/optional columns are omitted from the diagram; they remain part of the SQLAlchemy models.

```mermaid
erDiagram
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : contains
    DOCUMENTS ||--o| REGULATORY_UPDATES : simplified_as
    DOCUMENTS o|--o{ LEARNING_MODULES : optionally_sources
    REGULATORY_UPDATES o|--o{ LEARNING_MODULES : optionally_inspires
    LEARNING_MODULES ||--o{ LEARNING_SECTIONS : has
    LEARNING_MODULES ||--o{ SCENARIOS : has
    LEARNING_MODULES ||--o{ ASSESSMENTS : has
    LEARNING_MODULES ||--o| LEARNING_PROGRESS : shared_demo_progress
    ASSESSMENTS ||--o{ ASSESSMENT_QUESTIONS : defines
    ASSESSMENTS ||--o{ ASSESSMENT_ATTEMPTS : records

    DOCUMENTS {
        int id PK
        string title
        string document_type
        string rbi_reference
        date publication_date
        string department
        text source_url
        string source_file
        string language
        text description
    }
    DOCUMENT_CHUNKS {
        int id PK
        int document_id FK
        int chunk_index
        text content
        int page_start
        int page_end
        text section_reference
        text heading
        text heading_path
        json metadata
        text content_hash
        vector_384 embedding
        text embedding_model
    }
    REGULATORY_UPDATES {
        int id PK
        int document_id FK_UQ
        string title
        string category
        date publication_date
        date effective_date
        string importance
        json simplification
    }
    LEARNING_MODULES {
        int id PK
        int document_id FK_NULL
        int regulatory_update_id FK_NULL
        string title
        string category
        string difficulty
        string status
    }
    LEARNING_SECTIONS {
        int id PK
        int module_id FK
        text title
        text content
        int section_order
    }
    SCENARIOS {
        int id PK
        int module_id FK
        string title
        string category
        text situation
        text question
        json options
        int correct_option
        text explanation
        text learning_reference
    }
    LEARNING_PROGRESS {
        int id PK
        int module_id FK_UQ
        json completed_section_ids
        int progress_percent
        boolean completed
        datetime updated_at
    }
    ASSESSMENTS {
        int id PK
        int module_id FK
        string title
        int duration_minutes
        int passing_score
    }
    ASSESSMENT_QUESTIONS {
        int id PK
        int assessment_id FK
        text question
        json options
        int correct_option
        text explanation
        int question_order
    }
    ASSESSMENT_ATTEMPTS {
        int id PK
        int assessment_id FK
        int score
        int total_questions
        boolean passed
        json answers
        datetime completed_at
    }
```

## Important keys and relationships

- `document_chunks.document_id` references `documents.id`; deleting a document cascades to its chunks.
- `regulatory_updates.document_id` is required and unique, so a document has at most one regulatory update record. Deleting the document cascades to its update.
- `learning_modules.document_id` and `learning_modules.regulatory_update_id` are nullable. Deleting either referenced record sets the corresponding module foreign key to `NULL`.
- `learning_sections`, `scenarios` and `assessments` belong to a learning module. Module deletion cascades to those records.
- `learning_progress.module_id` is unique. There is no `user_id` column; this is one shared demo progress row per module, not per-employee tracking.
- `assessment_questions` has a uniqueness constraint on `(assessment_id, question_order)`. Assessment attempts are associated with an assessment but have no employee/user foreign key.
- `document_chunks.embedding` is `vector(384)` and may be `NULL`; retrieval filters out rows with no embedding.
- The `document_chunks.metadata` column is PostgreSQL `JSON`. In Python it is exposed as `chunk_metadata` to avoid colliding with SQLAlchemy's reserved `metadata` attribute.
- `regulatory_updates.simplification` stores the seven required sections as JSON: `executive_summary`, `what_changed`, `why_it_matters`, `who_is_affected`, `what_should_i_do`, `important_dates`, and `terminology`.

## Important non-database state

The scenario interface's current question bank lives in `frontend/src/data/scenarios.js`; its attempted answers and sessions use browser `localStorage`. There is no corresponding current scenario API route in `backend/app/main.py`, and no user/authentication table in the database schema. The `scenarios` table exists in the schema, but the UI's active quiz catalog is not served from it. These states must not be represented as database-persisted learner records.

The ERD is a structural model. For the local database snapshot inspected on 12 October 2026, table counts and source/status metadata were separately inspected; see the repository audit handoff rather than assuming this diagram implies seeded rows.
