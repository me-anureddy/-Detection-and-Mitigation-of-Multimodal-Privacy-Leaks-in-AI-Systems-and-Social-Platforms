# High-Level Design Document
## LeakWatch: Detection and Mitigation of Multimodal Privacy Leaks in AI Systems and Social Platforms

**Project Title:** LeakWatch Middleware for Multimodal Privacy Protection

**Domain:** Artificial Intelligence Systems, Privacy Engineering, Information Security

**Academic Context:** UE23CS320A Capstone Project - Phase 2 Implementation

**Document Version:** 2.0

**Date:** February 2026

---

## 1. Introduction

### 1.1 Purpose of the System

LeakWatch is a privacy-preserving middleware designed to detect and mitigate privacy leaks in multimodal user content (text, images, audio, and video) before such content is transmitted to downstream AI systems, machine learning pipelines, or social media platforms. The system operates as an independent, non-invasive protective layer that intercepts user-generated content, identifies sensitive information (Personally Identifiable Information, biometric data, and confidential content), applies appropriate mitigation strategies, and produces sanitized output with comprehensive audit trails.

The primary purpose of LeakWatch is to address the critical gap between user intent regarding data sharing and the actual exposure of sensitive information when interacting with AI systems and social platforms. By implementing privacy-first principles at the middleware level, the system enables organizations to meet regulatory compliance requirements (GDPR, CCPA) while maintaining user trust and transparency.

### 1.2 Scope of the Project

**Phase 2 Scope (Current Implementation):**

The current implementation focuses on establishing a robust foundation for multimodal privacy protection with complete support for two primary modalities and adapter architecture for secondary modalities.

- **Full Implementation:**
  - Text modality: Named Entity Recognition (NER)-based detection, rule-based heuristics, token-level analysis, and deterministic mitigation strategies (masking, redaction, synthesis)
  - Image modality: Object detection (face detection via Haar cascades and YOLO-compatible models), Optical Character Recognition (OCR) integration, bounding box extraction, and region-level mitigation (blur, inpainting)
  - Unified orchestration framework with configuration-driven detection and mitigation pipelines
  - CLI and REST API interfaces for easy integration
  - Explainability module with visual overlays and comprehensive audit logging

- **Partial Implementation:**
  - Audio and Video modalities: Implemented as adapter stubs that convert audio to text (via Automatic Speech Recognition) and video to image frames, enabling reuse of hardened text and image pipelines
  - Graph-based context structures (metadata representation for future GraphSAGE integration)

- **Future Enhancements (Phase 3+):**
  - Advanced mitigation using Generative Adversarial Networks (GANs) for realistic inpainting
  - Graph Neural Networks (GraphSAGE) for context-aware detection
  - Real-time streaming support
  - Integration with major platform APIs
  - Custom machine learning model deployment

---

## 2. System Overview

### 2.1 Architecture Style

LeakWatch adopts a **modular layered architecture combined with adapter and pipeline patterns**. The system is characterized by clear separation of concerns across detection, mitigation, orchestration, and explainability layers, enabling independent development, testing, and extension of each component.

**Architecture Paradigm:**
- **Layered Architecture:** Vertical separation into input processing, detection, mitigation, and output layers
- **Adapter Pattern:** Audio/video modalities adapt to existing text/image pipelines
- **Pipeline Pattern:** Sequential processing stages with data transformation at each step
- **Service-Oriented:** REST API wrapper enables service-based deployment

### 2.2 Key Design Principles

#### 2.2.1 Privacy-by-Design
- Sensitive data is treated as suspicious from the moment of ingestion
- All processing follows a "detect-mitigate-verify" pattern
- Audit trails are mandatory for all operations
- User control and transparency are paramount

#### 2.2.2 Non-Invasiveness
- LeakWatch operates independently of downstream AI systems
- No modification to existing AI pipelines or platform APIs required
- Acts as middleware: can be inserted before any AI system or data pipeline
- Minimal computational overhead through efficient algorithms

#### 2.2.3 Determinism and Reproducibility
- Detection and mitigation algorithms are fully deterministic (Phase 2)
- No machine learning model training or fine-tuning
- Ensures reproducibility for compliance audits
- Reduces variance and improves trustworthiness

#### 2.2.4 Modularity and Extensibility
- Each modality (text, image, audio, video) is independently implemented
- Detection and mitigation strategies are decoupled
- Configuration-driven behavior enables flexibility without code changes
- Clear interfaces for adding new detection models or mitigation techniques

#### 2.2.5 Transparency and Explainability
- All decisions must be explainable: what was detected, where, and why
- Visual and textual artifacts accompany every mitigation action
- Comprehensive audit logs enable regulatory compliance and forensic analysis

---

## 3. Architecture Diagram Explanation

### 3.1 System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                          LeakWatch System Architecture                     │
└───────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           INPUT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  CLI Interface (Typer)  │  REST API (FastAPI)  │  Batch Processing      │
│                   ↓                  ↓                    ↓              │
│              Configuration & Policy Injection            │              │
└──────────────────────────────┬───────────────────────────┘              │
                               │                                           │
                               ▼                                           │
┌─────────────────────────────────────────────────────────────────────────┐
│                    PRE-PROCESSING LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  Content Type Detection  │  Format Validation  │  Normalization         │
│  Size/Dimension Checks   │  Encoding Handling  │  Sanitization          │
└──────────────────────┬────────────────────────────┬──────────────────────┘
                       │                            │
              ┌────────┴────────┐           ┌───────┴────────┐
              │                 │           │                │
              ▼                 ▼           ▼                ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  ┌────────────┐
│  TEXT MODULE     │  │ IMAGE MODULE     │  │AUDIO ADAPTER │  │VIDEO ADAPT │
│  ────────────   │  │ ────────────────  │  │ ────────────  │  │ ──────────┘
│ • Tokenization  │  │• Preprocessing   │  │• ASR Conv.  │  │• Frame Ext.
│ • NER           │  │• Face Detection  │  │• Reuse Text  │  │• Reuse Img.
│ • Rules/Regex   │  │• OCR Scanning    │  │• Config-'d  │  │• Config-d
│ • GraphCoding   │  │• BBox Extraction │  │             │  │
└────────┬─────────┘  └────────┬─────────┘  └──────┬──────┘  └─────┬──────┘
         │                     │                   │               │
         │        ┌────────────┼───────────────────┼───────────┐   │
         │        │            │                   │           │   │
         └────────┼────────────┼───────────────────┼───────────┘   │
                  │            │                   │               │
                  ▼            ▼                   ▼               ▼
         ┌──────────────────────────────────────────────────────────┐
         │          UNIFIED DETECTION OUTPUT                         │
         │                                                            │
         │  Format: JSON with detection results                      │
         │  • Entity/Region Type                                     │
         │  • Location (token index / bounding box)                  │
         │  • Confidence Score                                       │
         │  • Modality Information                                   │
         │  • Contextual Metadata                                    │
         └────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
         ┌──────────────────────────────────────────────────────────┐
         │        ORCHESTRATION LAYER (Pipeline Manager)             │
         │                                                            │
         │  • Aggregate detection results across modalities           │
         │  • Apply policy and risk assessment                        │
         │  • Decide mitigation strategy per detection               │
         │  • Maintain execution state and dependencies              │
         │  • Route to appropriate mitigation module                 │
         └────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
         ┌──────────────────────────────────────────────────────────┐
         │           MITIGATION MODULE                               │
         │                                                            │
         │  ┌─────────────┐  ┌──────────────┐                       │
         │  │TEXT STRAT.  │  │ IMAGE STRAT.  │                      │
         │  │──────────── │  │──────────────│                       │
         │  │• Masking    │  │• Blur        │                       │
         │  │• Redaction  │  │• Pixelation  │                       │
         │  │• Replace    │  │• Inpaint     │                       │
         │  │• Synthetic  │  │• Overlay     │                       │
         │  └─────────────┘  └──────────────┘                       │
         │                                                            │
         │  ┌──────────────┐  ┌──────────────┐                      │
         │  │AUDIO STRAT.  │  │VIDEO STRAT.  │                      │
         │  │────────────  │  │────────────  │                      │
         │  │• Mute Seg.   │  │• Frame Blur  │                      │
         │  │• Beeping     │  │• Feature Strip│                      │
         │  │• Voice Mod.  │  │• Reuse Image │                      │
         │  └──────────────┘  └──────────────┘                       │
         └────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
         ┌──────────────────────────────────────────────────────────┐
         │     EXPLAINABILITY & AUDIT MODULE                         │
         │                                                            │
         │  • Highlight sensitive regions (text spans, bboxes)       │
         │  • Generate visual overlays                               │
         │  • Create audit logs (JSONL format)                       │
         │  • Track decision rationale                               │
         │  • Compliance report generation                           │
         └────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
         ┌──────────────────────────────────────────────────────────┐
         │          OUTPUT LAYER                                     │
         │                                                            │
         │  • Sanitized Content Artifact                             │
         │  • Audit Log (JSON/JSONL)                                │
         │  • Explainability Artifacts (overlays, spans, reports)    │
         │  • Policy Decision (ALLOW/BLOCK)                         │
         │  • Metadata & Statistics                                  │
         └────────────────────────┬────────────────────────────────┘
                                  │
                                  ▼
         ┌──────────────────────────────────────────────────────────┐
         │    DOWNSTREAM SYSTEMS                                     │
         │                                                            │
         │  • AI Systems (ML pipelines)                              │
         │  • Social Platforms (storage, processing)                 │
         │  • Analytics Systems (monitoring, reporting)              │
         └──────────────────────────────────────────────────────────┘
```

### 3.2 Major Components Description

#### 3.2.1 Input Layer
- **CLI Interface:** Typer-based command-line tool for scanning files and folders
- **REST API:** FastAPI service enabling integration with web applications and microservices
- **Batch Processing:** Support for processing large datasets without interactive input

#### 3.2.2 Pre-Processing Layer
- **Content Type Detection:** Identifies input data type (text, image, etc.)
- **Format Validation:** Verifies format integrity and compatibility
- **Normalization:** Standardizes encoding, dimensions, and representation
- **Size Validation:** Checks file size constraints and prevents resource exhaustion

#### 3.2.3 Detection Layer (Modality-Specific)
- **Text Module:** Implements NER, rule-based detection, and token-level analysis
- **Image Module:** Performs face detection, OCR scanning, and bounding box extraction
- **Audio Adapter:** Converts audio to text via ASR and reuses text detection module
- **Video Adapter:** Extracts key frames and reuses image detection module

#### 3.2.4 Unified Detection Output Format
All modalities produce standardized JSON output containing:
- Detection type (entity type, region type)
- Precise location (token index range, pixel coordinates)
- Confidence score (0.0 to 1.0)
- Modality-specific metadata

#### 3.2.5 Orchestration Layer
- **Policy Engine:** Applies user-defined policies to detection results
- **Risk Assessment:** Calculates risk scores based on sensitivity levels
- **Routing Logic:** Determines appropriate mitigation strategy for each detection
- **Dependency Management:** Handles dependencies between detections (e.g., covering related sensitive tokens)

#### 3.2.6 Mitigation Module
Implements modality-specific mitigation strategies:
- **Text:** Masking (XXX), redaction (removal), replacement, synthetic generation
- **Image:** Blur (Gaussian/motion), pixelation, inpainting, overlay markers
- **Audio:** Segment muting, beeping, voice modulation
- **Video:** Frame-level mitigation, feature stripping, silence insertion

#### 3.2.7 Explainability & Audit Layer
- **Visual Artifacts:** Generated overlays showing detected regions and mitigations
- **Text Reports:** Detailed span reports with before/after snippets
- **Audit Logs:** Comprehensive JSONL logs with timestamp, modality, entity, strategy, and output path
- **Compliance Reports:** Structured documents for regulatory audit (GDPR, CCPA)

#### 3.2.8 Output Layer
Delivers:
- Sanitized content artifacts (text file, image file, audio/video files)
- Audit trail (machine-readable and human-readable formats)
- Explainability artifacts (overlays, span reports, heatmaps)
- Policy decision (ALLOW/BLOCK for downstream consumption)

---

## 4. Major Modules

### 4.1 Text Detection Module

**Location:** `leakwatch/detection/text.py`

**Responsibilities:**
- Perform Named Entity Recognition (NER) to identify PII, sensitive organizations, products
- Apply regex-based rules to detect emails, phone numbers, SSN, credit card numbers
- Construct token-level graph representations for contextual analysis
- Score confidence levels for each detected entity
- Generate detailed span information (start index, end index, entity type)

**Inputs:**
- Raw text string
- Configuration object specifying which entity types to detect
- Policy object defining sensitivity levels and thresholds

**Outputs:**
```json
{
  "modality": "text",
  "detections": [
    {
      "type": "PERSON",
      "text": "John Smith",
      "start_idx": 45,
      "end_idx": 56,
      "confidence": 0.95,
      "source": "spacy_ner"
    },
    {
      "type": "EMAIL",
      "text": "john@example.com",
      "start_idx": 120,
      "end_idx": 136,
      "confidence": 0.99,
      "source": "regex"
    }
  ],
  "total_detections": 2,
  "processing_time_ms": 45
}
```

**Key Algorithms:**
- spaCy v3.7 NER with `en_core_web_sm` model
- Comprehensive regex patterns for structured PII
- Token graph construction for context preservation

---

### 4.2 Image Detection Module

**Location:** `leakwatch/detection/image.py`

**Responsibilities:**
- Detect faces in images using Haar Cascades and YOLO-compatible models
- Perform OCR-assisted text scanning to identify embedded sensitive text
- Extract precise bounding boxes for all detected sensitive regions
- Calculate confidence scores based on detection model output
- Handle multi-scale analysis to detect small objects

**Inputs:**
- Image file path or bytes
- Configuration specifying detection models and thresholds
- Policy object defining regions to detect and sensitivity levels

**Outputs:**
```json
{
  "modality": "image",
  "detections": [
    {
      "type": "FACE",
      "bbox": {"x": 100, "y": 150, "width": 200, "height": 250},
      "confidence": 0.98,
      "source": "haar_cascade"
    },
    {
      "type": "TEXT_REGION",
      "text": "Confidential",
      "bbox": {"x": 50, "y": 500, "width": 300, "height": 50},
      "confidence": 0.92,
      "source": "ocr"
    }
  ],
  "total_detections": 2,
  "image_dimensions": [1920, 1080],
  "processing_time_ms": 312
}
```

**Key Features:**
- OpenCV Haar Cascades for face detection
- EasyOCR integration for text detection in images
- Support for multiple object detection models (expandable)
- Bounding box refinement and NMS (Non-Maximum Suppression)

---

### 4.3 Audio Adapter Module

**Location:** `leakwatch/adapters/__init__.py` (audio stub)

**Responsibilities:**
- Accept audio input (WAV, MP3, etc.)
- Perform Automatic Speech Recognition (ASR) to convert audio to text
- Delegate to text detection module
- Map temporal information from audio to text detections
- Return audio-specific mitigation recommendations (mute, beep)

**Inputs:**
- Audio file path
- Configuration with ASR model selection and parameters
- Text detection policy (inherited from text module)

**Outputs:**
```json
{
  "modality": "audio",
  "transcript": "My name is John Smith, email john@example.com",
  "text_detections": [...],  // Reused from text module output
  "aligned_detections": [
    {
      "type": "PERSON",
      "text": "John Smith",
      "start_time_sec": 2.5,
      "end_time_sec": 4.2,
      "confidence": 0.95
    }
  ],
  "mitigation_strategy": "mute_segment",
  "processing_time_ms": 2400
}
```

**Design Rationale:**
- Reuses hardened text detection pipeline
- Avoids training audio-specific ML models
- Leverages existing ASR libraries (future: integration with Whisper or similar)
- Maps detection results to audio timestamps for precise mitigation

---

### 4.4 Image Preprocessing & Video Adapter Module

**Location:** `leakwatch/adapters/__init__.py` (video stub)

**Responsibilities:**
- Extract key frames from video at configurable intervals
- Validate frame format and dimensions
- Delegate to image detection module for each frame
- Aggregate results across frames
- Track spatial and temporal continuity

**Inputs:**
- Video file path
- Frame extraction parameters (sampling rate, max frames)
- Image detection policy

**Outputs:**
```json
{
  "modality": "video",
  "frame_count": 120,
  "extracted_frames": 15,
  "frame_detections": [
    {
      "frame_number": 0,
      "timestamp_sec": 0.0,
      "image_detections": [...]  // Reused from image module
    }
  ],
  "aggregated_detections": [...],
  "mitigation_strategy": "frame_blur_and_mute",
  "processing_time_ms": 3500
}
```

**Design Rationale:**
- Avoids redundant model training for video-specific processing
- Enables reuse of optimized image detection pipeline
- Temporal tracking enables continuous mitigation regions
- Configurable sampling prevents processing overhead

---

### 4.5 Orchestration Layer (Pipeline Manager)

**Location:** `leakwatch/orchestration/pipeline.py`

**Responsibilities:**
- Load configuration from YAML file
- Parse input and route to appropriate detection modules
- Aggregate detection results across modalities
- Apply user-defined policies to detection results
- Sequence and execute mitigation strategies
- Manage file I/O and artifact generation
- Coordinate logging and audit trail creation

**Inputs:**
- User input (file path, content, or through API)
- YAML configuration file specifying policies, models, and parameters
- Optional policy overrides (CLI flags or API parameters)

**Outputs:**
- Sanitized content artifact
- Comprehensive audit log (JSONL)
- Explainability artifacts (overlays, span reports)
- Structured policy decision (ALLOW/BLOCK/CONDITIONAL)

**Key Responsibilities (Detailed):**

```python
class PipelineManager:
    def execute(self, input_path: str, config: Config) -> ExecutionResult:
        # 1. Load and validate input
        # 2. Detect input modality
        # 3. Route to appropriate detection module
        # 4. Aggregate detection results
        # 5. Apply policy and risk assessment
        # 6. Execute mitigation strategies
        # 7. Generate explainability artifacts
        # 8. Create audit logs
        # 9. Return results
```

---

### 4.6 Mitigation Module

**Location:** `leakwatch/mitigation/text.py`, `leakwatch/mitigation/image.py`

**Text Mitigation Strategies:**

| Strategy | Mechanism | Preserves | Use Case |
|----------|-----------|-----------|----------|
| **Masking** | Replace with [REDACTED] or *** | Grammar | Standard PII masking |
| **Redaction** | Remove sensitive text entirely | Format | Strict privacy requirement |
| **Replacement** | Substitute with plausible synthetic text | Context | Preserve sentence structure |
| **Synthesis** | Generate contextually appropriate replacement | Semantics | Maintain document meaning |

**Image Mitigation Strategies:**

| Strategy | Mechanism | Preserves | Use Case |
|----------|-----------|-----------|----------|
| **Blur** | Apply Gaussian blur to region | Document layout | Standard face obscuring |
| **Pixelation** | Reduce resolution in region | Document context | Alternative to blur |
| **Inpainting** | Fill region with background texture | Visual continuity | Advanced privacy |
| **Overlay** | Draw colored rectangle over region | Original data | Audit/review mode |

**Inputs:**
- Detected sensitive information (from detection modules)
- Mitigation strategy selection
- Original content
- Configuration parameters (blur kernel, replacement templates)

**Outputs:**
- Sanitized content (modified original)
- Mitigation metadata (what was changed, where, how)
- Artifact file path for storage

---

### 4.7 Explainability & Audit Module

**Location:** `leakwatch/explainability/text.py`, `leakwatch/explainability/image.py`, `leakwatch/explainability/audit.py`

**Responsibilities:**
- Generate text span reports showing detected entities with context
- Create image overlays with bounding boxes and labels
- Maintain comprehensive audit logs in JSONL format
- Track all detection and mitigation decisions with timestamps
- Support compliance reporting (GDPR data breach notification, CCPA)
- Enable forensic analysis of system decisions

**Text Explainability Artifacts:**
```
=== Text Privacy Detection Report ===
Input: "My name is John Smith, contact me at john@example.com"

DETECTION 1: PERSON
  Entity: "John Smith"
  Location: Character 11-21
  Confidence: 0.95
  Source: spaCy NER
  Mitigation: MASKED
  Original: "My name is John Smith..."
  Sanitized: "My name is [PERSON]..."

DETECTION 2: EMAIL
  Entity: "john@example.com"
  Location: Character 42-58
  Confidence: 0.99
  Source: Regex Pattern
  Mitigation: REPLACED
  Original: "...at john@example.com"
  Sanitized: "...at [email]"
```

**Audit Log Format (JSONL):**
```json
{
  "timestamp": "2026-02-09T14:30:45.123Z",
  "execution_id": "exec_abc123xyz789",
  "input_file": "demo_email.txt",
  "modality": "text",
  "detection": {
    "type": "EMAIL",
    "text": "john@example.com",
    "confidence": 0.99
  },
  "mitigation": {
    "strategy": "replacement",
    "original_snippet": "john@example.com",
    "sanitized_snippet": "[EMAIL_REDACTED]"
  },
  "output_path": "artifacts/demo_email.sanitized.txt"
}
```

---

### 4.8 Configuration Module

**Location:** `leakwatch/utils/config.py`

**Configuration Schema (YAML):**
```yaml
detection:
  text:
    enabled: true
    models:
      ner: "en_core_web_sm"
      use_regex: true
    entities_to_detect:
      - PERSON
      - EMAIL
      - PHONE_NUMBER
      - CREDIT_CARD
    confidence_threshold: 0.7
  
  image:
    enabled: true
    face_detection: "haar_cascade"
    ocr_enabled: true
    confidence_threshold: 0.8
  
  audio:
    enabled: false
    asr_model: "whisper"  # Future
  
  video:
    enabled: false
    frame_sampling: "10%"  # Sample 10% of frames

mitigation:
  text:
    strategy: "masking"  # [masking, redaction, replacement, synthesis]
    mask_token: "[REDACTED]"
  
  image:
    strategy: "blur"  # [blur, pixelation, inpaint, overlay]
    blur_kernel: 21
  
  default_sensitivity_level: "high"  # [low, medium, high]

policy:
  block_on_detections:
    - "credit_card"
    - "ssn"
  allow_on_detections: []
  threshold_for_block: 0.85

output:
  artifact_dir: "artifacts/"
  generate_span_reports: true
  generate_image_overlays: true
  audit_log_format: "jsonl"

logging:
  level: "INFO"
  output: "console"  # [console, file, both]
```

---

## 5. Data Flow Overview

### 5.1 High-Level Data Flow Diagram

```
INPUT PHASE
────────────────────────────────────────────────────────────────
User submits content via:
  • CLI: python -m leakwatch scan-text file.txt
  • API: POST /scan/text with JSON payload
  • Batch: Directory scan with configuration

                          ↓

VALIDATION & PRE-PROCESSING PHASE
─────────────────────────────────────────────────────────────

[1] Content Type Detection
    - Determine modality (text/image/audio/video)
    - Extract file metadata (size, format, encoding)

[2] Format Validation
    - Verify file integrity
    - Check encoding compatibility
    - Validate dimensions/duration

[3] Normalization
    - Standardize encoding (UTF-8 for text, RGB for images)
    - Resize images if necessary
    - Trim silence in audio

                          ↓

DETECTION PHASE (Modality-Specific)
────────────────────────────────────────────────────────────────

TEXT PATH:
  Input: Normalized text string
    ↓
  [Text Module]
    • Tokenization using spaCy
    • NER pass for entities (PERSON, ORG, GPE, etc.)
    • Regex pass for structured data (email, phone, SSN, card)
    • Token graph construction and context analysis
    ↓
  Output: JSON with detections {type, text, location, confidence}

IMAGE PATH:
  Input: Normalized image (RGB, standardized dimensions)
    ↓
  [Image Module]
    • Face detection using Haar Cascades
    • OCR scanning using EasyOCR
    • Object detection using YOLO (if enabled)
    • Bounding box extraction and filtering
    ↓
  Output: JSON with detections {type, bbox, confidence}

AUDIO PATH:
  Input: Audio file (WAV, MP3)
    ↓
  [Audio Adapter]
    • ASR conversion to text transcript
    • Time alignment (map text to audio segments)
    ↓
  [Text Module] ← Reuse text detection
    ↓
  Output: JSON with audio-aligned detections {type, time, confidence}

VIDEO PATH:
  Input: Video file (MP4, AVI)
    ↓
  [Video Adapter]
    • Frame extraction at configured intervals
    • Validation of each frame
    ↓
  [Image Module] ← Reuse for each frame
    ↓
  Output: JSON with per-frame and aggregated detections {type, bbox, frame}

                          ↓

AGGREGATION & ORCHESTRATION PHASE
────────────────────────────────────────────────────────────────

[Orchestration Layer]
  1. Collect all detection results from active modality modules
  2. Create unified detection list (standardized format)
  3. Apply confidence threshold filtering
  4. Load user-defined policies
  5. For each detection:
     a. Calculate risk score based on entity type and sensitivity
     b. Determine mitigation strategy (from policy)
     c. Check for conflicts/overlaps with other detections
     d. Sequence mitigation actions (if multiple)

Output: Decision matrix (detection → mitigation strategy mapping)

                          ↓

MITIGATION PHASE
────────────────────────────────────────────────────────────────

For each detection in sequence:

TEXT MITIGATION:
  Original: "Contact John Smith at john@example.com"
    ↓
  Strategy: [masking, redaction, replacement, synthesis]
    ↓
  Result: "Contact [PERSON] at [EMAIL]"
  OR
  Result: "Contact [REDACTED] at [REDACTED]"
  OR
  Result: "Contact Michael Johnson at michael.j@company.com" (synthetic)

IMAGE MITIGATION:
  Original: Photograph with visible faces
    ↓
  Strategy: [blur, pixelate, inpaint, overlay]
    ↓
  Result: Same image with faces blurred/pixelated/marked

AUDIO MITIGATION:
  Original: Audio with sensitive speech at timestamp 0:10-0:15
    ↓
  Strategy: [mute_segment, beep, voice_modulation]
    ↓
  Result: Audio with segment muted or beep inserted

VIDEO MITIGATION:
  Original: Video with sensitive frames
    ↓
  Strategy: Select mitigation for each frame (reuse image strategies)
    ↓
  Result: Video with specified frames modified

Output: Sanitized content artifact

                          ↓

EXPLAINABILITY & AUDIT PHASE
────────────────────────────────────────────────────────────────

[Explainability Module]
  1. Generate detailed detection report (text spans / image overlays)
  2. Document each mitigation action with before/after
  3. Create audit log entry (JSONL format) with:
     - Timestamp, execution ID
     - Detection details (type, confidence, location)
     - Mitigation strategy applied
     - Original vs. sanitized snippet
     - Output artifact path
  4. Calculate aggregate statistics:
     - Total entities detected per type
     - Mitigation actions applied
     - Processing time
  5. Generate compliance report (if required)

Output: 
  - .spans.txt file (text report)
  - .overlay.png file (image with boxes)
  - audit.log entry (JSONL)
  - Optional: Compliance report PDF

                          ↓

OUTPUT & STORAGE PHASE
────────────────────────────────────────────────────────────────

[Output Manager]
  1. Write sanitized content artifact:
     - Text: Save .sanitized.txt file
     - Image: Save .sanitized.png file
     - Audio: Save .sanitized.wav file
     - Video: Save .sanitized.mp4 file
  
  2. Write explainability artifacts:
     - Text span reports
     - Image overlays
     - Audit log entries

  3. Register in artifact repository:
     - Create artifact metadata
     - Log file paths for downstream retrieval

  4. Respond to client:
     - CLI: Print summary to console
     - API: Return JSON response with artifact paths and decisions

Artifact Output Structure:
  artifacts/
    ├── demo_email.sanitized.txt
    ├── demo_email.sanitized.spans.txt
    ├── demo_image.sanitized.png
    ├── demo_image.sanitized.overlay.png
    └── audit.log (JSONL format)
```

### 5.2 Data Storage and Processing Layers

**Ephemeral Storage (Runtime):**
- Original input content (in memory)
- Parse trees and token graphs (temporary Python objects)
- Detection results (JSON structures)
- Mitigation metadata (temporary state)

**Persistent Storage:**
- Configuration files: `config/leakwatch.yaml` (YAML)
- Sanitized artifacts: `artifacts/` directory
- Audit logs: `artifacts/audit.log` (JSONL)
- Explainability reports: Text spans, image overlays (various formats)

**Processing Pipeline:**
1. **Streaming Processing:** Text processed sequentially token-by-token
2. **Batch Processing:** Images processed with vectorized operations (NumPy)
3. **Asynchronous Processing:** Audio/video can be processed with background jobs (for future REST API optimization)

---

## 6. Technology Stack Justification

### 6.1 Core Framework and Utilities

| Technology | Version | Purpose | Justification |
|-----------|---------|---------|-----------------|
| **Python** | 3.10+ | Primary language | Industry standard for ML/NLP; rich ecosystem |
| **Pydantic** | 2.6+ | Data validation | Type-safe configuration and API schemas |
| **Typer** | 0.12+ | CLI framework | Modern, intuitive, minimal boilerplate |
| **PyYAML** | 6.0+ | Configuration management | Human-readable config format, widely supported |
| **Rich** | 13.7+ | Terminal output | Beautiful, colored console output for CLI |

**Justification:** These technologies provide a lightweight, maintainable foundation for the middleware with excellent developer experience and minimal dependencies.

---

### 6.2 NLP and Text Processing

| Technology | Version | Purpose | Justification |
|-----------|---------|---------|-----------------|
| **spaCy** | 3.7+ | NER and tokenization | Industry-leading NLP library; fast, accurate, memory-efficient |
| **en_core_web_sm** | Latest | English language model | Pre-trained NER for PII detection; covers PERSON, ORG, GPE, DATE |

**Justification:** spaCy is chosen over alternatives (NLTK, TextBlob) for:
- Production-grade performance
- Pre-trained models with good accuracy for NER
- Pipeline architecture allowing custom components
- Active maintenance and community support

---

### 6.3 Computer Vision and Image Processing

| Technology | Version | Purpose | Justification |
|-----------|---------|---------|-----------------|
| **OpenCV** | 4.9+ | Image processing | Industry standard for computer vision; optimized C++ backend |
| **OpenCV Haar Cascades** | Built-in | Face detection | Fast, real-time face detection; minimal GPU requirements |
| **EasyOCR** | 1.7+ | Optical Character Recognition | Supports 80+ languages; handles rotated/skewed text |
| **Pillow (PIL)** | 10.2+ | Image I/O and manipulation | Lightweight alternative to OpenCV for I/O operations |
| **NumPy** | 1.26+ | Numerical operations | Foundation for vectorized image processing |

**Justification:** 
- OpenCV provides robust, well-tested algorithms for face detection and image manipulation
- EasyOCR selected for superior language support and text orientation handling compared to Tesseract
- Combined with Pillow for cleaner I/O operations

---

### 6.4 API and Web Framework

| Technology | Version | Purpose | Justification |
|-----------|---------|---------|-----------------|
| **FastAPI** | 0.109+ | REST API framework | Modern, fast async framework with automatic OpenAPI documentation |
| **Uvicorn** | 0.25+ | ASGI server | Lightweight, async-capable, excellent performance |

**Justification:** FastAPI chosen over Flask/Django for:
- Native async support for I/O operations
- Automatic API documentation and validation
- Type hints integration with automatic OpenAPI schema generation
- Superior performance in benchmarks

---

### 6.5 Deployment and Containerization

| Technology | Purpose | Justification |
|---------|---------|-----------------|
| **Docker** | Containerization | Reproducible environments, easy CI/CD integration, cloud portability |
| **Docker Compose** | Multi-container orchestration | Manage application + dependencies (future: multiple service architecture) |

**Justification:** Docker ensures:
- Environment consistency across development, testing, production
- Easy onboarding for team members
- Simplified deployment to cloud platforms
- Reproducibility for academic evaluation

---

### 6.6 Testing and Quality Assurance

| Technology | Version | Purpose | Justification |
|-----------|---------|---------|-----------------|
| **pytest** | 8.2+ | Testing framework | De facto standard for Python; excellent plugin ecosystem |
| **pytest-cov** | 5.0+ | Code coverage measurement | Ensures comprehensive test coverage |
| **ruff** | 0.1+ | Linting and formatting | Fast, modern linter replacing flake8 and black |

**Justification:** pytest ecosystem provides comprehensive testing capabilities with minimal boilerplate, essential for ensuring system reliability in privacy-critical application.

---

## 7. Scalability & Performance Considerations

### 7.1 Performance Targets

| Operation | Target Latency | Throughput | Notes |
|-----------|---|---|---|
| Text analysis | < 100 ms/document | 10+ docs/sec | Single-threaded processing |
| Image analysis | < 500 ms/image | 2+ images/sec | Subject to image resolution |
| Audio analysis | Real-time (1x) | 1+ hours audio/hour | Depends on ASR service |
| Video analysis | 1-3x real-time | 0.3-1 hour video/hour | Frame sampling reduces latency |
| REST API response | < 1 second (P95) | 100+ RPS | Excludes network latency |

### 7.2 Scalability Strategies

#### 7.2.1 Single-Machine Optimization
- **Lazy Loading:** Models loaded only when needed (text models optional if image-only processing)
- **Caching:** Repeated detections cached in-memory (LRU cache)
- **Vectorization:** NumPy operations for batch image processing
- **Model Optimization:** Quantized spaCy models for smaller memory footprint

#### 7.2.2 Multi-Machine Scaling
- **Stateless Design:** Each API request independent, enabling horizontal scaling
- **Load Balancing:** REST API layer amenable to load balancer integration (nginx, AWS ALB)
- **Distributed Processing:** Batch jobs can be parallelized using job queues (Celery, Dask)
- **Artifact Caching:** Shared artifact storage (S3, NFS) for consistency across instances

#### 7.2.3 Database and Storage
- **Configuration:** File-based YAML (Phase 2); migrate to database (PostgreSQL) for Phase 3
- **Artifacts:** Filesystem storage for Phase 2; scale to S3/cloud storage for production
- **Audit Logs:** JSONL append-only format; migrate to time-series database (InfluxDB, Elasticsearch) for Phase 3+

### 7.3 Performance Bottlenecks and Mitigations

| Bottleneck | Impact | Mitigation Strategy |
|-----------|--------|-------------|
| NER model loading | First-request latency (500+ ms) | Cache in memory; pre-warm on service start |
| Image resizing | Large images (4K+) | Downscale before processing; async processing |
| OCR latency | Whole-document OCR | Selective OCR (only flagged regions); parallel processing |
| Audio ASR | Real-time factor 3-5x | Cloud ASR service (Google Speech-to-Text); async streaming |
| Concurrent requests | Memory per request | Connection pooling; streaming response bodies |

---

## 8. Security Considerations

### 8.1 Input Validation and Sanitization

**Threat:** Malicious input exploits vulnerabilities in detection models or PIL/OpenCV libraries

**Mitigations:**
- **File Type Validation:** Whitelist accepted formats; reject polyglot files
- **Size Limits:** Reject files exceeding threshold (images > 50MB, text > 10MB)
- **Format Verification:** Validate file headers match extension
- **Encoding Detection:** Enforce UTF-8 for text; detect and reject binary data in text fields
- **Sandboxing:** Run untrusted image processing in isolated process (future: separate container)

### 8.2 Sensitive Data Handling in Memory

**Threat:** Malicious actors recover original sensitive data from memory dumps or hibernation files

**Mitigations:**
- **Minimal Retention:** Overwrite sensitive data after processing
- **Secure Deletion:** Use `secrets` module for cryptographic operations; avoid Python string caching
- **Memory Locking:** Pin sensitive buffers in RAM (future: use `ctypes.mlock`)
- **No Logging of PII:** Audit logs contain entity types but not original PII values
- **Temporary Files:** Use `tempfile.TemporaryDirectory()` with automatic cleanup

### 8.3 Output Validation and Integrity

**Threat:** Mitigation produces artifacts containing undetected sensitive data

**Mitigations:**
- **Multi-Pass Detection:** Apply detection twice; second pass verifies sensitive data removed
- **Statistical Analysis:** Test sanitized content for remaining patterns matching original
- **Manual Verification:** Sample-based review for high-risk documents (credit card, SSN)
- **Audit Trail:** Comprehensive logging enables forensic analysis if breach suspected

### 8.4 Configuration Security

**Threat:** Misconfiguration disables critical security controls

**Mitigations:**
- **Default-Secure:** Configuration defaults to high sensitivity levels
- **Policy Validation:** Reject configurations that allow sensitive entities to pass unmitigated
- **Version Control:** Track all configuration changes with Git
- **Access Control:** Restrict configuration file modification to administrators

### 8.5 API Security

**Threat:** Unauthorized access to sensitive artifacts; API exploitation

**Mitigations:**
- **Authentication:** (Phase 3) OAuth2 or API key-based authentication
- **Authorization:** (Phase 3) Role-based access control (RBAC) for artifact retrieval
- **Rate Limiting:** Restrict requests per IP/user to prevent DoS
- **HTTPS Only:** (Production) Enforce TLS 1.3+ for all API communication
- **Input Validation:** Pydantic schema validation on all request bodies
- **CORS Restrictions:** Configure CORS headers to restrict cross-origin requests

### 8.6 Audit and Compliance

**Threat:** No record of sensitive data exposure; inability to demonstrate compliance

**Mitigations:**
- **Comprehensive Logging:** JSONL audit logs with timestamps and execution IDs
- **Log Integrity:** (Future) Cryptographic signing of audit logs
- **Retention Policy:** Comply with GDPR right-to-erasure (delete logs after retention period)
- **Data Minimization:** Log only essential information (not original sensitive data)
- **Immutable Archive:** (Future) Copy audit logs to write-once storage for compliance

---

## 9. Assumptions & Constraints

### 9.1 Assumptions

#### 9.1.1 Threat Model
- **Assumption:** System protects against accidental exposure (user uploads without realizing sensitivity)
- **Non-Assumption:** System does NOT protect against intentional adversarial input designed to bypass detection
- **Out-of-Scope:** Sophisticated adversarial attacks (FGSM, PGD) on detection models

#### 9.1.2 Data Characteristics
- **Assumption:** Input data is in common formats (TXT, JPG, PNG, WAV, MP4)
- **Assumption:** Text is in supported languages (primarily English in Phase 2)
- **Assumption:** Images are standard dimensions (not extreme aspect ratios or resolutions)
- **Non-Assumption:** Encrypted data or steganographic attacks

#### 9.1.3 Computational Resources
- **Assumption:** Processing runs on x86-64 systems with 4+ GB RAM
- **Assumption:** Single-threaded execution is acceptable for Phase 2 performance requirements
- **Non-Assumption:** GPU acceleration (future Phase 3)

#### 9.1.4 Regulatory Environment
- **Assumption:** System completes on-device processing (no cloud transmission of sensitive data)
- **Assumption:** Audit logs retained per organizational policy (GDPR 30-day default)
- **Non-Assumption:** System provides legal guarantee of compliance (legal review required per jurisdiction)

### 9.2 Constraints

#### 9.2.1 Technical Constraints
- **Constraint:** Phase 2 excludes GAN-based inpainting (deterministic blur/pixelation only)
- **Constraint:** Audio/video implemented as adapters, not full pipelines
- **Constraint:** No unsupervised learning or adaptive models (determinism critical for compliance)
- **Constraint:** Single-file processing only (no cross-document relationships)

#### 9.2.2 Model Constraints
- **Constraint:** spaCy `en_core_web_sm` model limited to predefined entity types (no custom NER training in Phase 2)
- **Constraint:** Face detection relies on Haar Cascades (no deep learning in Phase 2 for GPU independence)
- **Constraint:** OCR uses EasyOCR only (no Tesseract ensemble)

#### 9.2.3 Performance Constraints
- **Constraint:** No real-time streaming in Phase 2 (batch processing only)
- **Constraint:** No distributed processing (single-machine only)
- **Constraint:** Audio/video processing latency acceptable only for batch mode

#### 9.2.4 Data Constraints
- **Constraint:** Maximum input file sizes: 10 MB (text), 50 MB (images), 100 MB (audio/video)
- **Constraint:** Maximum image resolutions: 4K (3840x2160)
- **Constraint:** No persistent user data across requests (stateless design)

### 9.3 Risk Mitigation for Constraints

| Constraint | Risk | Mitigation |
|-----------|------|-----------|
| No GAN inpainting | Quality of sanitized images poor | Upgrade in Phase 3 with research validation |
| Deterministic models only | Detection accuracy lower than adaptive ML | Compensate with conservative confidence thresholds, human review |
| Single-machine only | Scalability limited | Document limitation in SLA; upgrade architecture in Phase 3 |
| English-only NER | International users unsupported | Extend spaCy models in Phase 3; support multi-language |

---

## 10. Future Enhancements

### 10.1 Phase 3 Enhancements (Planned)

#### 10.1.1 Advanced Mitigation
- **GAN-Based Inpainting:** Realistic image reconstruction using Pix2Pix or CycleGAN
- **Voice Synthesis:** Replace sensitive speech with synthesized replica (maintaining acoustic characteristics)
- **Diffusion Models:** High-quality image inpainting using stable diffusion

#### 10.1.2 Advanced Detection
- **Graph Neural Networks (GraphSAGE):** Context-aware entity detection using token relationship graphs
- **Multi-Modal Models:** CLIP-based cross-modal understanding (text + image semantics)
- **Domain-Specific Models:** Fine-tuned models for medical records, legal documents, financial data

#### 10.1.3 Real-Time Streaming
- **Streaming Audio:** Process audio chunks as they arrive (latency: < 2 seconds behind real-time)
- **Video Stream Processing:** Real-time video frame processing with minimal buffering
- **WebSocket API:** Bidirectional streaming for live content moderation

#### 10.1.4 Platform Integration
- **Social Media APIs:** Native integration with Facebook, Twitter, Instagram detection and takedown
- **Cloud Provider SDKs:** AWS S3 triggers, Azure Blob Storage integration
- **Message Queue Integration:** Kafka/RabbitMQ for asynchronous processing pipelines

### 10.2 Phase 4+ Enhancements (Long-Term Vision)

#### 10.2.1 Machine Learning Improvements
- **Transfer Learning:** Fine-tune detection models on domain-specific data (medical, legal, financial)
- **Federated Learning:** Train models on decentralized data without centralizing sensitive information
- **Adversarial Robustness:** Develop detection models resistant to adversarial examples

#### 10.2.2 Explainability Enhancements
- **SHAP/LIME Analysis:** Interpret why each detection decision was made
- **Interactive Dashboards:** Visualize detection patterns and trends
- **Counterfactual Explanations:** Show what would need to change for detection threshold to flip

#### 10.2.3 Regulatory Compliance
- **Formal Verification:** Prove properties of algorithm satisfy GDPR/CCPA requirements
- **Certified Deletion:** Cryptographic proof that sensitive data was irreversibly deleted
- **Privacy Impact Assessment (PIA):** Automated compliance report generation

#### 10.2.4 Enterprise Features
- **Fine-Grained Access Control:** Role-based and attribute-based access control
- **Multi-Tenancy:** Support for multiple organizations with isolated data
- **Custom Detection Rules:** Domain-specific rule builder (UI-based design)
- **Webhooks and Callbacks:** Trigger downstream actions on detection events

### 10.3 Research Directions

#### 10.3.1 Adversarial Robustness
Investigate:
- Detection model robustness against intentional evasion attacks
- Evaluation metrics beyond accuracy (robustness, fairness, privacy)
- Adversarial training techniques applicable to privacy detection

#### 10.3.2 Fairness in Privacy
Research:
- Disparate impact of detection algorithms (e.g., higher false negatives for non-English text)
- Equity of protection across demographic groups
- Bias mitigation in NLP and computer vision models

#### 10.3.3 Synthetic Data Generation
Explore:
- Generation of realistic but fake PII for testing
- Controlled evaluation of detection accuracy
- Quality assessment of mitigation strategies

---

## 11. Conclusion

LeakWatch implements a **comprehensive, modular, and extensible privacy-preserving middleware** suitable for deployment in AI systems and social platforms. The Phase 2 architecture establishes a solid foundation with full support for text and image modalities, clear separation of concerns, and deterministic algorithms ensuring reproducibility and transparency.

**Key Architectural Strengths:**
- ✅ **Non-Invasive:** Operates as independent middleware
- ✅ **Multi-Modal:** Unified framework for text, image, audio, video
- ✅ **Transparent:** Comprehensive audit trails and explainability artifacts
- ✅ **Compliant:** Built-in support for GDPR and CCPA requirements
- ✅ **Extensible:** Modular design enables easy addition of new detection/mitigation strategies
- ✅ **Maintainable:** Clear interfaces, well-structured code, comprehensive documentation

The system successfully balances phase 2 feasibility with long-term roadmap for advanced capabilities, positioning the project for successful evaluation and future industry adoption.

---

## Appendix: Referenced Configuration File

**Location:** `config/leakwatch.yaml`

```yaml
# LeakWatch Configuration File
# Phase 2 - Production Settings

detection:
  text:
    enabled: true
    models:
      ner_model: "en_core_web_sm"
      use_regex_rules: true
      
    entities_to_detect:
      - "PERSON"
      - "ORG"
      - "GPE"
      - "DATE"
      - "EMAIL"
      - "PHONE_NUMBER"
      - "CREDIT_CARD"
      - "SSN"
      
    sensitivity_levels:
      PERSON: "high"
      EMAIL: "high"
      CREDIT_CARD: "critical"
      SSN: "critical"
      
    confidence_threshold: 0.70

  image:
    enabled: true
    models:
      face_detection: "haar_cascade"
      ocr_engine: "easyocr"
      
    detect_types:
      - "FACE"
      - "LICENSE_PLATE"
      - "DOCUMENT_TEXT"
      
    confidence_threshold: 0.80

  audio:
    enabled: false
    models:
      asr_model: "future_whisper"
      
  video:
    enabled: false
    frame_sampling_rate: 0.10  # Sample 10% of frames

mitigation:
  text:
    default_strategy: "masking"  # [masking, redaction, replacement]
    mask_token: "[REDACTED]"
    strategies:
      masking:
        token: "[REDACTED]"
      redaction:
        replace_with: ""
        preserve_length: false
      replacement:
        use_synthetic: false
        
  image:
    default_strategy: "blur"  # [blur, pixelate, overlay]
    strategies:
      blur:
        kernel_size: 21
        strength: 1.0
      pixelate:
        block_size: 16
      overlay:
        color: [0, 0, 0]
        transparency: 0.8

policy:
  # Block requests if these entities detected above threshold
  block_on_detections:
    - "CREDIT_CARD"
    - "SSN"
    
  # Always allow these (whitelist)
  always_allow: []
  
  # Risk scoring
  block_if_risk_score_exceeds: 0.85
  
  # PII threshold
  max_pii_entities_allowed: 5

output:
  artifact_directory: "artifacts/"
  
  generate_artifacts:
    sanitized_content: true
    text_span_report: true
    image_overlay: true
    audit_log: true
    
  audit_log_format: "jsonl"  # [json, jsonl, csv]

logging:
  level: "INFO"  # [DEBUG, INFO, WARNING, ERROR]
  output_targets:
    - "console"
    # - "file"
  file_path: "logs/leakwatch.log"
  
services:
  api:
    enabled: true
    host: "127.0.0.1"
    port: 8000
    
  cli:
    enabled: true
```

---

**Document Prepared By:** AI Architecture Team

**Status:** For Academic Evaluation

**Confidentiality:** Internal Use

