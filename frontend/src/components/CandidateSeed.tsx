import { useRef, useState } from "react";
import {
  Database,
  FileJson,
  Plus,
  Trash2,
  Upload,
  UserPlus,
  X,
} from "lucide-react";

import type { CandidateSeedRecord } from "../types";

type CandidateSeedProps = {
  candidates: CandidateSeedRecord[];
  onChange: (candidates: CandidateSeedRecord[]) => void;
};

type FormState = {
  full_name: string;
  headline: string;
  location: string;
  work_mode_preferences: string;
  years_experience: string;
  current_title: string;
  current_company: string;
  skills: string;
  domain_experience: string;
  summary: string;
  persona: CandidateSeedRecord["persona"];
  availability_days: string;
  compensation_expectation_lpa: string;
  engagement_status: CandidateSeedRecord["engagement_status"];
};

const PERSONAS: CandidateSeedRecord["persona"][] = [
  "actively_looking",
  "passively_open",
  "compensation_sensitive",
  "location_constrained",
  "currently_unavailable",
];

const ENGAGEMENTS: CandidateSeedRecord["engagement_status"][] = [
  "active",
  "passive",
  "unavailable",
];

const emptyForm: FormState = {
  full_name: "",
  headline: "",
  location: "",
  work_mode_preferences: "remote",
  years_experience: "",
  current_title: "",
  current_company: "",
  skills: "",
  domain_experience: "",
  summary: "",
  persona: "passively_open",
  availability_days: "30",
  compensation_expectation_lpa: "",
  engagement_status: "passive",
};

const sampleJson = `[
  {
    "full_name": "Aditi Rao",
    "headline": "Senior AI backend engineer building production RAG systems",
    "location": "Bengaluru, India",
    "work_mode_preferences": ["remote", "hybrid"],
    "years_experience": 7,
    "current_title": "Senior AI Engineer",
    "current_company": "VectorTrail",
    "skills": ["Python", "FastAPI", "LLMs", "RAG", "pgvector"],
    "domain_experience": ["SaaS", "developer tools"],
    "summary": "Owns backend architecture for retrieval systems.",
    "persona": "passively_open",
    "availability_days": 30,
    "compensation_expectation_lpa": 38,
    "engagement_status": "passive"
  }
]`;

function splitList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function normalizeWorkModes(value: unknown): CandidateSeedRecord["work_mode_preferences"] {
  const allowed = new Set(["remote", "hybrid", "onsite"]);
  const rawValues = Array.isArray(value)
    ? value.map(String)
    : typeof value === "string"
      ? splitList(value)
      : [];

  const normalized = rawValues
    .map((item) => item.toLowerCase())
    .filter(
      (item): item is CandidateSeedRecord["work_mode_preferences"][number] =>
        allowed.has(item),
    );

  return normalized.length > 0 ? normalized : ["remote"];
}

function normalizeCandidate(raw: Record<string, unknown>, index: number): CandidateSeedRecord {
  const personas = new Set(PERSONAS);
  const engagements = new Set(ENGAGEMENTS);
  const persona = String(raw.persona ?? "passively_open") as CandidateSeedRecord["persona"];
  const engagement = String(
    raw.engagement_status ?? "passive",
  ) as CandidateSeedRecord["engagement_status"];

  return {
    id:
      typeof raw.id === "string" && raw.id.trim().length > 0
        ? raw.id
        : `custom_${Date.now()}_${index}`,
    full_name: String(raw.full_name ?? "").trim(),
    headline: String(raw.headline ?? "").trim(),
    location: String(raw.location ?? "").trim(),
    work_mode_preferences: normalizeWorkModes(raw.work_mode_preferences),
    years_experience: Number(raw.years_experience ?? 0),
    current_title: String(raw.current_title ?? "").trim(),
    current_company: String(raw.current_company ?? "").trim(),
    skills: Array.isArray(raw.skills)
      ? raw.skills.map(String).map((item) => item.trim()).filter(Boolean)
      : splitList(String(raw.skills ?? "")),
    domain_experience: Array.isArray(raw.domain_experience)
      ? raw.domain_experience.map(String).map((item) => item.trim()).filter(Boolean)
      : splitList(String(raw.domain_experience ?? "")),
    summary: String(raw.summary ?? "").trim(),
    persona: personas.has(persona) ? persona : "passively_open",
    availability_days: Number(raw.availability_days ?? 30),
    compensation_expectation_lpa: Number(raw.compensation_expectation_lpa ?? 0),
    engagement_status: engagements.has(engagement) ? engagement : "passive",
  };
}

export function CandidateSeed({ candidates, onChange }: CandidateSeedProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"form" | "bulk">("form");
  const [form, setForm] = useState<FormState>(emptyForm);
  const [jsonError, setJsonError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  function addFromForm() {
    if (!form.full_name.trim() || !form.current_title.trim()) {
      return;
    }

    const next = normalizeCandidate(
      {
        ...form,
        years_experience: Number(form.years_experience || 0),
        availability_days: Number(form.availability_days || 30),
        compensation_expectation_lpa: Number(form.compensation_expectation_lpa || 0),
      },
      candidates.length,
    );

    onChange([...candidates, next]);
    setForm(emptyForm);
  }

  async function importJsonFile(file: File) {
    setJsonError(null);

    try {
      const parsed = JSON.parse(await file.text());
      const items = Array.isArray(parsed) ? parsed : [parsed];
      const next = items.map((item, index) =>
        normalizeCandidate(item as Record<string, unknown>, candidates.length + index),
      );
      onChange([...candidates, ...next]);
    } catch (error) {
      setJsonError(error instanceof Error ? error.message : "Invalid JSON file.");
    }
  }

  function removeCandidate(candidateId: string) {
    onChange(candidates.filter((candidate) => candidate.id !== candidateId));
  }

  if (!isOpen) {
    return (
      <button
        className="mt-4 flex w-full items-center justify-between rounded-xl border border-dashed border-border bg-card px-4 py-3 text-left transition hover:border-primary/50 hover:bg-card"
        onClick={() => setIsOpen(true)}
        type="button"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-secondary">
            <Database className="h-4 w-4 text-muted-foreground" />
          </div>
          <div>
            <div className="text-sm font-medium">Candidate pool</div>
            <div className="text-xs text-muted-foreground">
              {candidates.length > 0
                ? `${candidates.length} custom candidate(s) added`
                : "Using built-in sample data — click to add your own"}
            </div>
          </div>
        </div>
        <Plus className="h-4 w-4 text-muted-foreground" />
      </button>
    );
  }

  return (
    <div className="mt-4 overflow-hidden rounded-2xl border border-border/60 bg-card shadow-card">
      <div className="flex items-center justify-between border-b border-border/60 px-4 py-3">
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium">Candidate pool</span>
          <span className="text-xs text-muted-foreground">
            {candidates.length > 0 ? `${candidates.length} custom` : "defaults will be used"}
          </span>
        </div>
        <button
          className="text-muted-foreground transition hover:text-foreground"
          onClick={() => setIsOpen(false)}
          type="button"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="px-4 pt-4">
        <div className="grid grid-cols-2 gap-2 rounded-lg bg-secondary p-1">
          <button
            className={`inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 text-xs font-medium transition ${
              activeTab === "form" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground"
            }`}
            onClick={() => setActiveTab("form")}
            type="button"
          >
            <UserPlus className="h-3.5 w-3.5" />
            Add one
          </button>
          <button
            className={`inline-flex items-center justify-center gap-2 rounded-md px-3 py-2 text-xs font-medium transition ${
              activeTab === "bulk" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground"
            }`}
            onClick={() => setActiveTab("bulk")}
            type="button"
          >
            <FileJson className="h-3.5 w-3.5" />
            Bulk JSON
          </button>
        </div>
      </div>

      {activeTab === "form" ? (
        <div className="space-y-3 p-4">
          <p className="text-xs text-muted-foreground">
            These profiles will be sent to the scoring pipeline instead of the built-in sample set.
          </p>

          <div className="grid grid-cols-2 gap-3">
            <InputField
              label="Full name *"
              placeholder="Aditi Rao"
              value={form.full_name}
              onChange={(value) => setForm({ ...form, full_name: value })}
            />
            <InputField
              label="Location"
              placeholder="Bengaluru, India"
              value={form.location}
              onChange={(value) => setForm({ ...form, location: value })}
            />
          </div>
          <InputField
            label="Headline"
            placeholder="Senior AI backend engineer building production RAG systems"
            value={form.headline}
            onChange={(value) => setForm({ ...form, headline: value })}
          />
          <div className="grid grid-cols-2 gap-3">
            <InputField
              label="Current title *"
              placeholder="Senior AI Engineer"
              value={form.current_title}
              onChange={(value) => setForm({ ...form, current_title: value })}
            />
            <InputField
              label="Current company"
              placeholder="VectorTrail"
              value={form.current_company}
              onChange={(value) => setForm({ ...form, current_company: value })}
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <InputField
              label="Years exp."
              placeholder="7"
              type="number"
              value={form.years_experience}
              onChange={(value) => setForm({ ...form, years_experience: value })}
            />
            <InputField
              label="Avail. (days)"
              placeholder="30"
              type="number"
              value={form.availability_days}
              onChange={(value) => setForm({ ...form, availability_days: value })}
            />
            <InputField
              label="Comp. (LPA)"
              placeholder="38"
              type="number"
              value={form.compensation_expectation_lpa}
              onChange={(value) =>
                setForm({ ...form, compensation_expectation_lpa: value })
              }
            />
          </div>
          <InputField
            label="Skills (comma-separated)"
            placeholder="Python, FastAPI, LLMs, RAG"
            value={form.skills}
            onChange={(value) => setForm({ ...form, skills: value })}
          />
          <InputField
            label="Domain experience (comma-separated)"
            placeholder="SaaS, developer tools"
            value={form.domain_experience}
            onChange={(value) => setForm({ ...form, domain_experience: value })}
          />
          <InputField
            label="Work mode preferences (comma-separated)"
            placeholder="remote, hybrid"
            value={form.work_mode_preferences}
            onChange={(value) => setForm({ ...form, work_mode_preferences: value })}
          />

          <div className="grid grid-cols-2 gap-3">
            <SelectField
              label="Persona"
              options={PERSONAS}
              value={form.persona}
              onChange={(value) =>
                setForm({ ...form, persona: value as CandidateSeedRecord["persona"] })
              }
            />
            <SelectField
              label="Engagement status"
              options={ENGAGEMENTS}
              value={form.engagement_status}
              onChange={(value) =>
                setForm({
                  ...form,
                  engagement_status: value as CandidateSeedRecord["engagement_status"],
                })
              }
            />
          </div>

          <TextAreaField
            label="Summary"
            placeholder="Owns backend architecture for retrieval systems..."
            value={form.summary}
            onChange={(value) => setForm({ ...form, summary: value })}
          />

          <button
            className="inline-flex w-full items-center justify-center rounded-lg bg-secondary px-4 py-2.5 text-sm font-semibold text-secondary-foreground transition hover:bg-secondary/80"
            onClick={addFromForm}
            type="button"
          >
            <Plus className="mr-2 h-4 w-4" />
            Add candidate
          </button>
        </div>
      ) : (
        <div className="space-y-3 p-4">
          <button
            className="block w-full rounded-lg border border-dashed border-border p-6 text-center transition hover:border-primary/50 hover:bg-secondary/30"
            onClick={() => fileInputRef.current?.click()}
            type="button"
          >
            <Upload className="mx-auto mb-2 h-6 w-6 text-muted-foreground" />
            <div className="text-sm font-medium">Click to upload JSON</div>
            <div className="mt-1 text-xs text-muted-foreground">
              Array of candidate profiles to score against the JD
            </div>
          </button>
          <input
            accept=".json,application/json"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];

              if (file) {
                void importJsonFile(file);
              }

              event.target.value = "";
            }}
            ref={fileInputRef}
            type="file"
          />
          {jsonError ? <p className="text-xs text-red-600">{jsonError}</p> : null}
          <details className="text-xs">
            <summary className="cursor-pointer text-muted-foreground transition hover:text-foreground">
              Example format
            </summary>
            <pre className="mt-2 overflow-x-auto rounded-lg bg-secondary p-3 text-[11px]">
              {sampleJson}
            </pre>
          </details>
        </div>
      )}

      {candidates.length > 0 ? (
        <div className="space-y-2 border-t border-border/60 p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">
              Custom pool ({candidates.length})
            </span>
            <button
              className="text-xs text-muted-foreground transition hover:text-red-600"
              onClick={() => onChange([])}
              type="button"
            >
              Clear all
            </button>
          </div>
          <div className="max-h-40 space-y-1.5 overflow-y-auto">
            {candidates.map((candidate) => (
              <div
                className="flex items-center justify-between rounded-lg bg-secondary/50 px-3 py-2 text-sm"
                key={candidate.id}
              >
                <div className="min-w-0 flex-1">
                  <div className="truncate font-medium">{candidate.full_name}</div>
                  <div className="truncate text-xs text-muted-foreground">
                    {candidate.current_title}
                    {candidate.current_company ? ` @ ${candidate.current_company}` : ""}
                  </div>
                </div>
                <button
                  className="ml-2 p-1 text-muted-foreground transition hover:text-red-600"
                  onClick={() => removeCandidate(candidate.id)}
                  type="button"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function InputField({
  label,
  onChange,
  placeholder,
  type = "text",
  value,
}: {
  label: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
  value: string;
}) {
  return (
    <label className="space-y-1.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <input
        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none ring-0 transition focus:border-ring"
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        type={type}
        value={value}
      />
    </label>
  );
}

function SelectField({
  label,
  onChange,
  options,
  value,
}: {
  label: string;
  onChange: (value: string) => void;
  options: string[];
  value: string;
}) {
  return (
    <label className="space-y-1.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <select
        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none ring-0 transition focus:border-ring"
        onChange={(event) => onChange(event.target.value)}
        value={value}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option.replace(/_/g, " ")}
          </option>
        ))}
      </select>
    </label>
  );
}

function TextAreaField({
  label,
  onChange,
  placeholder,
  value,
}: {
  label: string;
  onChange: (value: string) => void;
  placeholder?: string;
  value: string;
}) {
  return (
    <label className="space-y-1.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <textarea
        className="min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none ring-0 transition focus:border-ring"
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        value={value}
      />
    </label>
  );
}
