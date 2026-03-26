"""Capability registry — all AI building blocks with metadata."""
from __future__ import annotations

LAYER_REGISTRY = {
    "foundation_models": {"name": "Foundation Models", "icon": "🧠", "order": 1, "description": "The core LLM or model powering your AI system"},
    "orchestration":     {"name": "Orchestration", "icon": "🔄", "order": 2, "description": "Frameworks and patterns that coordinate model calls and tool use"},
    "memory_context":    {"name": "Memory & Context", "icon": "🗄️", "order": 3, "description": "How your system stores and retrieves conversational and domain knowledge"},
    "data_grounding":    {"name": "Data & Grounding", "icon": "📚", "order": 4, "description": "Techniques for grounding model responses in real data"},
    "safety_control":    {"name": "Safety & Control", "icon": "🛡️", "order": 5, "description": "Guardrails, compliance, and human oversight mechanisms"},
    "observability":     {"name": "Observability", "icon": "📊", "order": 6, "description": "Monitoring, evaluation, and cost tracking for your AI system"},
    "deployment_scale":  {"name": "Deployment & Scale", "icon": "🚀", "order": 7, "description": "How your AI is deployed, served, and scaled"},
    "integration_ux":    {"name": "Integration & UX", "icon": "🔌", "order": 8, "description": "User interfaces and integration points"},
}

def _c(id, name, layer, icon, vendor, desc, fit, contra, cost, quality, latency, complexity, deps=None, questions=None):
    return {
        "id": id, "name": name, "layer": layer, "icon": icon, "vendor": vendor,
        "description": desc, "fit_signals": fit, "contra_signals": contra,
        "trade_offs": {"cost": cost, "quality": quality, "latency": latency, "complexity": complexity},
        "dependencies": deps or [], "interrogation": questions or [],
    }

CAPABILITY_REGISTRY = {
    # ── Foundation Models ───────────────────────────────────────────
    "gpt4o": _c("gpt4o", "GPT-4o", "foundation_models", "🧠", "OpenAI",
        "OpenAI's flagship multimodal model. Best-in-class reasoning, code, and instruction following.",
        ["complex_reasoning", "multimodal", "high_quality", "cloud_ok", "external_users", "enterprise_budget"],
        ["on_prem", "cost_critical", "ultra_low_latency", "vendor_lock_concern"],
        "high", "high", "medium", "low",
        questions=[
            {"q": "Does your use case require multi-step reasoning or complex problem solving?", "good": True},
            {"q": "Is it acceptable for data to be processed by a third-party cloud provider (OpenAI)?", "good": True},
            {"q": "Is minimising cost per query a primary requirement?", "good": False},
        ]
    ),
    "gpt4o_mini": _c("gpt4o_mini", "GPT-4o-mini", "foundation_models", "⚡", "OpenAI",
        "Fast, cost-effective OpenAI model. Great for high-volume tasks with simpler reasoning.",
        ["cost_critical", "high_volume", "cloud_ok", "simple_reasoning", "realtime"],
        ["complex_reasoning", "on_prem", "ultra_high_quality"],
        "low", "medium", "low", "low",
        questions=[
            {"q": "Is your use case primarily classification, extraction, or simple Q&A?", "good": True},
            {"q": "Do you process more than 10,000 queries per day?", "good": True},
            {"q": "Does the task require nuanced multi-step reasoning?", "good": False},
        ]
    ),
    "claude_35_sonnet": _c("claude_35_sonnet", "Claude 3.5 Sonnet", "foundation_models", "🎭", "Anthropic",
        "Anthropic's leading model. Exceptional at coding, analysis, and following nuanced instructions.",
        ["complex_reasoning", "high_quality", "cloud_ok", "compliance_aware", "long_context", "enterprise_budget"],
        ["on_prem", "cost_critical", "ultra_low_latency"],
        "high", "high", "medium", "low",
        questions=[
            {"q": "Is instruction-following accuracy and refusal of harmful requests critical?", "good": True},
            {"q": "Do you need to process very long documents (100K+ tokens)?", "good": True},
            {"q": "Is vendor diversity from OpenAI a concern for your organisation?", "good": True},
        ]
    ),
    "claude_haiku": _c("claude_haiku", "Claude Haiku", "foundation_models", "✍️", "Anthropic",
        "Anthropic's fastest model. Ideal for high-throughput, latency-sensitive tasks.",
        ["cost_critical", "high_volume", "realtime", "cloud_ok"],
        ["complex_reasoning", "on_prem"],
        "low", "medium", "low", "low",
        questions=[
            {"q": "Do you need responses in under 1 second?", "good": True},
            {"q": "Is the task simple enough for a smaller model (classification, extraction)?", "good": True},
            {"q": "Is highest possible answer quality more important than speed?", "good": False},
        ]
    ),
    "llama3_70b": _c("llama3_70b", "Llama 3.1 70B", "foundation_models", "🦙", "Meta (Open Source)",
        "Meta's open-source 70B model. Self-hostable, strong reasoning, no vendor dependency.",
        ["on_prem", "open_source_preferred", "vendor_lock_concern", "data_residency", "high_team_maturity"],
        ["low_team_maturity", "startup_budget", "ultra_low_latency"],
        "medium", "high", "medium", "high",
        questions=[
            {"q": "Does your team have ML infrastructure experience to deploy and manage a self-hosted model?", "good": True},
            {"q": "Is avoiding third-party model API providers a hard requirement?", "good": True},
            {"q": "Do you have GPU infrastructure available or budgeted?", "good": True},
        ]
    ),
    "mistral_large": _c("mistral_large", "Mistral Large", "foundation_models", "🌀", "Mistral AI",
        "European frontier model. Strong multilingual capabilities, EU data residency options.",
        ["multilingual", "data_residency", "eu_compliance", "cloud_ok"],
        ["ultra_low_latency", "on_prem"],
        "high", "high", "medium", "low",
        questions=[
            {"q": "Is EU data residency or GDPR compliance a driver for model selection?", "good": True},
            {"q": "Does your use case require strong multilingual support across European languages?", "good": True},
            {"q": "Are you already invested in the OpenAI or Anthropic ecosystem?", "good": False},
        ]
    ),
    "fine_tuned_model": _c("fine_tuned_model", "Fine-tuned Domain Model", "foundation_models", "🎯", "Custom",
        "A base model fine-tuned on proprietary domain data. Highest domain accuracy, but requires labeled data and MLOps.",
        ["fine_tuning_viable", "high_team_maturity", "domain_specific", "high_volume", "enterprise_budget"],
        ["low_team_maturity", "startup_budget", "low_scale", "no_labeled_data"],
        "very_high", "very_high", "low", "very_high",
        questions=[
            {"q": "Do you have at least 5,000 high-quality labeled examples in your domain?", "good": True},
            {"q": "Have you exhausted prompt engineering and RAG approaches first?", "good": True},
            {"q": "Do you have an MLOps team to manage retraining and evaluation cycles?", "good": True},
        ]
    ),

    # ── Orchestration ───────────────────────────────────────────────
    "langchain": _c("langchain", "LangChain", "orchestration", "⛓️", "LangChain",
        "The most widely adopted LLM orchestration framework. Rich ecosystem of integrations.",
        ["cloud_ok", "medium_team_maturity", "knowledge_base_heavy", "standard_rag"],
        ["ultra_low_latency", "minimal_dependencies"],
        "low", "medium", "medium", "medium",
        questions=[
            {"q": "Does your team already have experience with LangChain?", "good": True},
            {"q": "Do you need a large ecosystem of pre-built integrations?", "good": True},
            {"q": "Is minimal framework overhead a requirement?", "good": False},
        ]
    ),
    "llamaindex": _c("llamaindex", "LlamaIndex", "orchestration", "🦙", "LlamaIndex",
        "Data framework for LLM applications. Best-in-class for RAG pipelines and document ingestion.",
        ["knowledge_base_heavy", "unstructured_data", "standard_rag", "long_context"],
        ["multi_agent", "complex_tool_use"],
        "low", "high", "medium", "medium",
        questions=[
            {"q": "Is your primary use case document Q&A or knowledge base search?", "good": True},
            {"q": "Do you need sophisticated document parsing and chunking strategies?", "good": True},
            {"q": "Is multi-agent coordination a core requirement?", "good": False},
        ]
    ),
    "langgraph": _c("langgraph", "LangGraph", "orchestration", "🕸️", "LangChain",
        "Graph-based stateful agent framework. Best for complex multi-step agents and loops.",
        ["multi_agent", "stateful_conversation", "complex_tool_use", "high_team_maturity"],
        ["low_team_maturity", "simple_rag", "batch_ok"],
        "low", "high", "medium", "high",
        questions=[
            {"q": "Does your agent need to branch, loop, or make conditional decisions across steps?", "good": True},
            {"q": "Do you need human-in-the-loop checkpoints within agent execution?", "good": True},
            {"q": "Is your orchestration logic simple enough for a linear chain?", "good": False},
        ]
    ),
    "crewai": _c("crewai", "CrewAI", "orchestration", "👥", "CrewAI",
        "Multi-agent framework for collaborative AI teams. Role-based agents with shared goals.",
        ["multi_agent", "complex_reasoning", "high_team_maturity"],
        ["low_team_maturity", "simple_tasks", "cost_critical"],
        "low", "high", "low", "high",
        questions=[
            {"q": "Does your task naturally decompose into specialised sub-tasks handled by different agents?", "good": True},
            {"q": "Do you need agents to collaborate, debate, or validate each other's outputs?", "good": True},
            {"q": "Is cost per task a primary concern (multi-agent multiplies API calls)?", "good": False},
        ]
    ),
    "custom_agent_loop": _c("custom_agent_loop", "Custom Agent Loop", "orchestration", "🔁", "Custom",
        "Hand-rolled ReAct or tool-use loop. Full control, no framework overhead.",
        ["high_team_maturity", "ultra_low_latency", "minimal_dependencies", "vendor_lock_concern"],
        ["low_team_maturity", "rapid_prototyping"],
        "low", "medium", "low", "high",
        questions=[
            {"q": "Do you need sub-100ms agent overhead?", "good": True},
            {"q": "Is avoiding framework dependencies a hard requirement?", "good": True},
            {"q": "Do you have experienced ML engineers who can maintain custom orchestration code?", "good": True},
        ]
    ),
    "semantic_kernel": _c("semantic_kernel", "Semantic Kernel", "orchestration", "🔷", "Microsoft",
        "Microsoft's AI SDK. Deep Azure OpenAI integration, enterprise-ready, C# and Python.",
        ["existing_azure", "enterprise_budget", "cloud_ok"],
        ["open_source_preferred", "vendor_lock_concern"],
        "low", "high", "medium", "medium",
        questions=[
            {"q": "Is your organisation standardised on Microsoft Azure?", "good": True},
            {"q": "Do you need deep integration with Azure AI services and Microsoft 365?", "good": True},
            {"q": "Are you building on AWS or GCP as your primary cloud?", "good": False},
        ]
    ),

    # ── Memory & Context ────────────────────────────────────────────
    "faiss": _c("faiss", "FAISS", "memory_context", "🔍", "Meta (Open Source)",
        "In-memory vector store. Fast similarity search, no infrastructure cost. Good for prototyping.",
        ["low_scale", "rapid_prototyping", "open_source_preferred", "on_prem"],
        ["high_volume", "persistence_required", "distributed_scale"],
        "low", "medium", "low", "low",
        questions=[
            {"q": "Are you in a prototyping or proof-of-concept phase?", "good": True},
            {"q": "Is your vector index small enough to fit in memory (< 1M vectors)?", "good": True},
            {"q": "Do you need persistent, durable storage that survives restarts?", "good": False},
        ]
    ),
    "pinecone": _c("pinecone", "Pinecone", "memory_context", "🌲", "Pinecone",
        "Managed vector database. Serverless scaling, high availability, no infrastructure to manage.",
        ["cloud_ok", "high_volume", "enterprise_budget", "knowledge_base_heavy"],
        ["on_prem", "data_residency", "cost_critical"],
        "medium", "high", "low", "low",
        questions=[
            {"q": "Do you need a managed vector DB with no operational overhead?", "good": True},
            {"q": "Will you store more than 100K vectors or need multi-tenancy?", "good": True},
            {"q": "Is data residency or on-premise deployment required?", "good": False},
        ]
    ),
    "pgvector": _c("pgvector", "pgvector", "memory_context", "🐘", "PostgreSQL",
        "Vector search extension for Postgres. Combines relational and vector queries in one database.",
        ["existing_postgres", "structured_data", "hybrid_search", "on_prem", "cost_critical"],
        ["very_high_scale", "complex_ann"],
        "low", "medium", "medium", "medium",
        questions=[
            {"q": "Are you already running PostgreSQL in your stack?", "good": True},
            {"q": "Do you need to combine vector search with relational filters?", "good": True},
            {"q": "Do you need to search across more than 10 million vectors?", "good": False},
        ]
    ),
    "redis_cache": _c("redis_cache", "Redis Semantic Cache", "memory_context", "⚡", "Redis",
        "In-memory cache for LLM responses and embeddings. Dramatically reduces cost for repeated queries.",
        ["high_volume", "cost_critical", "realtime", "repeated_queries"],
        ["unique_queries", "low_scale"],
        "low", "medium", "very_low", "low",
        questions=[
            {"q": "Do you expect many users to ask similar or identical questions?", "good": True},
            {"q": "Is reducing API cost at scale a priority?", "good": True},
            {"q": "Is every query unique enough that caching would have low hit rate?", "good": False},
        ]
    ),
    "neo4j_graph": _c("neo4j_graph", "Neo4j Knowledge Graph", "memory_context", "🕸️", "Neo4j",
        "Graph database for knowledge representation. Excels at relationship-heavy domains.",
        ["relationship_heavy", "knowledge_graph_required", "complex_reasoning", "high_team_maturity"],
        ["low_team_maturity", "simple_rag", "startup_budget"],
        "high", "very_high", "medium", "very_high",
        questions=[
            {"q": "Does your domain have rich entity relationships (org charts, medical ontologies, etc.)?", "good": True},
            {"q": "Do users ask questions that require multi-hop reasoning across entities?", "good": True},
            {"q": "Does your team have graph database experience?", "good": True},
        ]
    ),
    "conversation_buffer": _c("conversation_buffer", "Conversation Buffer", "memory_context", "💬", "Custom",
        "Simple in-memory conversation history. No vector store needed for short sessions.",
        ["simple_chat", "low_scale", "stateful_conversation", "rapid_prototyping"],
        ["long_sessions", "high_volume", "cross_session_memory"],
        "low", "low", "very_low", "very_low",
        questions=[
            {"q": "Are your conversations short (< 20 turns)?", "good": True},
            {"q": "Is there no need for memory that persists across sessions?", "good": True},
            {"q": "Do users need to reference information from previous sessions?", "good": False},
        ]
    ),

    # ── Data & Grounding ────────────────────────────────────────────
    "naive_rag": _c("naive_rag", "Naive RAG", "data_grounding", "📄", "Custom",
        "Basic retrieve-then-generate. Embed documents, search by similarity, inject into prompt.",
        ["knowledge_base_heavy", "unstructured_data", "medium_team_maturity", "rapid_prototyping"],
        ["complex_reasoning", "very_high_quality", "structured_data"],
        "low", "medium", "medium", "low",
        questions=[
            {"q": "Do you have a corpus of documents users need to query?", "good": True},
            {"q": "Is a basic vector similarity search sufficient for your retrieval needs?", "good": True},
            {"q": "Do users ask complex analytical questions that require multiple documents?", "good": False},
        ]
    ),
    "hybrid_search": _c("hybrid_search", "Hybrid Search", "data_grounding", "🔀", "Custom",
        "Combines BM25 keyword search with vector search. Higher recall, especially for exact term matching.",
        ["knowledge_base_heavy", "high_quality", "enterprise_budget"],
        ["rapid_prototyping", "startup_budget", "simple_rag"],
        "medium", "high", "medium", "medium",
        questions=[
            {"q": "Do users frequently search for specific product names, codes, or technical terms?", "good": True},
            {"q": "Is recall (finding all relevant documents) as important as precision?", "good": True},
            {"q": "Is this a simple internal knowledge base with non-technical users?", "good": False},
        ]
    ),
    "reranker": _c("reranker", "Re-ranker", "data_grounding", "🏆", "Cohere / Custom",
        "Cross-encoder that re-ranks retrieved documents by relevance. Improves RAG precision significantly.",
        ["high_quality", "knowledge_base_heavy", "enterprise_budget", "grounding_critical"],
        ["cost_critical", "ultra_low_latency", "simple_rag"],
        "medium", "very_high", "medium", "medium",
        ["naive_rag", "hybrid_search"],
        questions=[
            {"q": "Is retrieval precision (top-ranked results being highly relevant) critical?", "good": True},
            {"q": "Can you afford the additional latency and cost of a re-ranking step?", "good": True},
            {"q": "Is your document corpus small enough that simple vector search is already accurate?", "good": False},
        ]
    ),
    "contextual_chunking": _c("contextual_chunking", "Contextual Chunking", "data_grounding", "✂️", "Custom",
        "Intelligent document chunking that preserves semantic context. Better than fixed-size splits.",
        ["knowledge_base_heavy", "long_context", "high_quality", "unstructured_data"],
        ["simple_documents", "rapid_prototyping"],
        "low", "high", "low", "medium",
        questions=[
            {"q": "Do your documents have complex structure (tables, headers, cross-references)?", "good": True},
            {"q": "Are you finding that retrieved chunks often lack context to answer questions?", "good": True},
            {"q": "Are your documents short and uniformly structured?", "good": False},
        ]
    ),
    "sql_connector": _c("sql_connector", "SQL / Database Connector", "data_grounding", "🗃️", "Custom",
        "Natural language to SQL. Allows AI to query structured databases directly.",
        ["structured_data", "analytics_use_case", "enterprise_budget"],
        ["unstructured_data_only", "no_database"],
        "low", "high", "medium", "high",
        questions=[
            {"q": "Do users need to query structured data from databases or data warehouses?", "good": True},
            {"q": "Is the database schema stable and well-documented?", "good": True},
            {"q": "Are the data sources primarily unstructured (PDFs, emails, web pages)?", "good": False},
        ]
    ),
    "streaming_ingestion": _c("streaming_ingestion", "Real-time Data Ingestion", "data_grounding", "📡", "Custom",
        "Continuous ingestion pipeline for live data feeds. Keeps the knowledge base current.",
        ["streaming_data", "realtime", "high_volume", "enterprise_budget", "high_team_maturity"],
        ["static_data", "low_team_maturity", "startup_budget"],
        "high", "high", "medium", "very_high",
        questions=[
            {"q": "Does your data change frequently and users expect up-to-date answers?", "good": True},
            {"q": "Do you have a data engineering team to build and maintain pipelines?", "good": True},
            {"q": "Is your data relatively static (updated monthly or less)?", "good": False},
        ]
    ),
    "knowledge_graph_rag": _c("knowledge_graph_rag", "Graph RAG", "data_grounding", "🗺️", "Custom",
        "RAG over a knowledge graph. Enables multi-hop reasoning across entity relationships.",
        ["relationship_heavy", "complex_reasoning", "high_team_maturity", "enterprise_budget"],
        ["low_team_maturity", "simple_rag", "startup_budget"],
        "very_high", "very_high", "medium", "very_high",
        ["neo4j_graph"],
        questions=[
            {"q": "Do your questions require connecting information across multiple entities?", "good": True},
            {"q": "Is your domain relationship-heavy (medical, legal, supply chain)?", "good": True},
            {"q": "Would standard vector search satisfy most of your retrieval needs?", "good": False},
        ]
    ),

    # ── Safety & Control ────────────────────────────────────────────
    "guardrails": _c("guardrails", "Guardrails AI", "safety_control", "🛡️", "Guardrails AI",
        "Framework for validating and correcting LLM outputs. Enforce schemas, detect hallucinations.",
        ["compliance_heavy", "high_data_sensitivity", "external_users", "grounding_critical"],
        ["ultra_low_latency", "simple_internal"],
        "medium", "high", "medium", "medium",
        questions=[
            {"q": "Do you need structured output validation (JSON schema compliance)?", "good": True},
            {"q": "Is output accuracy and safety critical (medical, financial, legal)?", "good": True},
            {"q": "Is this an internal prototype where occasional errors are acceptable?", "good": False},
        ]
    ),
    "pii_masking": _c("pii_masking", "PII Masking / Anonymisation", "safety_control", "🎭", "Custom / AWS Comprehend",
        "Detect and redact personally identifiable information before sending to LLM APIs.",
        ["high_data_sensitivity", "compliance_heavy", "external_users", "gdpr", "hipaa"],
        ["internal_only", "no_pii_data"],
        "medium", "high", "medium", "medium",
        questions=[
            {"q": "Do users share or does your data contain PII (names, emails, health data)?", "good": True},
            {"q": "Do you operate in a regulated industry (healthcare, finance, legal)?", "good": True},
            {"q": "Is all data fully anonymised before it reaches your AI system?", "good": False},
        ]
    ),
    "output_filter": _c("output_filter", "Output Content Filter", "safety_control", "🔒", "OpenAI / Custom",
        "Filter model outputs for harmful, inappropriate, or off-topic content before showing users.",
        ["external_users", "compliance_heavy", "consumer_facing"],
        ["internal_only", "trusted_users"],
        "low", "high", "medium", "low",
        questions=[
            {"q": "Is your AI facing external or consumer users who might receive harmful outputs?", "good": True},
            {"q": "Is your brand reputation at risk if the model generates inappropriate content?", "good": True},
            {"q": "Are all users internal employees with appropriate oversight?", "good": False},
        ]
    ),
    "human_in_loop": _c("human_in_loop", "Human-in-the-Loop", "safety_control", "👤", "Custom",
        "Route low-confidence or high-risk decisions to human review before acting.",
        ["compliance_heavy", "high_stakes_decisions", "external_users", "regulated_industry"],
        ["fully_automated", "high_volume", "realtime"],
        "high", "very_high", "very_low", "high",
        questions=[
            {"q": "Are there decisions in your workflow that carry significant risk if wrong?", "good": True},
            {"q": "Do your users or regulators expect human oversight of AI decisions?", "good": True},
            {"q": "Is fully automated, high-throughput processing a core requirement?", "good": False},
        ]
    ),
    "audit_logging": _c("audit_logging", "Audit Logging", "safety_control", "📋", "Custom",
        "Immutable logs of all AI inputs, outputs, and decisions. Required for regulated industries.",
        ["compliance_heavy", "gdpr", "hipaa", "sox", "enterprise_budget", "external_users"],
        ["startup_budget", "internal_prototype"],
        "medium", "high", "low", "medium",
        questions=[
            {"q": "Does your industry require audit trails for AI-generated decisions?", "good": True},
            {"q": "Could you face regulatory scrutiny or legal action based on AI outputs?", "good": True},
            {"q": "Is this an internal prototype with no compliance requirements?", "good": False},
        ]
    ),
    "prompt_injection_defense": _c("prompt_injection_defense", "Prompt Injection Defence", "safety_control", "💉", "Custom",
        "Detect and block attempts to manipulate the AI via adversarial user inputs.",
        ["external_users", "tool_use", "multi_agent", "agentic_systems"],
        ["internal_only", "simple_chat"],
        "low", "high", "medium", "medium",
        questions=[
            {"q": "Does your AI have access to tools or external systems that could be abused?", "good": True},
            {"q": "Do untrusted external users have direct input to your AI system?", "good": True},
            {"q": "Is the AI accessed only by trusted internal users with no tool access?", "good": False},
        ]
    ),

    # ── Observability ───────────────────────────────────────────────
    "langsmith": _c("langsmith", "LangSmith", "observability", "🔭", "LangChain",
        "Tracing, evaluation, and debugging for LangChain apps. Excellent developer experience.",
        ["langchain_user", "medium_team_maturity", "cloud_ok"],
        ["non_langchain", "on_prem", "data_residency"],
        "medium", "high", "low", "low",
        ["langchain"],
        questions=[
            {"q": "Are you using LangChain or LangGraph as your orchestration framework?", "good": True},
            {"q": "Do you need to trace and debug complex multi-step chains?", "good": True},
            {"q": "Are you using a framework other than LangChain?", "good": False},
        ]
    ),
    "langfuse": _c("langfuse", "Langfuse", "observability", "🌿", "Langfuse (Open Source)",
        "Open-source LLM observability. Self-hostable, framework-agnostic tracing and evals.",
        ["open_source_preferred", "on_prem", "any_framework", "high_team_maturity"],
        ["low_team_maturity"],
        "low", "high", "low", "medium",
        questions=[
            {"q": "Are you using a framework other than LangChain (or want framework-agnostic tracing)?", "good": True},
            {"q": "Is self-hosting your observability stack a preference?", "good": True},
            {"q": "Do you need a fully managed SaaS solution with zero ops overhead?", "good": False},
        ]
    ),
    "custom_eval": _c("custom_eval", "Custom Eval Harness", "observability", "🧪", "Custom",
        "Domain-specific evaluation framework. Test against ground truth, measure accuracy over time.",
        ["grounding_critical", "high_team_maturity", "enterprise_budget", "compliance_heavy"],
        ["rapid_prototyping", "low_team_maturity"],
        "high", "very_high", "low", "very_high",
        questions=[
            {"q": "Do you have domain experts who can create ground-truth evaluation datasets?", "good": True},
            {"q": "Is measuring and improving model accuracy over time a business requirement?", "good": True},
            {"q": "Are you in early-stage prototyping with no production SLAs yet?", "good": False},
        ]
    ),
    "cost_monitor": _c("cost_monitor", "Cost Monitoring Dashboard", "observability", "💰", "Custom",
        "Track LLM API spend per user, tenant, or feature. Prevent bill shock at scale.",
        ["high_volume", "enterprise_budget", "multi_tenant", "cost_critical"],
        ["low_scale", "single_user"],
        "low", "medium", "low", "medium",
        questions=[
            {"q": "Do you serve multiple teams or customers who each need cost attribution?", "good": True},
            {"q": "Is LLM API cost a significant or unpredictable line item in your budget?", "good": True},
            {"q": "Are you building a single-user internal tool with predictable usage?", "good": False},
        ]
    ),
    "ab_testing": _c("ab_testing", "A/B Testing Framework", "observability", "⚗️", "Custom",
        "Run experiments comparing prompt versions, models, or retrieval strategies.",
        ["enterprise_budget", "high_volume", "high_team_maturity", "grounding_critical"],
        ["rapid_prototyping", "low_scale", "startup_budget"],
        "medium", "very_high", "low", "high",
        questions=[
            {"q": "Do you need to systematically compare model versions or prompt strategies?", "good": True},
            {"q": "Is continuous improvement of AI quality a core product requirement?", "good": True},
            {"q": "Are you building a one-off tool rather than a continuously improving product?", "good": False},
        ]
    ),

    # ── Deployment & Scale ──────────────────────────────────────────
    "rest_api": _c("rest_api", "REST API (FastAPI)", "deployment_scale", "🌐", "Custom",
        "Standard HTTP API layer. Decouples your AI from frontends, enables multi-client access.",
        ["external_users", "multi_client", "enterprise_budget", "high_team_maturity"],
        ["single_internal_user", "rapid_prototyping"],
        "low", "high", "medium", "medium",
        questions=[
            {"q": "Do you need to serve the AI capability to multiple clients or frontends?", "good": True},
            {"q": "Will other services need to call your AI programmatically?", "good": True},
            {"q": "Is this a standalone tool used only via a single UI?", "good": False},
        ]
    ),
    "streaming_api": _c("streaming_api", "Streaming API (SSE/WebSocket)", "deployment_scale", "🌊", "Custom",
        "Stream model tokens to the user as they're generated. Dramatically improves perceived latency.",
        ["external_users", "chat_interface", "realtime", "high_quality"],
        ["batch_ok", "internal_batch"],
        "low", "high", "very_low", "medium",
        questions=[
            {"q": "Do users interact with the AI via a chat interface and expect real-time responses?", "good": True},
            {"q": "Is perceived response speed important for user satisfaction?", "good": True},
            {"q": "Is your use case batch processing where users don't wait for results?", "good": False},
        ]
    ),
    "prompt_cache": _c("prompt_cache", "Prompt Caching", "deployment_scale", "💾", "OpenAI / Anthropic",
        "Cache repeated prompt prefixes (system prompts, documents) to reduce latency and cost.",
        ["high_volume", "long_context", "cost_critical", "repeated_system_prompts"],
        ["fully_dynamic_prompts"],
        "low", "high", "very_low", "very_low",
        questions=[
            {"q": "Do you use long system prompts or inject large documents that repeat across calls?", "good": True},
            {"q": "Do you process more than 1,000 API calls per day?", "good": True},
            {"q": "Are all your prompts fully dynamic with no repeating prefix?", "good": False},
        ]
    ),
    "azure_openai": _c("azure_openai", "Azure OpenAI Service", "deployment_scale", "☁️", "Microsoft",
        "OpenAI models deployed in Azure. EU data residency, private networking, enterprise SLAs.",
        ["existing_azure", "data_residency", "enterprise_budget", "compliance_heavy", "eu_compliance"],
        ["open_source_preferred", "aws_only"],
        "high", "high", "medium", "medium",
        questions=[
            {"q": "Is your organisation already on Microsoft Azure?", "good": True},
            {"q": "Do you need EU data residency with OpenAI model quality?", "good": True},
            {"q": "Are you committed to open-source or non-Microsoft cloud providers?", "good": False},
        ]
    ),
    "on_prem_deploy": _c("on_prem_deploy", "On-Premise Deployment", "deployment_scale", "🏢", "Custom",
        "Deploy the entire AI stack within your own data centre. Maximum data control.",
        ["on_prem", "data_residency", "compliance_heavy", "high_team_maturity", "enterprise_budget"],
        ["cloud_ok", "low_team_maturity", "startup_budget", "rapid_prototyping"],
        "very_high", "high", "medium", "very_high",
        questions=[
            {"q": "Is on-premise deployment a hard requirement (regulatory or security)?", "good": True},
            {"q": "Do you have a DevOps/infrastructure team to manage the deployment?", "good": True},
            {"q": "Would a sovereign cloud option (Azure Gov, AWS GovCloud) satisfy your requirements?", "good": False},
        ]
    ),
    "multi_tenant_routing": _c("multi_tenant_routing", "Multi-Tenant Routing", "deployment_scale", "🏘️", "Custom",
        "Route requests to tenant-specific models, prompts, and data. Essential for SaaS AI products.",
        ["multi_tenant", "enterprise_budget", "external_users", "high_team_maturity"],
        ["single_tenant", "internal_only"],
        "high", "high", "low", "very_high",
        questions=[
            {"q": "Are you building a SaaS product where each customer needs isolated AI contexts?", "good": True},
            {"q": "Do different customers need different models, prompts, or knowledge bases?", "good": True},
            {"q": "Are you building for a single organisation with a shared knowledge base?", "good": False},
        ]
    ),

    # ── Integration & UX ────────────────────────────────────────────
    "chat_interface": _c("chat_interface", "Chat Interface (Web)", "integration_ux", "💬", "Custom",
        "Web-based conversational UI. The standard interaction pattern for conversational AI.",
        ["external_users", "stateful_conversation", "realtime", "consumer_facing"],
        ["batch_only", "api_only"],
        "medium", "high", "medium", "medium",
        questions=[
            {"q": "Is the primary user interaction conversational (back-and-forth dialogue)?", "good": True},
            {"q": "Do users access the AI via a web browser?", "good": True},
            {"q": "Is the primary use case batch processing or API-to-API integration?", "good": False},
        ]
    ),
    "slack_teams_bot": _c("slack_teams_bot", "Slack / Teams Bot", "integration_ux", "💼", "Custom",
        "Deploy AI directly into collaboration tools. High adoption for internal use cases.",
        ["internal_users", "existing_slack_teams", "enterprise_budget"],
        ["external_users", "consumer_facing"],
        "medium", "high", "medium", "medium",
        questions=[
            {"q": "Is this primarily an internal tool for employees?", "good": True},
            {"q": "Does your organisation use Slack or Microsoft Teams as primary communication?", "good": True},
            {"q": "Do you need to serve external customers who don't have Slack/Teams access?", "good": False},
        ]
    ),
    "voice_interface": _c("voice_interface", "Voice Interface", "integration_ux", "🎤", "OpenAI / Custom",
        "Speech-to-text and text-to-speech for voice-enabled AI. Higher engagement, accessibility.",
        ["voice_required", "accessibility", "multimodal", "external_users"],
        ["text_only", "cost_critical"],
        "high", "high", "medium", "high",
        questions=[
            {"q": "Do users need to interact with the AI via voice (call centre, hands-free)?", "good": True},
            {"q": "Is accessibility for users who struggle with text a key requirement?", "good": True},
            {"q": "Are text-based interfaces sufficient for all your target users?", "good": False},
        ]
    ),
    "api_sdk": _c("api_sdk", "Developer API / SDK", "integration_ux", "📦", "Custom",
        "Published API and SDK for developers to integrate your AI capability into their own apps.",
        ["developer_platform", "multi_client", "enterprise_budget", "high_team_maturity"],
        ["single_use_case", "internal_only"],
        "high", "very_high", "medium", "very_high",
        questions=[
            {"q": "Are you building a platform that other developers or teams will integrate with?", "good": True},
            {"q": "Do you need to expose your AI capability as a product to external developers?", "good": True},
            {"q": "Is this AI capability consumed only by a single internal application?", "good": False},
        ]
    ),
    "webhook_system": _c("webhook_system", "Webhook System", "integration_ux", "🔔", "Custom",
        "Event-driven integration. Trigger AI workflows from external system events.",
        ["event_driven", "enterprise_budget", "high_team_maturity", "existing_integrations"],
        ["simple_chat", "synchronous_only"],
        "medium", "high", "low", "high",
        questions=[
            {"q": "Does your AI need to react to events from other systems (new document, ticket, etc.)?", "good": True},
            {"q": "Is your architecture event-driven rather than request-response?", "good": True},
            {"q": "Is the primary interaction model synchronous user queries?", "good": False},
        ]
    ),
}

def get_layers_ordered():
    """Return layer IDs sorted by order."""
    return sorted(LAYER_REGISTRY.keys(), key=lambda k: LAYER_REGISTRY[k]["order"])

def get_caps_for_layer(layer_id):
    """Return all capabilities for a given layer."""
    return [c for c in CAPABILITY_REGISTRY.values() if c["layer"] == layer_id]
