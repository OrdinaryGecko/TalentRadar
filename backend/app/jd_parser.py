import re

from app.models import (
    JobParseResponse,
    JobParseSignal,
    JobRequirement,
    WorkMode,
)

REQUIRED_SECTION_HEADERS = (
    "requirements",
    "must have",
    "must-have",
    "what we're looking for",
    "what you will need",
    "responsibilities",
)

PREFERRED_SECTION_HEADERS = (
    "nice to have",
    "nice-to-have",
    "preferred",
    "bonus",
    "good to have",
)


class JobDescriptionParser:
    def parse(self, raw_description: str) -> JobParseResponse:
        normalized_text = self._normalize_text(raw_description)
        title = self._extract_title(raw_description)
        seniority = self._extract_labeled_value(raw_description, "seniority")
        years_experience = self._extract_years_experience(normalized_text)
        location = self._extract_location(raw_description)
        work_mode = self._extract_work_mode(normalized_text)
        required_capabilities = self._extract_section_items(
            raw_description,
            REQUIRED_SECTION_HEADERS,
        )
        preferred_capabilities = self._extract_section_items(
            raw_description,
            PREFERRED_SECTION_HEADERS,
        )

        signals = [
            JobParseSignal(section="title", value=title),
            JobParseSignal(
                section="experience",
                value=f"{years_experience}+ years",
            ),
            JobParseSignal(section="location", value=location),
            JobParseSignal(section="work_mode", value=work_mode.value),
        ]

        if seniority is not None:
            signals.append(JobParseSignal(section="seniority", value=seniority))

        for capability in required_capabilities:
            signals.append(
                JobParseSignal(section="required_capability", value=capability)
            )

        for capability in preferred_capabilities:
            signals.append(
                JobParseSignal(section="preferred_capability", value=capability)
            )

        return JobParseResponse(
            title=title,
            normalized_requirement=JobRequirement(
                role=title,
                seniority=seniority,
                required_capabilities=required_capabilities,
                preferred_capabilities=preferred_capabilities,
                minimum_years_experience=years_experience,
                location=location,
                work_mode=work_mode,
            ),
            signals=signals,
        )

    def _normalize_text(self, raw_description: str) -> str:
        lowered = raw_description.lower()
        lowered = lowered.replace("/", " ")
        lowered = re.sub(r"\s+", " ", lowered)

        return lowered.strip()

    def _extract_title(self, raw_description: str) -> str:
        first_line = raw_description.strip().splitlines()[0].strip(" :-")

        if first_line:
            return first_line

        return "Unknown Role"

    def _extract_years_experience(self, normalized_text: str) -> int:
        matched = re.search(r"(\d+)\s*\+?\s*(?:years|yrs)", normalized_text)

        if matched:
            return int(matched.group(1))

        return 3

    def _extract_location(self, raw_description: str) -> str:
        labeled_value = self._extract_labeled_value(raw_description, "location")

        if labeled_value is not None:
            return labeled_value

        if "india" in raw_description.lower():
            return "India"

        return "Unspecified"

    def _extract_work_mode(self, normalized_text: str) -> WorkMode:
        explicit_mode = self._extract_work_mode_label(normalized_text)

        if explicit_mode is not None:
            return explicit_mode

        if "hybrid" in normalized_text:
            return WorkMode.HYBRID

        if "onsite" in normalized_text or "on-site" in normalized_text:
            return WorkMode.ONSITE

        return WorkMode.REMOTE

    def _extract_labeled_value(
        self,
        raw_description: str,
        label: str,
    ) -> str | None:
        pattern = re.compile(
            rf"^\s*{re.escape(label)}\s*:\s*(.+)$",
            flags=re.IGNORECASE | re.MULTILINE,
        )
        matched = pattern.search(raw_description)

        if matched is None:
            return None

        return matched.group(1).strip()

    def _extract_work_mode_label(self, normalized_text: str) -> WorkMode | None:
        matched = re.search(r"work mode\s*:\s*([a-z-]+)", normalized_text)

        if matched is None:
            return None

        candidate_value = matched.group(1).replace("-", "")

        if candidate_value == "hybrid":
            return WorkMode.HYBRID

        if candidate_value == "onsite":
            return WorkMode.ONSITE

        if candidate_value == "remote":
            return WorkMode.REMOTE

        return None

    def _extract_section_items(
        self,
        raw_description: str,
        headers: tuple[str, ...],
    ) -> list[str]:
        lines = raw_description.splitlines()
        capture = False
        items: list[str] = []

        for line in lines:
            stripped = line.strip()
            lowered = stripped.lower().rstrip(":")

            if any(header == lowered for header in headers):
                capture = True
                continue

            if capture and stripped.endswith(":") and lowered not in headers:
                break

            if capture:
                item = self._normalize_requirement_line(stripped)

                if item and item not in items:
                    items.append(item)

        return items

    def _normalize_requirement_line(self, value: str) -> str | None:
        cleaned = re.sub(r"^[\-\*\u2022]+\s*", "", value).strip()

        if not cleaned:
            return None

        if re.search(r"\b\d+\s*\+?\s*(?:years|yrs)\b", cleaned, flags=re.IGNORECASE):
            return None

        return re.sub(r"\s+", " ", cleaned)
