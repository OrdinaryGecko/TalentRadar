export type TranscriptTurn = {
  speaker: "recruiter" | "candidate";
  message: string;
  turn_index: number;
};

export type CandidateSeedRecord = {
  id: string;
  full_name: string;
  headline: string;
  location: string;
  work_mode_preferences: Array<"remote" | "hybrid" | "onsite">;
  years_experience: number;
  current_title: string;
  current_company: string;
  skills: string[];
  domain_experience: string[];
  summary: string;
  persona:
    | "actively_looking"
    | "passively_open"
    | "compensation_sensitive"
    | "location_constrained"
    | "currently_unavailable";
  availability_days: number;
  compensation_expectation_lpa: number;
  engagement_status: "active" | "passive" | "unavailable";
};

export type ConversationRecord = {
  simulation_index: number;
  provider: string;
  generation_mode: string;
  transcript: TranscriptTurn[];
};

export type CandidateRecord = {
  candidate: {
    id: string;
    full_name: string;
    headline: string;
    current_company: string;
    current_title: string;
    location: string;
    skills?: string[];
  };
  base_match_score: number;
  match_score: number;
  match_adjustment: number;
  interest_score: number;
  combined_score: number;
  explanation: {
    summary: string;
    strengths: string[];
    concerns: string[];
    matched_capabilities: string[];
    missing_capabilities: string[];
    matched_preferred_capabilities: string[];
    missing_preferred_capabilities: string[];
    provider: string;
    generation_mode: string;
  };
  interest: {
    interest_level: string;
    interest_score: number;
    positives: string[];
    blockers: string[];
    summary: string;
  };
  conversation: ConversationRecord;
};

export type ShortlistResponse = {
  parsed_job: {
    title: string;
    normalized_requirement: {
      role: string;
    };
  };
  results: CandidateRecord[];
};
