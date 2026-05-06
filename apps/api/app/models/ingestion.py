from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ProcessingStatus(StrEnum):
    uploaded = "uploaded"
    parsing = "parsing"
    parsed = "parsed"
    failed = "failed"


class SourceType(StrEnum):
    employee_handbook = "employee_handbook"
    benefits_guide = "benefits_guide"
    pto_leave_policy = "pto_leave_policy"
    onboarding_doc = "onboarding_doc"
    offboarding_checklist = "offboarding_checklist"
    payroll_faq = "payroll_faq"
    hr_ticket_export = "hr_ticket_export"
    hr_channel_export = "hr_channel_export"
    internal_wiki = "internal_wiki"
    other = "other"


class HRDomain(StrEnum):
    onboarding = "onboarding"
    benefits = "benefits"
    pto_leave = "pto_leave"
    payroll = "payroll"
    compliance = "compliance"
    offboarding = "offboarding"
    employee_records = "employee_records"
    policy_faq = "policy_faq"
    unknown = "unknown"


class SensitivityLabel(StrEnum):
    none = "none"
    pii = "pii"
    compensation = "compensation"
    medical_leave = "medical_leave"
    employee_relations = "employee_relations"


class SourceDocument(BaseModel):
    id: str
    title: str
    original_filename: str
    source_type: SourceType = SourceType.other
    content_type: str | None = None
    storage_path: str
    processing_status: ProcessingStatus = ProcessingStatus.uploaded
    uploaded_by: str | None = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: datetime | None = None
    error_message: str | None = None
    chunk_count: int = 0
    detected_domains: list[HRDomain] = Field(default_factory=list)
    sensitivity_labels: list[SensitivityLabel] = Field(default_factory=list)


class DocumentChunk(BaseModel):
    id: str
    source_document_id: str
    source_title: str
    chunk_index: int
    content: str
    section_title: str | None = None
    start_char: int = 0
    end_char: int = 0
    hr_domain: HRDomain = HRDomain.unknown
    risk_level: str = "low"
    sensitivity_label: SensitivityLabel = SensitivityLabel.none
    citation_label: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SourceDocumentDetail(SourceDocument):
    chunks: list[DocumentChunk] = Field(default_factory=list)


class IngestionSummary(BaseModel):
    source_count: int
    chunk_count: int
    parsed_count: int
    failed_count: int
    supported_file_types: list[str]
