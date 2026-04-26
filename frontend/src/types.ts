export type TranscriptTurn = {
  speaker: "recruiter" | "candidate";
  message: string;
  turn_index: number;
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
