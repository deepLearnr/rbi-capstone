from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DocumentProfile:
    source_file: str
    title: str
    document_type: str
    rbi_reference: str | None
    publication_date: date | None
    department: str | None
    language: str = "en"
    description: str | None = None
    chunker: str = "generic"
    regulatory_status: str | None = None


DOCUMENT_PROFILES = {
    "ucb_cyber_security_framework.pdf": DocumentProfile(
        source_file="ucb_cyber_security_framework.pdf",
        title=(
            "Comprehensive Cyber Security Framework for Primary "
            "(Urban) Cooperative Banks (UCBs) – A Graded Approach"
        ),
        document_type="circular",
        rbi_reference="RBI/2019-20/129",
        publication_date=date(2019, 12, 31),
        department="Department of Supervision",
        description=(
            "RBI circular dated 31 December 2019. "
            "The supplied PDF is marked Withdrawn; retain as historical "
            "material and do not present as currently applicable guidance."
        ),
        chunker="ucb_cyber",
        regulatory_status="withdrawn",
    ),
}
