# Data

This directory is reserved for public or simulated data used in later iterations.

- `raw/`: original public datasets or generated mock samples.
- `processed/`: cleaned and mapped datasets.
- `eval/`: model, RAG, and multi-agent review evaluation sets.
- `seed/`: generated mock SQL snippets for local demos.

The first round uses seed SQL and mock policy documents only. The second round adds UCI German Credit public data and simulated field mappings for a baseline risk model. Do not store real bank customer data, real identity card numbers, real phone numbers, or secrets here.
