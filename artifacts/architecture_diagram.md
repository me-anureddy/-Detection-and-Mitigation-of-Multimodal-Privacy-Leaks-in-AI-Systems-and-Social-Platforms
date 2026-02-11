# LeakWatch Architecture Diagram

This diagram shows the complete end-to-end architecture of the LeakWatch system.

```mermaid
graph TB
    subgraph Input["🔌 INPUT LAYER"]
        CLI["CLI Interface<br/>(Typer)"]
        REST["REST API<br/>(FastAPI)"]
        Batch["Batch Processing"]
    end
    
    subgraph Preprocess["<br/>⚙️ PRE-PROCESSING LAYER<br/>"]
        TypeDetect["Content Type Detection"]
        Validate["Format Validation"]
        Normalize["Normalization & Encoding"]
        SizeCheck["Size/Dimension Checks"]
    end
    
    subgraph Detection["<br/>🔍 DETECTION LAYER<br/>"]
        TextMod["📝 Text Module<br/>NER • Rules • Tokenization"]
        ImgMod["🖼️ Image Module<br/>Face Detection • OCR • BBox"]
        AudioAdp["🎵 Audio Adapter<br/>ASR → Text Reuse"]
        VideoAdp["🎬 Video Adapter<br/>Frame Extract → Image Reuse"]
    end
    
    UnifiedOutput["<br/>📊 UNIFIED DETECTION OUTPUT<br/>Type • Location • Confidence • Metadata<br/>"]
    
    subgraph Orchestration["<br/>🎯 ORCHESTRATION LAYER<br/>"]
        PipelineMgr["Pipeline Manager"]
        PolicyEngine["Policy Engine"]
        RiskAssess["Risk Assessment"]
        Router["Routing Logic"]
    end
    
    subgraph Mitigation["<br/>🛡️ MITIGATION STRATEGIES<br/>"]
        TextMit["📝 Text: Mask • Redact<br/>Replace • Synthesize"]
        ImgMit["🖼️ Image: Blur • Pixelate<br/>Inpaint • Overlay"]
        AudioMit["🎵 Audio: Mute • Beep<br/>Voice Modulation"]
        VideoMit["🎬 Video: Frame Blur<br/>Feature Strip"]
    end
    
    subgraph Explain["<br/>📋 EXPLAINABILITY & AUDIT<br/>"]
        VisualArt["Visual Artifacts<br/>(Overlays, Heatmaps)"]
        TextReport["Text Reports<br/>(Spans, Before/After)"]
        AuditLog["Audit Logs<br/>(JSONL Format)"]
        ComplianceRpt["Compliance Reports<br/>(GDPR, CCPA)"]
    end
    
    subgraph Output["<br/>✅ OUTPUT LAYER<br/>"]
        Sanitized["Sanitized Content"]
        Metadata["Metadata & Stats"]
        Decision["Policy Decision<br/>ALLOW/BLOCK"]
    end
    
    subgraph Downstream["<br/>🚀 DOWNSTREAM SYSTEMS<br/>"]
        AISystem["AI/ML Systems"]
        SocialPlatforms["Social Platforms"]
        Analytics["Analytics Systems"]
    end
    
    CLI --> TypeDetect
    REST --> TypeDetect
    Batch --> TypeDetect
    
    TypeDetect --> Validate
    Validate --> Normalize
    Normalize --> SizeCheck
    
    SizeCheck --> TextMod
    SizeCheck --> ImgMod
    SizeCheck --> AudioAdp
    SizeCheck --> VideoAdp
    
    TextMod --> UnifiedOutput
    ImgMod --> UnifiedOutput
    AudioAdp --> UnifiedOutput
    VideoAdp --> UnifiedOutput
    
    UnifiedOutput --> PipelineMgr
    PipelineMgr --> PolicyEngine
    PolicyEngine --> RiskAssess
    RiskAssess --> Router
    
    Router --> TextMit
    Router --> ImgMit
    Router --> AudioMit
    Router --> VideoMit
    
    TextMit --> VisualArt
    ImgMit --> VisualArt
    AudioMit --> TextReport
    VideoMit --> TextReport
    
    VisualArt --> AuditLog
    TextReport --> AuditLog
    AuditLog --> ComplianceRpt
    
    ComplianceRpt --> Sanitized
    ComplianceRpt --> Metadata
    ComplianceRpt --> Decision
    
    Sanitized --> AISystem
    Metadata --> SocialPlatforms
    Decision --> Analytics
    
    style Input fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Preprocess fill:#7B68EE,stroke:#5A4BA8,color:#fff
    style Detection fill:#50C878,stroke:#3A9B5C,color:#fff
    style Orchestration fill:#FF6B6B,stroke:#CC5555,color:#fff
    style Mitigation fill:#FFA500,stroke:#CC8400,color:#fff
    style Explain fill:#1E90FF,stroke:#1566B2,color:#fff
    style Output fill:#2ECC71,stroke:#229954,color:#fff
    style Downstream fill:#95E1D3,stroke:#6FA8A1,color:#000
```

## How to Use

1. **View Online**: Copy the Mermaid code and paste it at [Mermaid Live Editor](https://mermaid.live)
2. **GitHub**: Include directly in GitHub markdown files
3. **Documentation**: Add to your documentation tools that support Mermaid (Obsidian, Notion, etc.)
4. **Export**: Use Mermaid Live Editor to export as PNG or SVG
