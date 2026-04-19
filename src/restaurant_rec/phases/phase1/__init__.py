"""Phase 1: Hugging Face ingest, canonical schema, processed catalog."""

from restaurant_rec.phases.phase1.ingest import IngestStats, run_ingest

__all__ = ["IngestStats", "run_ingest"]
