# Interview Guide — Flipkart Grid Search Project

Use this document to prepare for **“Describe your project”**, **technical follow-ups**, and **system design** questions.

---

## 1. Elevator pitch (30 seconds)

> I built a Flipkart-inspired e-commerce search system with a **FastAPI backend** and **Next.js frontend**. The backend serves two main APIs: **autosuggest** and **product search**. Search is **hybrid**: I use **FAISS** for semantic similarity with sentence-transformer embeddings, plus an **inverted index** for exact keyword matches. Autosuggest combines **prefix trie**, **fuzzy and phonetic matching**, a **knowledge graph** built from product metadata, and **query templates** like “laptop under 50000”. The frontend mimics Flipkart’s UX—search, filters, sort, cart, and **delivery estimates** from the user’s GPS to warehouse coordinates. The dataset is ~15K real Flipkart-style products in JSON. I also have an optional **Elasticsearch Learning-to-Rank** module for advanced ranking experiments.

---

## 2. Describe the project (2–3 minutes)

### Problem

E-commerce search must handle **typos**, **synonyms**, **natural language** (“mobile under 15000”), and **fast suggestions**—not just exact title match.

### What you built

1. **Backend (`backend/main.py`)**  
   - Loads products at startup.  
   - Builds **FAISS indexes** (title + full text), **inverted index**, **phrase trie**, **phonetic map**, and a **NetworkX graph** linking phrases to categories, tags, and attributes.  
   - **`/autosuggest`**: Multi-strategy ranking; returns up to 8 suggestions.  
   - **`/search`**: Retrieves candidates semantically + lexically, filters, scores, returns facets and a sponsored product id.

2. **Frontend (`frontend/`)**  
   - Search bar with live suggest and keyboard navigation.  
   - Results grid with filters (price, rating, brand, category) and sort options.  
   - **Haversine-based delivery** from user location to each product’s warehouse.  
   - Cart and demo login via `localStorage`.

3. **Optional SRP (`SRP/`)**  
   - Elasticsearch with **LTR plugin** to rescore results using a trained linear model and feature set—shows awareness of production search stacks.

### Why it matters

You demonstrate **information retrieval** (lexical + vector), **NLP** (spaCy phrases, embeddings), **ranking** (weighted features, sponsored logic), and **full-stack integration**—aligned with Flipkart Grid themes.

### Trade-offs you can mention honestly

- Embeddings are **precomputed at startup** → fast queries, slower deploy/restart.  
- **In-memory JSON** → fine for demo; production would use Elasticsearch/OpenSearch + caching.  
- Hindi translation hook exists but is a **placeholder** (`translate_hindi_to_english` returns normalized text)—easy extension point.

---

## 3. Architecture (draw or explain)

```
Browser (Next.js)
    │  autosuggest, search, filters
    ▼
FastAPI
    ├── FAISS (semantic retrieval)
    ├── Inverted index (lexical)
    ├── Knowledge graph (suggest expansion)
    └── Scoring + facets + sponsored logic
    ▼
products.json
```

**Optional path:** Browser → SRP FastAPI → Elasticsearch + LTR rescore.

---

## 4. Questions interviewers often ask

### A. Project & motivation

| Question | How to answer |
|----------|----------------|
| **Why did you build this?** | Flipkart Grid focuses on search quality; I wanted a portfolio piece showing hybrid retrieval, autosuggest, and a realistic UI. |
| **What was the hardest part?** | Balancing **autosuggest latency vs quality**—many strategies (trie, fuzzy, graph, templates); merging and deduping without noisy suggestions. Or: **cold start** time for embedding all products. |
| **What would you improve next?** | Hindi/English query translation (Argos already stubbed in repo), user personalization, A/B testing ranking weights, move index build to offline pipeline, Redis cache for hot queries. |
| **How is this different from SQL `LIKE`?** | `LIKE` is exact substring; we add **semantic similarity**, **typo tolerance**, **synonyms/tags**, and **ranking signals** (rating, reviews, boost). |

### B. Autosuggest

| Question | How to answer |
|----------|----------------|
| **How does autosuggest work?** | Pipeline: trending → trie prefix → substring → fuzzy (if few hits) → phonetic → FAISS semantic neighbors → graph neighbors → templates (“X for Y”, “X under price”) → score by linked products’ boost/rating/reviews → return top 8. |
| **How do you handle typos?** | **RapidFuzz** partial/token match + **Double Metaphone** so “fone” can match phonetically similar phrases. |
| **What is the knowledge graph for?** | Nodes = phrases, categories, tags, attributes; edges from co-occurring product fields. Expands “shirt” to “shirt for men” if those nodes are neighbors. |
| **What are query templates?** | Rule-based completions from graph node types: tag → “for”, attribute → “with”, category → “in”; plus price buckets per product category. |

### C. Search & ranking

| Question | How to answer |
|----------|----------------|
| **Explain hybrid search.** | **FAISS** finds semantically similar products (top 50 from title + full text indexes). **Inverted index** adds products matching query tokens (with stemming). **Union** of IDs → filter → **weighted score**. |
| **Why FAISS?** | Approximate/exact vector search at scale; `IndexFlatL2` is simple and fast for ~15K vectors in memory. |
| **Why sentence-transformers?** | `all-MiniLM-L6-v2` gives 384-dim embeddings; good speed/quality trade-off for semantic matching. |
| **How do you rank results?** | `0.4×cosine_sim + 0.2×rating + 0.2×search_boost + 0.2×log(reviews)`; then apply user **sort** (price, rating, etc.). |
| **How does “laptop under 50000” work?** | Regex extracts price from query; sets `max_price`; category-specific price buckets also feed autosuggest. |
| **What is `search_boost`?** | Manual/promoted relevance signal; also used to pick **sponsored** product among high-boost items (not the #1 organic result). |
| **What are facets?** | `Counter` on brands/categories of **filtered** candidates—powers sidebar filter counts. |

### D. Frontend & system design

| Question | How to answer |
|----------|----------------|
| **How does delivery ETA work?** | Browser geolocation (fallback Bangalore); **Haversine** distance to `warehouse_loc.coords`; bucket into 1–7 days (`deliveryUtils.ts`). |
| **How do filters sync with search?** | `ResultsGrid` builds query string from `filters` state; `useEffect` refetches when query/filters/sort change. |
| **Why localStorage for cart?** | Demo scope; production needs auth, inventory API, and server-side cart. |
| **How would you scale this?** | Offline index builder → Elasticsearch/OpenSearch; embedding service; CDN for images; API gateway; cache autosuggest; horizontal FastAPI workers with shared vector index or dedicated search service. |

### E. Elasticsearch / SRP (if they dig deeper)

| Question | How to answer |
|----------|----------------|
| **What is Learning to Rank?** | First-stage retrieval (e.g. `match` on description), then **rescore** with LTR model using query-document features (BM25, popularity, etc.). |
| **Why both FAISS and Elasticsearch?** | Main app is self-contained for demo; SRP shows familiarity with **industry-standard** search + LTR plugins used in large catalogs. |

### F. Behavioral / ownership

| Question | How to answer |
|----------|----------------|
| **What did you personally implement?** | Be specific: e.g. autosuggest pipeline, hybrid search scoring, frontend search integration, delivery logic—match your actual contributions. |
| **Tell me about a bug you fixed.** | Example: sort not applying → traced `sort` param in `ResultsGrid` URL; sponsored flag using wrong id; location denied → Bangalore fallback. |

---

## 5. Questions YOU can ask the interviewer

1. How does your team measure search relevance (CTR, zero-result rate, NDCG)?  
2. Is autosuggest served from the same index as product search or a separate service?  
3. How do you handle sponsored vs organic blending in production?  
4. What’s the typical stack for catalog search at Flipkart—OpenSearch, custom ML, real-time features?  

---

## 6. Demo walkthrough checklist

Before the interview, run locally and practice:

- [ ] Empty search → trending in suggest dropdown  
- [ ] Type `lap` → see prefix + trending suggestions  
- [ ] Type `laptp` or typo → fuzzy/phonetic still suggests  
- [ ] Select `laptop under 50000` → results respect price  
- [ ] Change sort and filters → grid updates  
- [ ] Open cart, add item, refresh → persists  
- [ ] Mention delivery days change with location (or fallback)  
- [ ] Open `http://localhost:8000/docs` to show API contract  

---

## 7. Code walkthrough map (for “open any file” interviews)

| File | What to explain |
|------|-----------------|
| `backend/main.py` | Startup indexing; `autosuggest()` pipeline; `_compute_search()` hybrid retrieval + scoring |
| `frontend/components/Header.tsx` | `SearchBar` debounce/fetch, context path, keyboard UX |
| `frontend/components/ResultsGrid.tsx` | Search API integration, sponsored flag, delivery calculation |
| `frontend/lib/deliveryUtils.ts` | Haversine + day buckets |
| `SRP/main.py` | Elasticsearch query + LTR rescore |

---

## 8. One-liners (memorize if needed)

- **Hybrid search** = vectors catch meaning; inverted index catches exact tokens.  
- **Autosuggest** = retrieval (many strategies) + ranking (boost, rating, reviews).  
- **FAISS** = fast nearest-neighbor search in embedding space.  
- **Knowledge graph** = connect queries to categories/attributes for smarter completions.  
- **Sponsored** = high `search_boost` but not the most relevant organic hit.  

Good luck with your interview.
