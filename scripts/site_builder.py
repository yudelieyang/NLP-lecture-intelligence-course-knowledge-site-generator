from __future__ import annotations

import html
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.models import LectureUnit, SourceSection
from scripts.utils import (
    build_heuristic_chinese_note,
    contains_course_metadata,
    count_ascii_words,
    count_chinese_chars,
    detect_english_leakage,
    is_low_quality_chinese_fallback,
    looks_like_raw_english_dump,
    normalize_ws,
    rewrite_mixed_paragraph_to_chinese,
    rewrite_source_text_to_chinese_note,
    strip_course_metadata,
)


COMMON_TERMS = [
    "language model",
    "n-gram",
    "smoothing",
    "perplexity",
    "bag-of-words",
    "BOW",
    "TF-IDF",
    "cosine similarity",
    "PCA",
    "word embedding",
    "distributional semantics",
    "word2vec",
    "supervised learning",
    "feature vector",
    "classification",
    "loss function",
    "gradient descent",
    "neural network",
    "activation function",
    "backpropagation",
    "sequence data",
    "RNN",
    "hidden state",
    "vanishing gradient",
    "LSTM",
    "GRU",
    "encoder-decoder",
    "machine translation",
    "attention",
    "attention weights",
    "self-attention",
    "Transformer",
    "BERT",
    "GPT",
    "T5",
    "pretraining",
    "fine-tuning",
    "text-to-text",
    "next-token prediction",
    "ASR",
    "audio processing",
    "acoustic model",
]


FALLBACK_TERM_EXPLANATIONS: dict[str, str] = {
    "language model": "language model 是为 token 序列分配概率的模型，用来判断一句话有多可能，或预测下一个 token。",
    "n-gram": "n-gram 用前面有限个 token 近似完整历史上下文，是早期 language model 的核心简化。",
    "smoothing": "smoothing 为训练集中没见过的 n-gram 分配非零概率，缓解数据稀疏导致的零概率问题。",
    "perplexity": "perplexity 衡量 language model 对测试文本的不确定性，通常越低表示模型越能解释测试语料。",
    "bag-of-words": "bag-of-words 将文档表示为词项计数或权重向量，牺牲词序来换取简单、可计算的文本表示。",
    "BOW": "BOW 是 bag-of-words 的缩写，把文本转成词项维度上的向量，常用于检索、分类和相似度计算。",
    "TF-IDF": "TF-IDF 同时考虑词频和逆文档频率，用来突出对某篇文档更有区分度的词。",
    "cosine similarity": "cosine similarity 用向量夹角衡量两个文本向量的相似度，比向量长度更关注方向。",
    "PCA": "PCA 通过线性投影保留主要方差方向，常用于降维、可视化和分析 embedding 空间结构。",
    "word embedding": "word embedding 将离散词映射到连续向量空间，使语义或上下文相近的词在向量空间中更接近。",
    "distributional semantics": "distributional semantics 基于“上下文相似则意义相似”的思想，用词的分布模式解释语义。",
    "word2vec": "word2vec 通过预测上下文或中心词学习 word embedding，是 distributional semantics 的神经化实现。",
    "supervised learning": "supervised learning 使用带标签样本学习从输入到输出的映射，典型任务包括 classification 和 regression。",
    "feature vector": "feature vector 是把原始对象转成模型可计算的数值特征后的表示。",
    "classification": "classification 是把输入分到离散类别中的 supervised learning 任务。",
    "loss function": "loss function 衡量模型预测和真实标签之间的差距，是训练优化的目标。",
    "gradient descent": "gradient descent 沿损失下降最快方向迭代更新参数，是训练神经网络和许多 ML 模型的基础方法。",
    "neural network": "neural network 由多层可学习参数和 activation function 组成，用于自动学习非线性表示。",
    "activation function": "activation function 给 neural network 引入非线性，使模型不只是线性变换的堆叠。",
    "backpropagation": "backpropagation 用链式法则把 loss 的梯度从输出层传回各层参数。",
    "sequence data": "sequence data 是有顺序依赖的数据，例如文本 token 序列和语音帧序列。",
    "RNN": "RNN 通过 hidden state 在时间步之间传递历史信息，用于处理 sequence data。",
    "hidden state": "hidden state 是 RNN 在每个时间步保存历史上下文的内部状态。",
    "vanishing gradient": "vanishing gradient 指梯度在长链路反传时逐渐变小，导致模型难以学习长期依赖。",
    "LSTM": "LSTM 使用 input/forget/output gates 控制记忆读写，用来缓解普通 RNN 的 long-term dependency 问题。",
    "GRU": "GRU 用 update/reset gates 简化 LSTM 的门控记忆结构，在效率和记忆能力之间折中。",
    "encoder-decoder": "encoder-decoder 先把输入序列编码成表示，再由 decoder 生成输出序列，常用于 machine translation。",
    "machine translation": "machine translation 将一种语言的文本自动转换成另一种语言，是典型 sequence-to-sequence 任务。",
    "attention": "attention 让模型根据当前任务动态关注输入序列中的相关位置，而不是把所有信息压缩成单一向量。",
    "attention weights": "attention weights 是 attention 对不同输入位置分配的重要性权重。",
    "self-attention": "self-attention 让同一序列内部的 token 彼此建立直接关系，是 Transformer 的核心机制。",
    "Transformer": "Transformer 用 self-attention 和 feed-forward layers 建模序列关系，减少 RNN 的串行瓶颈。",
    "BERT": "BERT 通过 bidirectional context 和 masked language modeling 学习适合理解任务的上下文表示。",
    "GPT": "GPT 通常使用 decoder-only Transformer，通过 autoregressive next-token prediction 进行生成式预训练。",
    "T5": "T5 将多种 NLP 任务统一为 text-to-text 格式，输入和输出都表示为文本。",
    "ASR": "ASR 将 speech signal 转换为文本，通常结合 acoustic model 与 language model。",
    "audio processing": "audio processing 处理 waveform、spectrogram 等连续语音信号，是 speech NLP 的输入基础。",
    "acoustic model": "acoustic model 建模音频特征与语音单位之间的关系，是 ASR 系统的重要组成。",
}

FALLBACK_TERM_EXPLANATIONS.update(
    {
        "pretraining": "pretraining 指模型先在大规模通用数据上学习可迁移表示或生成能力，再把这些能力迁移到具体 NLP 任务中。",
        "fine-tuning": "fine-tuning 指在预训练模型基础上，用较小的任务数据继续训练参数，使模型适配分类、问答、生成等具体任务。",
        "text-to-text": "text-to-text 把不同 NLP 任务统一成文本输入到文本输出的格式，T5 用这种框架把翻译、摘要、问答等任务放进同一接口。",
        "next-token prediction": "next-token prediction 是 GPT-style language model 的核心训练目标：根据已有上下文预测下一个 token。",
    }
)


SECTION_FALLBACKS = [
    "Core Idea",
    "Model Workflow",
    "Key Example",
    "Evaluation Setup",
    "Practical Limitation",
    "Conceptual Bridge",
]


OFFLINE_CAPABILITIES = [
    "source_explorer",
    "search",
    "slide_figures",
    "slide_gallery",
    "lecture_map",
    "cross_lecture_references",
    "template_practice",
]


LLM_CAPABILITIES = [
    "chinese_summaries",
    "enriched_glossary",
    "creative_extension_practice",
    "application_scenarios",
    "advanced_code_cloze",
    "cross_lecture_reasoning",
]


FEATURE_MATRIX = [
    ("features.pdfReading", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.versionedOutput", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.sourceRefs", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.cleanedExcerpts", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.searchIndex", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.slideFigures", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.slideGallery", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.lectureMap", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.crossLectureReferences", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.basicGlossary", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.enrichedGlossary", "mode.limitedOffline", "mode.availableWithLlm"),
    ("features.templatePractice", "mode.availableOffline", "mode.availableWithLlm"),
    ("features.chineseSummaries", "mode.requiresLlm", "mode.availableWithLlm"),
    ("features.creativePractice", "mode.requiresLlm", "mode.availableWithLlm"),
    ("features.applicationScenarios", "mode.requiresLlm", "mode.availableWithLlm"),
    ("features.codeCloze", "mode.limitedOffline", "mode.availableWithLlm"),
    ("features.crossLectureReasoning", "mode.limitedOffline", "mode.availableWithLlm"),
    ("features.privacy", "mode.fullyLocal", "mode.dependsOnProvider"),
]


I18N_DEFAULTS = {
    "mode.generationMode": "Generation Mode",
    "mode.offline": "Offline Mode",
    "mode.onlineLlm": "Online LLM Mode",
    "mode.offlineDescription": "This site was generated without LLM calls. It organizes your source materials into a searchable lecture explorer.",
    "mode.onlineDescription": "This site was generated with an online LLM. Chinese summaries, enriched glossary entries, and advanced practice questions may use the configured model provider.",
    "mode.availableOffline": "Available offline",
    "mode.requiresLlm": "Requires Online LLM",
    "mode.limitedOffline": "Limited offline",
    "mode.availableWithLlm": "Available with LLM",
    "mode.featureMatrix": "Feature Availability Matrix",
    "mode.currentGenerationMode": "Current generation mode",
    "mode.privacyNote": "Offline Mode keeps files local. Online LLM Mode may send selected source text to the configured provider.",
    "mode.fullyLocal": "Fully local",
    "mode.dependsOnProvider": "Depends on provider",
    "mode.feature": "Feature",
    "mode.cardSourceExplorer": "Searchable Source Explorer",
    "mode.cardSourceExplorerDesc": "Browse cleaned source excerpts with source references.",
    "mode.cardSlideGalleryDesc": "View extracted diagrams, formulas, tables, and slide figures.",
    "mode.cardChineseSummary": "Structured Chinese notes generated from source text and references.",
    "mode.cardChineseSummaryRequiresDesc": "Enable Online LLM Mode to generate Chinese structured notes.",
    "mode.cardAdvancedPractice": "Advanced Practice",
    "mode.cardAdvancedPracticeDesc": "Creative extensions, application scenarios, and harder synthesis questions can use the configured model.",
    "mode.sourceExplorer": "Source Explorer",
    "mode.sourceGroundedNotes": "Source-grounded Notes",
    "mode.sourceExplorerNote": "Offline Mode shows cleaned excerpts and slide figures instead of AI-written summaries.",
    "mode.sourceGroundedNote": "Generated with LLM using uploaded source materials and source references.",
    "mode.llmDisabledFallback": "LLM disabled: showing cleaned source excerpts instead of generated Chinese summaries.",
    "mode.practiceOfflineNote": "Template-based practice is available offline. Creative Extension, hard application scenarios, advanced code cloze, and cross-lecture synthesis require Online LLM Mode.",
    "mode.practiceOnlineNote": "Online LLM Mode: source-grounded and creative practice can use the configured model.",
    "features.pdfReading": "PDF / MD / DOCX reading",
    "features.versionedOutput": "Versioned output site",
    "features.sourceRefs": "Source references",
    "features.cleanedExcerpts": "Cleaned source excerpts",
    "features.searchIndex": "Search index",
    "features.slideFigures": "Slide figures",
    "features.slideGallery": "Slide Figure Gallery",
    "features.lectureMap": "Lecture Map",
    "features.crossLectureReferences": "Cross-Lecture References",
    "features.basicGlossary": "Basic glossary",
    "features.enrichedGlossary": "Enriched glossary",
    "features.templatePractice": "Template practice",
    "features.chineseSummaries": "Chinese structured summaries",
    "features.creativePractice": "Creative Extension Practice",
    "features.applicationScenarios": "Application scenario questions",
    "features.codeCloze": "Code cloze generation",
    "features.crossLectureReasoning": "Cross-lecture reasoning",
    "features.privacy": "Privacy",
    "sources.title": "Sources",
    "sources.count": "sources",
    "sources.expandHint": "Click to view source references",
    "sources.generatedFrom": "Generated from",
    "sources.page": "Page",
}


def extract_terms(text: str, limit: int = 14) -> list[str]:
    lower = text.lower()
    terms: list[str] = []
    for term in COMMON_TERMS:
        if term.lower() in lower and term not in terms:
            terms.append(term)
    return terms[:limit]


def clean_extracted_text(text: str) -> str:
    text = text.replace("\x00", " ")
    lines = [normalize_ws(line) for line in text.splitlines()]
    cleaned: list[str] = []
    seen: Counter[str] = Counter()
    for line in lines:
        if not line:
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if re.fullmatch(r"page\s+\d+", line, flags=re.I):
            continue
        if len(line) < 4 and not re.search(r"[A-Za-z]", line):
            continue
        seen[line] += 1
        if seen[line] > 2 and len(line) < 80:
            continue
        cleaned.append(line)
    return normalize_ws(" ".join(cleaned))


def sentence_split(text: str) -> list[str]:
    clean = clean_extracted_text(text)
    parts = re.split(r"(?<=[.!?。！？])\s+|(?<=；)\s*", clean)
    return [part.strip() for part in parts if len(part.strip()) > 18]


def excerpt_sentence_split(text: str) -> list[str]:
    clean = clean_extracted_text(strip_course_metadata(text))
    clean = re.sub(r"[•●▪■]+", " ", clean)
    clean = re.sub(r"\s*[-–—]{2,}\s*", " ", clean)
    clean = normalize_ws(clean)
    parts = re.split(r"(?<=[.!?。！？])\s+|(?<=[;；])\s+", clean)
    return [normalize_ws(part.strip(" -–—:;")) for part in parts if len(normalize_ws(part)) > 24]


def sentence_quality_score(sentence: str, key_terms: list[str] | None = None) -> int:
    clean = normalize_ws(sentence)
    lower = clean.lower()
    words = count_ascii_words(clean)
    score = 0
    if 8 <= words <= 45:
        score += 4
    elif 46 <= words <= 80:
        score += 2
    if any(term.lower() in lower for term in (key_terms or [])):
        score += 5
    if any(keyword in lower for keyword in QUOTE_KEYWORDS):
        score += 3
    if re.search(r"\b(is|are|means|refers to|used to|used for|can|helps|contains|includes|called|defined)\b", lower):
        score += 3
    if detect_english_leakage(clean).get("metadataHits"):
        score -= 8
    if words < 6 or words > 90:
        score -= 4
    if re.fullmatch(r"[A-Za-z0-9 ,:;()/.+-]+", clean) and words < 5:
        score -= 4
    return score


def build_clean_source_excerpt(
    raw_text: str,
    lecture_title: str | None = None,
    max_sentences: int = 2,
    max_words: int = 80,
    key_terms: list[str] | None = None,
) -> str:
    cleaned = strip_course_metadata(raw_text or "", lecture_title or "")
    cleaned = re.sub(r"[^\w\s.,;:!?()/%+\-=<>α-ωΑ-Ω\u4e00-\u9fff]", " ", cleaned)
    sentences = []
    seen: set[str] = set()
    for sentence in excerpt_sentence_split(cleaned):
        sentence = strip_course_metadata(sentence, lecture_title or "")
        if not sentence or sentence.lower() in seen:
            continue
        seen.add(sentence.lower())
        if contains_course_metadata(sentence):
            continue
        if looks_like_raw_english_dump(sentence) and count_ascii_words(sentence) > 80:
            continue
        if sentence_quality_score(sentence, key_terms) < 3:
            continue
        sentences.append(sentence)
    if not sentences:
        return ""
    selected = sorted(sentences, key=lambda item: sentence_quality_score(item, key_terms), reverse=True)[:max_sentences]
    words: list[str] = []
    output: list[str] = []
    for sentence in selected:
        sentence_words = re.findall(r"\S+", sentence)
        if len(words) + len(sentence_words) > max_words:
            remaining = max_words - len(words)
            if remaining >= 8:
                output.append(" ".join(sentence_words[:remaining]).rstrip(".,;:") + "...")
            break
        output.append(sentence)
        words.extend(sentence_words)
    return normalize_ws(" ".join(output))


def compact_summary(text: str, max_sentences: int = 3, max_chars: int = 700) -> str:
    sentences = sentence_split(text)
    if not sentences:
        return "该页没有提取到足够可读文本，需要结合原始 slide image 人工检查。"
    return " ".join(sentences[:max_sentences])[:max_chars]


QUOTE_KEYWORDS = [
    "attention",
    "transformer",
    "language model",
    "perplexity",
    "embedding",
    "rnn",
    "lstm",
    "gru",
    "bert",
    "gpt",
    "t5",
    "asr",
    "tf-idf",
    "cosine",
    "workflow",
    "raw data",
    "curated data",
    "loss",
    "gradient",
    "pretraining",
    "fine-tuning",
    "text-to-text",
]


def trim_source_quote(text: str, max_words: int = 28) -> str:
    text = normalize_ws(text).strip(" -:\t")
    words = re.findall(r"\S+", text)
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(".,;:") + "..."


def normalized_quote_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def compact_source_ref(source_ref: str) -> str:
    ref = normalize_ws(source_ref)
    match = re.search(r"\bLecture\s+0*(\d+)\b.*?,\s*(p\.\d+)", ref, flags=re.I)
    if match:
        return f"Lecture {int(match.group(1))}, {match.group(2)}"
    return strip_course_metadata(ref)


def score_source_quote(quote: str, section_context: str) -> int:
    clean = normalize_ws(quote)
    lower = clean.lower()
    words = count_ascii_words(clean)
    score = 0
    if 3 <= words <= 18:
        score += 4
    elif 19 <= words <= 28:
        score += 2
    if re.search(r"[=→↔≤≥∑∏λθαβ]|\bP\(|\\frac|->", clean):
        score += 6
    if any(keyword in lower for keyword in QUOTE_KEYWORDS):
        score += 5
    if re.search(r"\b(is|are|means|defined as|called|refers to)\b", lower):
        score += 3
    if re.search(r"raw data|curated data|algorithm|results|encoder|decoder|masked|prediction", lower):
        score += 3
    if clean and clean == clean.title():
        score += 2
    context_title = normalized_quote_key(section_context)[:140]
    if normalized_quote_key(clean) and normalized_quote_key(clean) in context_title:
        score += 1
    return score


def is_low_information_quote(text: str, lecture_title: str = "") -> bool:
    clean = normalize_ws(text).strip(" -:\t")
    lower = clean.lower()
    if not clean or len(clean) < 8:
        return True
    if re.fullmatch(r"\d+|page\s+\d+", clean, flags=re.I):
        return True
    if any(item in lower for item in ["copyright", "wayne snyder", "boston university", "natural language processing"]):
        return True
    if lower in {"introduction", "introduction to", "overview", "summary", "questions", "references"}:
        return True
    if lecture_title and normalized_quote_key(clean) == normalized_quote_key(lecture_title):
        return True
    return False


def short_original_quote(text: str, lecture_title: str = "") -> str:
    lines = [normalize_ws(line) for line in text.splitlines() if normalize_ws(line)]
    candidates = []
    for line in lines[:12]:
        if is_low_information_quote(line, lecture_title):
            continue
        if len(line) > 180:
            continue
        if not re.search(r"[A-Za-z]", line):
            continue
        candidates.append(trim_source_quote(line))
    if not candidates:
        return ""
    return max(candidates, key=lambda item: score_source_quote(item, text))


def deduplicate_quotes(quotes: list[tuple[SourceSection, str, int]], report: dict[str, int]) -> list[tuple[SourceSection, str, int]]:
    kept: list[tuple[SourceSection, str, int]] = []
    seen: set[str] = set()
    for section, quote, score in quotes:
        key = normalized_quote_key(quote)
        short_key = " ".join(key.split()[:12])
        if not key or short_key in seen:
            report["duplicateQuotesRemoved"] += 1
            continue
        seen.add(short_key)
        kept.append((section, quote, score))
    return kept


def select_source_quotes_for_lecture(
    sections: list[SourceSection],
    lecture_title: str,
    report: dict[str, int],
    *,
    max_quotes_per_lecture: int = 8,
) -> dict[str, str]:
    candidates: list[tuple[SourceSection, str, int]] = []
    for section in sections:
        quote = short_original_quote(section.text, lecture_title)
        if not quote:
            report["lowInformationQuotesRemoved"] += 1
            continue
        report["rawQuotesCollected"] += 1
        if count_ascii_words(quote) > 35:
            report["longQuotesRemoved"] += 1
            continue
        score = score_source_quote(quote, section.text)
        if score < 5:
            report["lowInformationQuotesRemoved"] += 1
            continue
        candidates.append((section, trim_source_quote(quote), score))
    candidates = deduplicate_quotes(candidates, report)
    report["quotesAfterFiltering"] += len(candidates)
    selected = sorted(candidates, key=lambda item: (-item[2], item[0].page_number or 9999))[:max_quotes_per_lecture]
    return {section.id: quote for section, quote, _score in selected}


def build_source_quote_html(section: SourceSection, quote: str | None) -> str:
    if not quote:
        return ""
    return (
        '<blockquote class="source-quote">'
        '<span class="quote-label">Original source wording</span> '
        f'{html.escape(quote)} '
        f'<span class="page-ref">{html.escape(compact_source_ref(section.source_ref))}</span>'
        '</blockquote>'
    )


def normalize_section_title(title: str, lecture_title: str | None = None) -> str:
    clean = strip_course_metadata(normalize_ws(title), lecture_title or "")
    if not clean:
        return ""
    lower = clean.lower()
    title_map = [
        ("mixture of experts", "Mixture of Experts (MoE)"),
        ("gpt-3", "GPT-3 与模型规模"),
        ("gpt-2", "GPT-2 与训练语料"),
        ("gpt", "GPT-style Generation"),
        ("t5", "T5 Text-to-Text Framework"),
        ("bert", "BERT Pretraining"),
        ("audio", "Audio Processing Pipeline"),
        ("speech", "Speech Processing"),
        ("asr", "ASR Pipeline"),
        ("attention", "Attention Mechanism"),
        ("transformer", "Transformer Architecture"),
        ("language model", "Language Model Objective"),
        ("perplexity", "Language Model Evaluation"),
        ("workflow", "Machine Learning Workflow"),
        ("embedding", "Embedding Representation"),
        ("tf-idf", "TF-IDF Weighting"),
        ("cosine", "Cosine Similarity"),
        ("rnn", "RNN Sequence Modeling"),
    ]
    word_count = count_ascii_words(clean)
    looks_sentence = bool(re.search(r"\b(is|are|was|were|used|called|contains|includes|introduced)\b", lower))
    if word_count > 10 or looks_sentence or detect_english_leakage(clean)["metadataHits"]:
        for key, value in title_map:
            if key in lower:
                return value
        return ""
    return clean[:90]


def semantic_title(section: SourceSection, index: int) -> str:
    title = normalize_ws(section.title)
    title = normalize_section_title(title, section.metadata.get("lecture_title") or "")
    bad_title = (
        not title
        or re.fullmatch(r"page\s+\d+", title, flags=re.I)
        or re.fullmatch(r"wayne\s+snyder", title, flags=re.I)
        or re.fullmatch(r"boston\s+university", title, flags=re.I)
        or re.fullmatch(r"cs\s+\d+.*", title, flags=re.I)
        or title.lower() in {"tree", "introduction to"}
        or len(title) < 8
    )
    if not bad_title:
        return title[:90]
    lower = section.text.lower()
    mapping = [
        ("cosine", "Cosine Similarity"),
        ("tf-idf", "TF-IDF Weighting"),
        ("bag", "Bag-of-Words Representation"),
        ("embedding", "Embedding Representation"),
        ("workflow", "Machine Learning Workflow"),
        ("supervised", "Supervised Learning Setup"),
        ("classification", "Classification Objective"),
        ("gradient", "Optimization with Gradient Descent"),
        ("rnn", "RNN Sequence Modeling"),
        ("attention", "Attention Mechanism"),
        ("transformer", "Transformer Architecture"),
        ("bert", "BERT Contextual Pretraining"),
        ("gpt", "GPT-style Generation"),
        ("asr", "ASR Pipeline"),
    ]
    for key, value in mapping:
        if key in lower:
            return value
    return SECTION_FALLBACKS[index % len(SECTION_FALLBACKS)]


def context_for_term(term: str, units: list[LectureUnit], current_unit: LectureUnit) -> tuple[str, str, bool]:
    term_re = re.compile(re.escape(term), flags=re.I)
    for unit in [current_unit, *[item for item in units if item is not current_unit]]:
        for section in unit.pages_or_sections:
            text = clean_extracted_text(section.text)
            match = term_re.search(text)
            if not match:
                continue
            start = max(0, match.start() - 260)
            end = min(len(text), match.end() + 360)
            context = text[start:end].strip()
            if len(context) > 90:
                return context, section.source_ref, unit is current_unit
    return "", "", False


def find_term_contexts(
    term: str,
    all_units: list[LectureUnit],
    current_unit: LectureUnit | None = None,
    max_contexts: int = 5,
) -> list[tuple[str, str, bool]]:
    ordered = []
    if current_unit is not None:
        ordered.append(current_unit)
    ordered.extend(unit for unit in all_units if unit is not current_unit)
    contexts: list[tuple[str, str, bool]] = []
    term_re = re.compile(re.escape(term), flags=re.I)
    for unit in ordered:
        for section in unit.pages_or_sections:
            text = clean_extracted_text(section.text)
            match = term_re.search(text)
            if not match:
                continue
            start = max(0, match.start() - 220)
            end = min(len(text), match.end() + 320)
            contexts.append((text[start:end].strip(), section.source_ref, unit is current_unit))
            if len(contexts) >= max_contexts:
                return contexts
    return contexts


def explain_term(term: str, units: list[LectureUnit], current_unit: LectureUnit) -> dict[str, str]:
    context, ref, same_lecture = context_for_term(term, units, current_unit)
    base = FALLBACK_TERM_EXPLANATIONS.get(
        term,
        f"{term} 是当前 NLP/ML 学习材料中的关键术语，需要结合上下文理解其输入、输出和使用场景。",
    )
    if context:
        role = (
            f"在当前 lecture 中，它出现在与 {semantic_context_label(context)} 相关的讨论中。"
            if same_lecture
            else f"当前 lecture 没有给出完整定义；在其他上传材料中，它出现在与 {semantic_context_label(context)} 相关的上下文里。"
        )
        explanation = f"{base} {role}"
        source_type = "source-context"
    else:
        explanation = f"{base} 这是 fallback explanation：当前上传材料没有提供足够完整的定义，因此使用本地术语词典补充。"
        ref = "fallback explanation"
        source_type = "fallback"
    return {"term": term, "explanation": explanation, "source_ref": ref, "source_type": source_type}


PLACEHOLDER_GLOSSARY_PATTERNS = [
    "从源材料中提取的关键词",
    "重要术语",
    "关键词",
    "No explanation available",
]


def validate_glossary_entry(entry: dict[str, str]) -> bool:
    explanation = normalize_ws(entry.get("explanation", ""))
    if not explanation:
        return False
    if any(pattern.lower() in explanation.lower() for pattern in PLACEHOLDER_GLOSSARY_PATTERNS):
        return False
    if count_chinese_chars(explanation) < 20:
        return False
    if not (entry.get("source_ref") or entry.get("source_type") in {"fallback", "ai"}):
        return False
    return True


def build_fallback_glossary_explanation(term: str, contexts: list[tuple[str, str, bool]]) -> dict[str, str]:
    base = FALLBACK_TERM_EXPLANATIONS.get(
        term,
        f"{term} 是当前 NLP/ML 课程中的关键术语，需要结合上下文理解它对应的输入表示、模型机制、训练目标或评估作用。",
    )
    if contexts:
        _context, ref, same_lecture = contexts[0]
        role = "当前 lecture" if same_lecture else "其他上传 lecture"
        return {
            "term": term,
            "explanation": f"{base} 在{role}中，它用于连接课件中的具体例子和模型流程，复习时应关注它解决的问题、适用场景和局限。",
            "source_ref": ref,
            "source_type": "source-context",
        }
    return {
        "term": term,
        "explanation": f"{base} 这是本地 fallback 补充解释，不是原始资料的直接引文。",
        "source_ref": "fallback explanation",
        "source_type": "fallback",
    }


def enrich_glossary_entry(
    entry: dict[str, str],
    lecture_unit: LectureUnit,
    all_units: list[LectureUnit],
    llm_client: object | None = None,
) -> dict[str, str]:
    if validate_glossary_entry(entry):
        return entry
    term = entry.get("term", "")
    contexts = find_term_contexts(term, all_units, lecture_unit)
    enriched = build_fallback_glossary_explanation(term, contexts)
    if validate_glossary_entry(enriched):
        return enriched
    return {
        "term": term,
        "explanation": f"{term} 是本讲相关术语。当前资料中定义信息不足，因此使用本地 fallback 提供保守中文解释；复习时请结合 Sources 中的页码核对上下文。",
        "source_ref": enriched.get("source_ref", "fallback explanation"),
        "source_type": "fallback",
    }


def semantic_context_label(context: str) -> str:
    lower = context.lower()
    labels = [
        ("evaluation", "evaluation / 评估"),
        ("similarity", "similarity / 相似度"),
        ("vector", "vector representation / 向量表示"),
        ("classification", "classification / 分类"),
        ("translation", "machine translation / 机器翻译"),
        ("attention", "attention mechanism / 注意力机制"),
        ("sequence", "sequence modeling / 序列建模"),
        ("speech", "speech processing / 语音处理"),
        ("probability", "probabilistic modeling / 概率建模"),
    ]
    for key, label in labels:
        if key in lower:
            return label
    return "核心概念解释"


def render_terms(text: str, glossary: dict[str, dict[str, str]] | None = None) -> str:
    terms = sorted(extract_terms(text), key=len, reverse=True)
    if not terms:
        return html.escape(text)
    pattern = re.compile(r"\b(" + "|".join(re.escape(term) for term in terms) + r")\b", flags=re.I)
    pieces: list[str] = []
    last = 0
    for match in pattern.finditer(text):
        pieces.append(html.escape(text[last:match.start()]))
        matched = match.group(0)
        canonical = next((term for term in terms if term.lower() == matched.lower()), matched)
        explanation = glossary.get(canonical, {}).get("explanation") if glossary else FALLBACK_TERM_EXPLANATIONS.get(canonical)
        tooltip = html.escape(explanation or FALLBACK_TERM_EXPLANATIONS.get(canonical, canonical), quote=True)
        pieces.append(f'<span class="term" tabindex="0" data-tooltip="{tooltip}">{html.escape(matched)}</span>')
        last = match.end()
    pieces.append(html.escape(text[last:]))
    return "".join(pieces)


def build_glossary_terms(unit: LectureUnit, all_units: list[LectureUnit]) -> dict[str, dict[str, str]]:
    terms = extract_terms(unit.full_text, limit=16)
    # Ensure each lecture has enough useful core terms when the text is sparse.
    for fallback in ["language model", "BOW", "TF-IDF", "cosine similarity", "word embedding", "attention", "Transformer", "BERT"]:
        if fallback.lower() in unit.full_text.lower() and fallback not in terms:
            terms.append(fallback)
    glossary = {}
    for term in terms[:16]:
        glossary[term] = enrich_glossary_entry(explain_term(term, all_units, unit), unit, all_units)
    return glossary


def build_search_index(units: list[LectureUnit]) -> list[dict[str, Any]]:
    records = []
    for unit in units:
        for section in unit.pages_or_sections:
            text = clean_extracted_text(section.text)
            if not text:
                continue
            records.append(
                {
                    "id": section.id,
                    "lectureId": unit.lecture_id,
                    "lectureTitle": unit.lecture_title,
                    "sourceFile": unit.source_file,
                    "sourceType": unit.source_type,
                    "sectionTitle": semantic_title(section, section.page_number or 0),
                    "text": text,
                    "snippet": text[:260],
                    "pageRefs": [section.source_ref],
                    "sourceRefs": [section.source_ref],
                    "terms": extract_terms(text),
                }
            )
    return records


def i18n_text(key: str) -> str:
    return I18N_DEFAULTS.get(key, key)


def i18n_span(key: str, *, cls: str | None = None) -> str:
    cls_attr = f' class="{html.escape(cls)}"' if cls else ""
    return f'<span{cls_attr} data-site-i18n="{html.escape(key)}">{html.escape(i18n_text(key))}</span>'


def capability_badge(label_key: str) -> str:
    if label_key == "mode.requiresLlm":
        cls = "feature-badge-llm"
    elif label_key in {"mode.limitedOffline", "mode.dependsOnProvider"}:
        cls = "feature-badge-limited"
    else:
        cls = "feature-badge-offline"
    return i18n_span(label_key, cls=cls)


def render_feature_matrix(generation_mode: str) -> str:
    rows = []
    for feature_key, offline_key, online_key in FEATURE_MATRIX:
        rows.append(
            "<tr>"
            f"<th>{i18n_span(feature_key)}</th>"
            f"<td>{capability_badge(offline_key)}</td>"
            f"<td>{capability_badge(online_key)}</td>"
            "</tr>"
        )
    mode_key = "mode.onlineLlm" if generation_mode == "online_llm" else "mode.offline"
    return f"""
<section class="feature-matrix-section" id="feature-matrix">
  <h2 data-site-i18n="mode.featureMatrix">{html.escape(i18n_text("mode.featureMatrix"))}</h2>
  <p class="mode-note"><span data-site-i18n="mode.currentGenerationMode">{html.escape(i18n_text("mode.currentGenerationMode"))}</span>: <strong data-site-i18n="{html.escape(mode_key)}">{html.escape(display_generation_mode(generation_mode))}</strong></p>
  <div class="table-wrap"><table class="feature-matrix"><thead><tr><th data-site-i18n="mode.feature">{html.escape(i18n_text("mode.feature"))}</th><th data-site-i18n="mode.offline">{html.escape(i18n_text("mode.offline"))}</th><th data-site-i18n="mode.onlineLlm">{html.escape(i18n_text("mode.onlineLlm"))}</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
</section>
"""


def display_generation_mode(generation_mode: str) -> str:
    return "Online LLM Mode" if generation_mode == "online_llm" else "Offline Mode"


def render_mode_capability_banner(metadata: dict[str, Any], generation_mode: str) -> str:
    telemetry = metadata.get("llmTelemetry") or {}
    if generation_mode == "online_llm":
        detail_key = "mode.onlineDescription"
        mode_cards = [
            ("mode.availableWithLlm", "features.chineseSummaries", "mode.cardChineseSummary", "available"),
            ("mode.availableOffline", "mode.cardSourceExplorer", "mode.cardSourceExplorerDesc", "available"),
            ("mode.availableWithLlm", "mode.cardAdvancedPractice", "mode.cardAdvancedPracticeDesc", "available"),
        ]
        llm_meta = (
            f'<p class="mode-note">Provider: {html.escape(str(telemetry.get("diagnostics", {}).get("provider") or metadata.get("llmProvider") or "configured provider"))} | '
            f'Model: {html.escape(str(metadata.get("llmModel") or telemetry.get("diagnostics", {}).get("modelConfigured") or "configured model"))} | '
            f'Calls: {int(telemetry.get("llmCallsAttempted") or 0)} attempted / {int(telemetry.get("llmCallsSucceeded") or 0)} succeeded / {int(telemetry.get("llmCallsFailed") or 0)} failed | '
            f'Parse: {int(telemetry.get("llmParseSucceeded") or metadata.get("llmParseSucceeded") or 0)} succeeded | '
            f'Repair: {int(telemetry.get("llmRepairAttempted") or metadata.get("llmRepairAttempted") or 0)} attempted / {int(telemetry.get("llmRepairSucceeded") or metadata.get("llmRepairSucceeded") or 0)} succeeded</p>'
        )
    else:
        detail_key = "mode.offlineDescription"
        mode_cards = [
            ("mode.availableOffline", "mode.cardSourceExplorer", "mode.cardSourceExplorerDesc", "available"),
            ("mode.availableOffline", "features.slideGallery", "mode.cardSlideGalleryDesc", "available"),
            ("mode.requiresLlm", "features.chineseSummaries", "mode.cardChineseSummaryRequiresDesc", "requires-llm"),
        ]
        llm_meta = f'<p class="mode-note" data-site-i18n="mode.privacyNote">{html.escape(i18n_text("mode.privacyNote"))}</p>'
    cards = "".join(
        f"""
<div class="capability-card {cls}">
  {i18n_span(status, cls="capability-status")}
  <h3 data-site-i18n="{html.escape(title)}">{html.escape(i18n_text(title))}</h3>
  <p data-site-i18n="{html.escape(text)}">{html.escape(i18n_text(text))}</p>
</div>
"""
        for status, title, text, cls in mode_cards
    )
    mode_key = "mode.onlineLlm" if generation_mode == "online_llm" else "mode.offline"
    return f"""
<div class="mode-capability-banner">
  <h2><span data-site-i18n="mode.generationMode">{html.escape(i18n_text("mode.generationMode"))}</span>: <span data-site-i18n="{html.escape(mode_key)}">{html.escape(display_generation_mode(generation_mode))}</span></h2>
  <p data-site-i18n="{html.escape(detail_key)}">{html.escape(i18n_text(detail_key))}</p>
  {llm_meta}
  <div class="capability-grid">{cards}</div>
</div>
"""

def lecture_map_items(unit: LectureUnit, limit: int = 14) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    seen: set[str] = set()
    for index, section in enumerate(unit.pages_or_sections):
        title = semantic_title(section, index)
        if not title or title.lower() in seen or contains_course_metadata(title):
            continue
        seen.add(title.lower())
        items.append((section.id, title))
        if len(items) >= limit:
            break
    return items


def render_lecture_map(unit: LectureUnit) -> str:
    items = lecture_map_items(unit)
    if not items:
        return ""
    rows = "".join(f'<li><a href="#{html.escape(section_id)}">{html.escape(title)}</a></li>' for section_id, title in items)
    return f"""
<section class="lecture-map" id="{html.escape(unit.lecture_id)}-map">
  <h2>Lecture Map</h2>
  <p class="mode-note">Available offline · inferred from slide titles and page structure.</p>
  <ol>{rows}</ol>
</section>
"""


def lecture_terms(unit: LectureUnit) -> set[str]:
    terms = set(extract_terms(unit.full_text, limit=18))
    for section in unit.pages_or_sections[:12]:
        title = semantic_title(section, section.page_number or 0)
        for term in extract_terms(f"{title} {section.text}", limit=8):
            terms.add(term)
    return terms


def related_lectures(units: list[LectureUnit], current: LectureUnit, limit: int = 4) -> list[dict[str, Any]]:
    current_terms = lecture_terms(current)
    current_number = int(re.search(r"\d+", current.lecture_id).group(0)) if re.search(r"\d+", current.lecture_id) else 0
    related = []
    for unit in units:
        if unit is current:
            continue
        terms = lecture_terms(unit)
        shared = sorted(current_terms & terms)
        other_number = int(re.search(r"\d+", unit.lecture_id).group(0)) if re.search(r"\d+", unit.lecture_id) else 0
        sequential = abs(other_number - current_number) == 1 if current_number and other_number else False
        score = len(shared) * 3 + (2 if sequential else 0)
        if score <= 0:
            continue
        relation = "shared terms / sequential order" if sequential else "shared terminology"
        related.append({"unit": unit, "shared": shared[:7], "relation": relation, "score": score})
    return sorted(related, key=lambda item: (-item["score"], item["unit"].lecture_id))[:limit]


def render_cross_lecture_references(unit: LectureUnit, all_units: list[LectureUnit], generation_mode: str) -> str:
    related = related_lectures(all_units, unit)
    if not related:
        return ""
    cards = []
    for item in related:
        target = item["unit"]
        llm_note = ""
        if generation_mode == "online_llm":
            llm_note = '<p><span class="feature-badge-llm">LLM-generated relation explanation</span> Available when relation explanations are generated.</p>'
        cards.append(
            f"""
<div class="related-lecture-card">
  <h3>{html.escape(target.lecture_title)}</h3>
  <p>Shared terms: {html.escape(", ".join(item["shared"]) or "adjacent lecture structure")}</p>
  <p>Relation type: {html.escape(item["relation"])}</p>
  {llm_note}
  <a href="#{html.escape(target.lecture_id)}">Open lecture</a>
</div>
"""
        )
    return f"""
<section class="cross-lecture-references" id="{html.escape(unit.lecture_id)}-related">
  <h2>Related Lectures</h2>
  <p class="mode-note">Available offline · based on shared terms and source structure.</p>
  <div class="related-lecture-grid">{''.join(cards)}</div>
</section>
"""


def classify_slide(section: SourceSection) -> str:
    text = section.text or ""
    lower = text.lower()
    if re.search(r"=|Σ|∑|log|P\(|softmax|argmax|\\frac|θ|α|β", text):
        return "formula"
    if any(term in lower for term in ["architecture", "layer", "encoder", "decoder", "transformer", "rnn", "cnn", "model"]):
        return "architecture"
    if any(term in lower for term in ["table", "matrix", "column", "row"]):
        return "table"
    if any(term in lower for term in ["example", "e.g.", "input", "output", "sample"]):
        return "example"
    if int(section.metadata.get("visual_score", 0)) >= 6:
        return "diagram"
    return "slide"


def render_slide_gallery(units: list[LectureUnit]) -> str:
    cards = []
    for unit in units:
        rendered = unit.metadata.get("slide_images") or {}
        by_page = {section.page_number: section for section in unit.pages_or_sections}
        for page_number, rel in sorted(rendered.items()):
            section = by_page.get(page_number)
            if not section:
                continue
            slide_type = classify_slide(section)
            ref = compact_source_ref(section.source_ref)
            cards.append(
                f"""
<article class="gallery-card" data-gallery-type="{html.escape(slide_type)}">
  <img src="{html.escape(rel)}" alt="Slide thumbnail from {html.escape(ref)}">
  <div>
    <span class="feature-badge-offline">{html.escape(slide_type)}</span>
    <h3>{html.escape(unit.lecture_title)}</h3>
    <p><span class="page-ref">{html.escape(ref)}</span></p>
    <a href="#{html.escape(section.id)}">Open in notes</a>
  </div>
</article>
"""
            )
    if not cards:
        return ""
    return f"""
<section id="slide-gallery" class="slide-gallery lecture-section">
  <div class="lecture-heading"><div><div class="eyebrow">Offline</div><h1>Slide Figure Gallery</h1></div><span class="quality">{len(cards)} figures</span></div>
  <p class="mode-note">Available offline · extracted directly from PDF pages.</p>
  <div class="gallery-filters">
    <button data-filter="all" type="button">All</button>
    <button data-filter="diagram" type="button">Diagrams</button>
    <button data-filter="formula" type="button">Formulas</button>
    <button data-filter="table" type="button">Tables</button>
    <button data-filter="architecture" type="button">Architectures</button>
  </div>
  <div class="gallery-grid">{''.join(cards)}</div>
</section>
"""


def select_visual_pages(unit: LectureUnit, max_pages: int = 4) -> list[int]:
    if unit.source_type != "pdf":
        return []
    scored: list[tuple[int, int]] = []
    for section in unit.pages_or_sections:
        if not section.page_number:
            continue
        score = int(section.metadata.get("visual_score", 0))
        if section.page_number == 1:
            score += 1
        if score > 0:
            scored.append((score, section.page_number))
    if not scored:
        return [1] if unit.pages_or_sections else []
    pages = [page for _, page in sorted(scored, key=lambda item: (-item[0], item[1]))[:max_pages]]
    return sorted(set(pages))


def render_pdf_slide_images(unit: LectureUnit, output_path: Path, max_pages: int = 4) -> None:
    if unit.source_type != "pdf":
        return
    source_path = unit.metadata.get("source_path")
    if not source_path or not Path(source_path).exists():
        return
    pages = select_visual_pages(unit, max_pages=max_pages)
    if not pages:
        return
    try:
        import fitz
    except ImportError:
        return
    assets_dir = output_path / "assets" / "slides"
    assets_dir.mkdir(parents=True, exist_ok=True)
    rendered: dict[int, str] = {}
    document = fitz.open(source_path)
    try:
        for page_number in pages:
            if page_number < 1 or page_number > len(document):
                continue
            page = document[page_number - 1]
            pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
            filename = f"{unit.lecture_id}-page-{page_number:03d}.png"
            pix.save(assets_dir / filename)
            rendered[page_number] = f"assets/slides/{filename}"
    finally:
        document.close()
    unit.metadata["slide_images"] = rendered


def build_slide_figure_html(unit: LectureUnit, page_number: int, source_ref: str) -> str:
    rel = (unit.metadata.get("slide_images") or {}).get(page_number)
    if not rel:
        return ""
    ref = html.escape(compact_source_ref(source_ref))
    return f"""
<figure class="slide-figure" data-page="{page_number}">
  <img src="{html.escape(rel)}" alt="Original slide from {ref}">
  <figcaption>Original slide: <span class="page-ref">{ref}</span></figcaption>
</figure>
"""


def safe_source_note_html(
    text: str,
    glossary: dict[str, dict[str, str]],
    report: dict[str, int],
    source_refs: list[str],
    *,
    raw_text: str | None = None,
    terms: list[str] | None = None,
    llm_client: object | None = None,
    lecture_title: str | None = None,
) -> str:
    candidate = strip_course_metadata(normalize_ws(text), lecture_title or "")
    if is_low_quality_chinese_fallback(candidate):
        report["lowQualityChineseFallbackBlocked"] += 1
        return ""
    leakage = detect_english_leakage(candidate)
    if leakage.get("metadataHits"):
        report["metadataLeakageDetected"] += len(leakage.get("metadataHits") or [])
    if leakage.get("longEnglishRuns"):
        report["longEnglishRunsDetected"] += len(leakage.get("longEnglishRuns") or [])
    if leakage.get("hasLeakage"):
        report["englishLeakageParagraphsDetected"] += 1
    if looks_like_raw_english_dump(candidate) or leakage.get("hasLeakage"):
        report["suspiciousRawEnglishParagraphsDetected"] += 1
        rewritten = rewrite_mixed_paragraph_to_chinese(
            candidate,
            source_refs=source_refs,
            llm_client=llm_client,
            key_terms=terms,
            lecture_title=lecture_title,
        )
        fallback_note = build_heuristic_chinese_note(candidate, [], terms)
        if llm_client is not None and rewritten != fallback_note:
            report["rewrittenWithLLM"] += 1
        else:
            report["rewrittenWithFallback"] += 1
        candidate = rewritten
    final_leakage = detect_english_leakage(candidate)
    if looks_like_raw_english_dump(candidate) or final_leakage.get("hasLeakage") or is_low_quality_chinese_fallback(candidate):
        report["blockedRawEnglishParagraphs"] += 1
        return ""
    return render_terms(candidate, glossary)


def build_source_note_payload(section: SourceSection, lecture_title: str, has_slide_figure: bool = False) -> dict[str, Any]:
    title = semantic_title(section, section.page_number or 0)
    terms = extract_terms(section.text, limit=5)
    excerpt = build_clean_source_excerpt(section.text, lecture_title, key_terms=terms)
    state = "fallback_cleaned_excerpt" if excerpt else ("visual_only" if has_slide_figure else "empty")
    return {
        "title": title,
        "summary_zh": "",
        "source_excerpt": excerpt,
        "state": state,
        "source_refs": [section.source_ref],
        "key_terms": terms,
        "source_quotes": [],
    }


def build_source_paragraph(section: SourceSection, glossary: dict[str, dict[str, str]], report: dict[str, int], lecture_title: str, has_slide_figure: bool = False) -> str:
    note = build_source_note_payload(section, lecture_title, has_slide_figure)
    if looks_like_raw_english_dump(section.text):
        report["suspiciousRawEnglishSourceInputsDetected"] += 1
    if note["state"] != "summary_zh":
        return ""
    return safe_source_note_html(
        note["summary_zh"],
        glossary,
        report,
        note["source_refs"],
        raw_text=None,
        terms=note["key_terms"],
        lecture_title=lecture_title,
    )


def render_llm_structured_summary(
    unit: LectureUnit,
    summary: dict[str, Any] | None,
    status: dict[str, Any] | None,
    glossary: dict[str, dict[str, str]],
    language_report: dict[str, int],
) -> str:
    status = status or {}
    if not summary:
        reason = status.get("reasonIfMissing") or "LLM summary was not generated for this lecture."
        status_name = status.get("llmSummaryStatus") or "fallback_cleaned_excerpt"
        return f"""
<div class="llm-summary-status missing" data-llm-status="{html.escape(str(status_name))}">
  <span class="feature-badge-limited">LLM summary not available</span>
  <p>Reason: {html.escape(str(reason))}. Showing cleaned source excerpts instead.</p>
</div>
"""
    sections_html: list[str] = []
    for section in summary.get("sections") or []:
        paragraphs_html: list[str] = []
        for paragraph in section.get("paragraphs") or []:
            text = safe_source_note_html(
                str(paragraph.get("text") or ""),
                glossary,
                language_report,
                [str(ref) for ref in paragraph.get("sourceRefs") or []],
                raw_text=None,
                terms=section.get("keyTerms") or [],
                lecture_title=unit.lecture_title,
            )
            if not text:
                continue
            refs = "".join(
                f'<span class="page-ref">{html.escape(compact_source_ref(str(ref)))}</span>'
                for ref in paragraph.get("sourceRefs") or []
            )
            paragraphs_html.append(f"<p>{text} {refs}</p>")
        if not paragraphs_html:
            continue
        terms = "".join(f"<li>{html.escape(str(term))}</li>" for term in section.get("keyTerms") or [])
        terms_html = f'<ul class="llm-key-terms">{terms}</ul>' if terms else ""
        quotes = []
        for quote in section.get("sourceQuotes") or []:
            quote_text = html.escape(str(quote.get("text") or ""))
            quote_ref = html.escape(compact_source_ref(str(quote.get("sourceRef") or "")))
            if quote_text:
                quotes.append(f'<blockquote class="source-quote"><span class="quote-label">Short source quote</span> {quote_text} <span class="page-ref">{quote_ref}</span></blockquote>')
        quote_html = "".join(quotes)
        sections_html.append(
            f"""
<section class="llm-summary-section">
  <h3>{html.escape(str(section.get("title") or "核心概念"))}</h3>
  {''.join(paragraphs_html)}
  {terms_html}
  {quote_html}
</section>
"""
        )
    if not sections_html:
        return f"""
<div class="llm-summary-status missing" data-llm-status="llm_schema_invalid">
  <span class="feature-badge-limited">LLM summary not available</span>
  <p>Reason: validated summary had no renderable sections. Showing cleaned source excerpts instead.</p>
</div>
"""
    language_report["highQualityChineseSummaryCount"] += 1
    return f"""
<section class="llm-structured-summary source-note-section llm-summary-zh-section" data-note-state="llm_summary_zh" data-llm-status="success">
  <header class="llm-summary-header">
    <span class="feature-badge-llm">Generated with LLM</span>
    <h3 class="source-note-heading">LLM Structured Summary</h3>
  </header>
  {''.join(sections_html)}
</section>
"""


def render_source_grounded_notes(
    unit: LectureUnit,
    glossary: dict[str, dict[str, str]],
    llm_note: dict[str, Any] | None,
    llm_status: dict[str, Any] | None,
    llm_enabled: bool,
    language_report: dict[str, int],
    generation_mode: str,
) -> str:
    title_key = "mode.sourceGroundedNotes" if generation_mode == "online_llm" else "mode.sourceExplorer"
    title = "Source-grounded Notes" if generation_mode == "online_llm" else "Source Explorer"
    description_key = "mode.sourceGroundedNote" if generation_mode == "online_llm" else "mode.sourceExplorerNote"
    description = i18n_text(description_key)
    warning = "" if llm_enabled else f'<div class="note mode-note" data-site-i18n="mode.llmDisabledFallback">{html.escape(i18n_text("mode.llmDisabledFallback"))}</div>'
    overview_terms = extract_terms(unit.full_text, limit=6)
    overview_ref = unit.pages_or_sections[0].source_ref if unit.pages_or_sections else unit.source_file
    overview_excerpt = build_clean_source_excerpt(unit.full_text, unit.lecture_title, key_terms=overview_terms)
    overview_note = {
        "title": "Lecture overview / 本讲概览",
        "summary_zh": "",
        "source_excerpt": overview_excerpt,
        "state": "fallback_cleaned_excerpt" if overview_excerpt else "empty",
        "source_refs": [overview_ref],
        "key_terms": overview_terms,
        "source_quotes": [],
    }
    selected_numbers = set((unit.metadata.get("slide_images") or {}).keys())
    pages = []
    seen_ids: set[str] = set()
    for section in unit.pages_or_sections[:8]:
        pages.append(section)
        seen_ids.add(section.id)
    for section in unit.pages_or_sections:
        if section.page_number in selected_numbers and section.id not in seen_ids:
            pages.append(section)
            seen_ids.add(section.id)
    pages = pages[:14]
    quote_budget = min(8, max(2, len(pages) // 5 + 1))
    unit_quote_report = language_report.setdefault("sourceQuoteControlByLecture", {})
    unit_quote_report[unit.lecture_id] = {"maxQuotesAllowed": quote_budget, "sourceQuotesRendered": 0}
    selected_quotes = select_source_quotes_for_lecture(
        pages,
        unit.lecture_title,
        language_report["sourceQuoteControlReport"],
        max_quotes_per_lecture=quote_budget,
    )
    cards = []
    for index, section in enumerate(pages):
        fig = build_slide_figure_html(unit, section.page_number or 0, section.source_ref)
        note = build_source_note_payload(section, unit.lecture_title, has_slide_figure=bool(fig))
        title = note["title"]
        paragraph = build_source_paragraph(section, glossary, language_report, unit.lecture_title, has_slide_figure=bool(fig))
        quote_html = build_source_quote_html(section, selected_quotes.get(section.id))
        body_html = ""
        state_class = note["state"].replace("_", "-")
        if paragraph:
            language_report["highQualityChineseSummaryCount"] += 1
            body_html = f'<p class="source-note-paragraph">{paragraph} <span class="page-ref">{html.escape(compact_source_ref(section.source_ref))}</span></p>'
            state_class = "summary-zh"
        elif note["source_excerpt"]:
            language_report["sourceExcerptCount"] += 1
            body_html = (
                '<div class="source-excerpt-card">'
                '<span class="excerpt-label">Cleaned source excerpt</span>'
                f'<p>{html.escape(note["source_excerpt"])} <span class="page-ref">{html.escape(compact_source_ref(section.source_ref))}</span></p>'
                '</div>'
            )
        elif fig:
            language_report["visualOnlySectionCount"] += 1
        else:
            language_report["skippedLowQualitySections"] += 1
            continue
        if quote_html:
            language_report["renderedAsSourceQuotes"] += 1
            language_report["sourceQuoteControlReport"]["quotesRendered"] += 1
            unit_quote_report[unit.lecture_id]["sourceQuotesRendered"] += 1
        cards.append(
            f"""
<article class="source-note-section {html.escape(state_class)}-section" id="{html.escape(section.id)}" data-note-state="{html.escape(note["state"])}">
  <h3 class="source-note-heading">{html.escape(title)}</h3>
  {body_html}
  {quote_html}
  {fig}
</article>
"""
        )
    if generation_mode == "online_llm":
        llm_block = render_llm_structured_summary(unit, llm_note, llm_status, glossary, language_report)
    else:
        llm_block = ""
    overview_body = ""
    if overview_note["source_excerpt"]:
        language_report["sourceExcerptCount"] += 1
        overview_body = (
            '<div class="source-excerpt-card">'
            '<span class="excerpt-label">Cleaned source excerpt</span>'
            f'<p>{html.escape(overview_note["source_excerpt"])} <span class="page-ref">{html.escape(compact_source_ref(overview_ref))}</span></p>'
            '</div>'
        )
    return f"""
<section id="{html.escape(unit.lecture_id)}-notes">
  <h2 data-site-i18n="{html.escape(title_key)}">{html.escape(title)}</h2>
  <p class="mode-note" data-site-i18n="{html.escape(description_key)}">{html.escape(description)}</p>
  {warning}
  <article class="source-note-section source-excerpt-section" data-note-state="fallback_cleaned_excerpt">
    <h3 class="source-note-heading">Lecture overview / 本讲概览</h3>
    {overview_body}
  </article>
  {llm_block}
  {''.join(cards)}
</section>
"""


def render_glossary(unit: LectureUnit, glossary: dict[str, dict[str, str]]) -> str:
    rows = []
    for term, item in glossary.items():
        explanation = item["explanation"]
        source_ref = item.get("source_ref") or "fallback explanation"
        label = ""
        if item.get("source_type") == "fallback":
            label = '<span class="ai-label">fallback explanation; not directly quoted from source material</span>'
        elif item.get("source_type") == "source-context":
            label = '<span class="term-source-label">source-context explanation</span>'
        rows.append(
            f"""
<tr>
  <th><span class="term" tabindex="0" data-tooltip="{html.escape(explanation)}">{html.escape(term)}</span></th>
  <td>{render_terms(explanation, glossary)} <span class="page-ref">{html.escape(source_ref)}</span> {label}</td>
</tr>
"""
        )
    if not rows:
        rows.append("<tr><td>未提取到明显术语。</td></tr>")
    return f"""
<section id="{html.escape(unit.lecture_id)}-terms">
  <h2>Glossary / 术语表</h2>
  <div class="table-wrap"><table class="glossary-table"><tbody>{''.join(rows)}</tbody></table></div>
</section>
"""


def render_nav(units: list[LectureUnit], has_failed_files: bool = False) -> str:
    links = ['<a class="nav-overview" href="#overview" data-site-i18n="overview">课程总览</a>']
    links.append('<a class="nav-page" href="#slide-gallery">Slide Gallery</a>')
    for unit in units:
        links.append(
            f'<div class="nav-group"><a class="nav-lecture" href="#{unit.lecture_id}"><span>{html.escape(unit.lecture_id.replace("lecture-", "").replace("lecture-unit-", "U"))}</span>{html.escape(unit.lecture_title[:44])}</a>'
            f'<div class="nav-children"><a href="#{unit.lecture_id}-map">Lecture Map</a><a href="#{unit.lecture_id}-notes">Source Explorer</a><a href="#{unit.lecture_id}-related">Related Lectures</a><a href="#{unit.lecture_id}-terms">Glossary</a><a href="#{unit.lecture_id}-sources">Sources</a></div></div>'
        )
    if has_failed_files:
        links.append('<a class="nav-page" href="#failed-files" data-site-i18n="failedFiles">未能处理的文件</a>')
    return "".join(links)


def render_sources_panel(unit: LectureUnit) -> str:
    source_count = min(len(unit.pages_or_sections), 30)
    sources = "".join(
        f'<li class="source-item"><span class="page-ref">{html.escape(section.source_ref)}</span> {html.escape(semantic_title(section, index))}</li>'
        for index, section in enumerate(unit.pages_or_sections[:30])
    )
    open_attr = " open" if source_count <= 3 else ""
    return f"""
<section id="{html.escape(unit.lecture_id)}-sources" class="sources-section">
  <details class="sources-panel"{open_attr}>
    <summary>
      <span class="sources-summary-main">
        <span data-site-i18n="sources.title">{html.escape(i18n_text("sources.title"))}</span>
        <span class="sources-count"><span>{source_count}</span> <span data-site-i18n="sources.count">{html.escape(i18n_text("sources.count"))}</span></span>
      </span>
      <span class="sources-hint" data-site-i18n="sources.expandHint">{html.escape(i18n_text("sources.expandHint"))}</span>
    </summary>
    <ul class="sources-list">{sources}</ul>
  </details>
</section>
"""


def render_unit(
    unit: LectureUnit,
    all_units: list[LectureUnit],
    llm_note: dict[str, Any] | None,
    llm_status: dict[str, Any] | None,
    llm_enabled: bool,
    language_report: dict[str, int],
    generation_mode: str,
) -> str:
    glossary = build_glossary_terms(unit, all_units)
    return f"""
<section class="lecture-section" id="{html.escape(unit.lecture_id)}">
  <div class="lecture-heading"><div><div class="eyebrow">{html.escape(unit.source_type.upper())}</div><h1>{html.escape(unit.lecture_title)}</h1></div><span class="quality">{len(unit.pages_or_sections)} source sections</span></div>
  <p class="source">源文件：{html.escape(unit.source_file)}</p>
  {render_lecture_map(unit)}
  {render_source_grounded_notes(unit, glossary, llm_note, llm_status, llm_enabled, language_report, generation_mode)}
  {render_cross_lecture_references(unit, all_units, generation_mode)}
  <section id="{html.escape(unit.lecture_id)}-extension"><h2>Creative Extension / 自由拓展内容</h2><div class="note creative-extension">AI-generated extension; not directly from uploaded notes. This area is reserved for analogies, code practice, and system-design style questions inspired by the source material.</div></section>
  {render_glossary(unit, glossary)}
  {render_sources_panel(unit)}
</section>
"""


def render_failed_files(failed_files: list[dict[str, str]]) -> str:
    if not failed_files:
        return ""
    rows = "".join(
        f"<tr><td>{html.escape(item.get('file', 'unknown'))}</td><td>{html.escape(item.get('reason', 'unknown error'))}</td></tr>"
        for item in failed_files
    )
    return f"""
<section class="lecture-section" id="failed-files">
  <div class="lecture-heading"><div><div class="eyebrow">Processing Report</div><h1>未能处理的文件</h1></div><span class="quality">{len(failed_files)} files</span></div>
  <p>以下文件在本次生成中未能成功提取文本。站点其余内容仍然基于成功处理的文件生成。</p>
  <div class="table-wrap"><table><thead><tr><th>File</th><th>Reason</th></tr></thead><tbody>{rows}</tbody></table></div>
</section>
"""


def build_index_html(
    units: list[LectureUnit],
    project_name: str,
    llm_notes: dict[str, dict[str, Any]],
    llm_enabled: bool,
    language_report: dict[str, int],
    metadata: dict[str, Any],
    failed_files: list[dict[str, str]] | None = None,
) -> str:
    generation_mode = str(metadata.get("generationMode") or ("online_llm" if llm_enabled else "offline"))
    llm_status_by_lecture = {
        str(item.get("lectureId")): item
        for item in (metadata.get("llmSummaryStatuses") or metadata.get("llmTelemetry", {}).get("lectureStatuses") or [])
        if isinstance(item, dict)
    }
    sections = "\n".join(
        render_unit(unit, units, llm_notes.get(unit.lecture_id), llm_status_by_lecture.get(unit.lecture_id), llm_enabled, language_report, generation_mode)
        for unit in units
    )
    failed_section = render_failed_files(failed_files or [])
    slide_gallery = render_slide_gallery(units)
    overview = f"""
<section class="lecture-section active-page" id="overview">
  <div class="lecture-heading"><div><div class="eyebrow">Local-first</div><h1>{html.escape(project_name)} Knowledge Site</h1></div><span class="quality">{len(units)} learning units</span></div>
  {render_mode_capability_banner(metadata, generation_mode)}
  {render_feature_matrix(generation_mode)}
  <div class="outcome-grid"><div><strong>Source Explorer</strong><p>Offline Mode organizes cleaned excerpts, source references, search, lecture maps, related lectures, and slide figures.</p></div><div><strong>Online LLM Mode</strong><p>Chinese structured summaries and advanced practice require a configured LLM provider.</p></div><div><strong>Versioned output</strong><p>每次生成都会写入新的 output_sites 版本文件夹。</p></div></div>
</section>
"""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(project_name)} Knowledge Site</title>
  <link rel="stylesheet" href="style.css">
  <script defer src="script.js"></script>
  <script>
    window.MathJax = {{tex: {{inlineMath: [['\\\\(', '\\\\)']], displayMath: [['\\\\[', '\\\\]']]}}}};
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body data-generation-mode="{html.escape(generation_mode)}">
<header class="mobile-header"><button id="menu-toggle" aria-expanded="false" data-site-i18n="menu">目录</button><strong>{html.escape(project_name)}</strong><button id="theme-toggle-mobile" data-site-i18n="theme">Theme</button></header>
<aside class="sidebar" id="sidebar"><div class="brand"><h1>{html.escape(project_name)}</h1><p>Versioned Local-first Lecture Knowledge Generator</p><label class="site-language-switch"><span data-site-i18n="uiLanguage">界面语言</span><select id="site-ui-language"><option value="zh">中文</option><option value="en">English</option></select></label><div class="search-panel"><input id="site-search" class="search-input" data-site-i18n-placeholder="searchPlaceholder" placeholder="搜索笔记..." autocomplete="off"><div id="search-results"></div></div><button id="theme-toggle" type="button" data-site-i18n="toggleTheme">切换主题</button></div><nav>{render_nav(units, bool(failed_files))}</nav></aside>
<main>
{overview}
{slide_gallery}
{sections}
{failed_section}
{practice_generator_html(generation_mode)}
</main>
<button id="back-to-top" aria-label="Back to top">↑</button>
<div class="lightbox" id="slide-lightbox" aria-hidden="true"><button type="button" aria-label="Close">×</button><img alt=""><p></p></div>
</body>
</html>"""


def practice_generator_html(generation_mode: str = "offline") -> str:
    note_key = "mode.practiceOnlineNote" if generation_mode == "online_llm" else "mode.practiceOfflineNote"
    offline_note = i18n_text(note_key)
    return """
<section class="practice-generator" id="practice-generator" aria-labelledby="practice-title">
  <div class="practice-header"><div><div class="eyebrow">Exam Practice</div><h2 id="practice-title" data-site-i18n="practiceTitle">备考题生成器</h2></div><p data-site-i18n="practiceDesc">Source-grounded Practice 严格基于资料；Creative Extension 可生成应用场景和系统设计题。</p></div>
  <p class="mode-note practice-mode-note" data-site-i18n=\"""" + html.escape(note_key) + """\">""" + html.escape(offline_note) + """</p>
  <div class="practice-tabs" role="tablist"><button class="practice-tab active" type="button" data-practice-mode-tab="source">Source-grounded Practice</button><button class="practice-tab" type="button" data-practice-mode-tab="creative">Creative Extension Practice <span class="feature-badge-llm" data-site-i18n="mode.requiresLlm">""" + html.escape(i18n_text("mode.requiresLlm")) + """</span></button></div>
  <div class="note creative-extension practice-extension-note" hidden>AI-generated extension; not directly from uploaded notes. AI 自由拓展内容，不是原始笔记来源。</div>
  <div class="practice-controls">
    <label><span data-site-i18n="questionSource">题目来源</span><select class="practice-source"><option value="current-lecture">当前 Lecture</option><option value="search-context">搜索关键词相关内容</option><option value="custom-context">自定义内容</option></select></label>
    <label><span data-site-i18n="keyword">关键词</span><input class="practice-keyword" type="text" placeholder="attention, BERT, ASR..." autocomplete="off"></label>
    <label><span data-site-i18n="questionType">题型</span><select class="practice-type"><option value="mixed">Mixed</option><option value="multiple-choice">Multiple-choice</option><option value="concept">Concept question</option><option value="short-answer">Short-answer</option><option value="code-cloze">Code cloze</option><option value="application-scenario">Application scenario (Requires LLM)</option></select><small class="practice-type-hint" data-site-i18n="practiceTypeHint">选择具体题型时只生成该题型；Mixed 才会混合题型。</small></label>
    <label><span data-site-i18n="difficulty">难度</span><select class="practice-difficulty"><option value="easy">Easy</option><option value="medium" selected>Medium</option><option value="hard">Hard (Requires LLM for advanced scenarios)</option></select></label>
    <label><span data-site-i18n="count">数量</span><select class="practice-count"><option value="3">3</option><option value="5" selected>5</option><option value="10">10</option></select></label>
    <label><span data-site-i18n="answerDisplay">答案显示</span><select class="practice-answer-mode"><option value="hidden" selected>先隐藏答案</option><option value="visible">立即显示答案</option></select></label>
  </div>
  <textarea class="custom-practice-context" hidden placeholder="Paste custom context here..."></textarea>
  <details class="llm-settings"><summary>LLM Settings / 可选</summary><p class="llm-warning">浏览器端 API key 仅适合本地自用。公开部署请改成后端代理。</p><div class="practice-controls llm-controls"><label>模式<select class="practice-mode"><option value="local" selected>Local template mode</option><option value="api">OpenAI-compatible API mode</option></select></label><label>Endpoint URL<input class="llm-endpoint" type="url" placeholder="https://api.example.com/v1/chat/completions"></label><label>Model<input class="llm-model" type="text" placeholder="model-name"></label><label>API key<input class="llm-api-key" type="password" placeholder="Stored only in this browser"></label></div></details>
  <div class="practice-actions"><button class="generate-practice-btn" type="button" data-site-i18n="generatePractice">生成练习题</button><button class="reveal-all-answers-btn" type="button" disabled data-site-i18n="revealAnswers">显示全部答案</button><button class="copy-questions-btn" type="button" disabled data-site-i18n="copyQuestions">复制题目</button></div>
  <p class="practice-hint" data-site-i18n="practiceHint">重复点击 Generate 会重新采样上下文，并尽量生成不同角度、不同术语和不同场景的问题。</p>
  <div class="practice-status" aria-live="polite"></div><div class="practice-output" aria-live="polite"></div>
</section>
"""


def build_site(
    units: list[LectureUnit],
    output_path: Path,
    project_name: str,
    metadata: dict[str, Any],
    template_dir: Path,
    llm_notes: dict[str, dict[str, Any]] | None = None,
    llm_enabled: bool = False,
) -> None:
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "assets" / "slides").mkdir(parents=True, exist_ok=True)
    for unit in units:
        render_pdf_slide_images(unit, output_path)
    language_report = {
        "suspiciousRawEnglishParagraphsDetected": 0,
        "suspiciousRawEnglishSourceInputsDetected": 0,
        "rewrittenWithLLM": 0,
        "rewrittenWithFallback": 0,
        "blockedRawEnglishParagraphs": 0,
        "englishLeakageParagraphsDetected": 0,
        "metadataLeakageDetected": 0,
        "longEnglishRunsDetected": 0,
        "renderedAsSourceQuotes": 0,
        "lowQualityChineseFallbackBlocked": 0,
        "sourceExcerptCount": 0,
        "visualOnlySectionCount": 0,
        "highQualityChineseSummaryCount": 0,
        "skippedLowQualitySections": 0,
        "sourceQuoteControlReport": {
            "rawQuotesCollected": 0,
            "quotesAfterFiltering": 0,
            "quotesRendered": 0,
            "duplicateQuotesRemoved": 0,
            "longQuotesRemoved": 0,
            "lowInformationQuotesRemoved": 0,
        },
        "sourceQuoteControlByLecture": {},
    }
    html_text = build_index_html(
        units,
        project_name,
        llm_notes or {},
        llm_enabled,
        language_report,
        metadata,
        metadata.get("failedFiles") or [],
    )
    metadata["languageNormalizationReport"] = language_report
    (output_path / "index.html").write_text(html_text, encoding="utf-8")
    shutil.copyfile(template_dir / "style.css", output_path / "style.css")
    shutil.copyfile(template_dir / "script.js", output_path / "script.js")
    (output_path / "search-index.json").write_text(json.dumps(build_search_index(units), ensure_ascii=False, indent=2), encoding="utf-8")
    (output_path / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

