export type PredictedField =
  | 'Data Science'
  | 'Web Development'
  | 'Android Development'
  | 'iOS Development'
  | 'UI/UX'
  | 'Unknown';

export interface FieldEvidence {
  field: PredictedField;
  matchedSkills: string[];
  confidence: number;
}

export interface ScoreBreakdown {
  contact: number;
  summary: number;
  skills: number;
  education: number;
  experience: number;
  projects: number;
  achievementsCertifications: number;
  quantifiedImpact: number;
  total: number;
}

export interface AiMetadata {
  provider: 'OLLAMA' | 'RULE_BASED';
  model: string;
  usedFallback: boolean;
  processingMs: number;
}

export interface ResumeAnalysisResult {
  fileName: string;
  candidateName: string | null;
  candidateEmail: string | null;
  skills: string[];
  predictedField: PredictedField;
  fieldEvidence: FieldEvidence[];
  resumeScore: number;
  scoreBreakdown: ScoreBreakdown;
  recommendedSkills: string[];
  recommendations: string[];
  ai: AiMetadata;
}
