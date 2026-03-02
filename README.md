## Overview

This project implements an ingredient pairing framework based on semantic similarity of flavor descriptors derived from botanical literature. The approach leverages Natural Language Processing (NLP), Retrieval-Augmented Generation (RAG), and Latent Semantic Analysis (LSA) to identify ingredients with similar flavor profiles.

Rather than relying on experimental flavor chemistry data, this method infers flavor similarity from textual associations between ingredients and flavor descriptors within a large corpus describing edible plants indigenous to North America.

---

## Methodology

The ingredient pairing pipeline consists of four main stages:

### 1. Flavor Descriptor Extraction via RAG

Flavor descriptors were generated for each ingredient using Retrieval-Augmented Generation (RAG).

- A publicly available Large Language Model (LLM) was queried.
- Retrieval was performed over a curated corpus of books describing edible indigenous plants of North America.
- The model generated lists of qualitative flavor descriptors (e.g., *earthy, nutty, bitter, citrusy*) associated with each ingredient based on the retrieved textual context.

This approach grounds LLM outputs in domain-specific botanical literature, improving relevance and reducing hallucinations.

---

### 2. Descriptor Filtering and Binary Encoding

The generated descriptors were standardized to create a structured feature representation:

- Low-frequency descriptors were filtered to reduce noise.
- Synonymous and semantically redundant descriptors were grouped.
- Each ingredient was represented as a **binary feature vector**, where:

This resulted in a sparse ingredient × descriptor matrix capturing qualitative flavor attributes.

---

### 3. Latent Semantic Analysis via Singular Value Decomposition (SVD)

To reduce sparsity and capture latent semantic relationships between flavor descriptors, Latent Semantic Analysis (LSA) was performed.

- Singular Value Decomposition (SVD) was applied to the binary descriptor matrix:

- Each ingredient was projected into a lower-dimensional latent feature space.
- These latent vectors summarize the principal axes of variation in flavor.

This step enables detection of higher-order semantic relationships between ingredients beyond exact descriptor overlap.

---

### 4. Ingredient Similarity Computation

Similarity between ingredients was calculated using cosine distance in the latent semantic space.
Ingredients with the **lowest cosine distance** are considered to have the most similar flavor profiles.