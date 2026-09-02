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

export interface MatchResult {
  fileName: string;
  targetRole: string;
  matchScore: number;
  matchedSkills: string[];
  missingSkills: string[];
  atsKeywords: string[];
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  ai: AiMetadata;
}

export interface PersistedResumeAnalysisResponse {
  id: number;
  createdAt: string;
  result: ResumeAnalysisResult;
}

export interface PersistedMatchResponse {
  id: number;
  createdAt: string;
  result: MatchResult;
}

export interface AnalysisSummaryDto {
  id: number;
  analysisType: 'RESUME' | 'MATCH';
  fileName: string;
  candidateName: string | null;
  predictedField: string | null;
  resumeScore: number | null;
  matchScore: number | null;
  targetRole: string | null;
  aiProvider: string;
  usedFallback: boolean;
  createdAt: string;
}

export interface PagedAnalysisSummary {
  items: AnalysisSummaryDto[];
  page: number;
  size: number;
  totalItems: number;
  totalPages: number;
}

export interface AnalysisDetailResponse {
  id: number;
  analysisType: 'RESUME' | 'MATCH';
  fileName: string;
  createdAt: string;
  resultJson: Record<string, any>;
}

export interface AdminMetricsResponse {
  totalAnalyses: number;
  resumeAnalysesCount: number;
  matchAnalysesCount: number;
  fallbackRate: number;
  avgLatencyMs: number;
  p95LatencyMs: number;
}

export interface UserDto {
  id: number;
  email: string;
  fullName: string;
  role: 'USER' | 'ADMIN';
}

export interface PagedUsers {
  items: UserDto[];
  page: number;
  size: number;
  totalItems: number;
  totalPages: number;
}

export interface PagedAdminAnalyses {
  items: AnalysisSummaryDto[];
  page: number;
  size: number;
  totalItems: number;
  totalPages: number;
}

export interface ResumeResultLocationState {
  result?: ResumeAnalysisResult;
}

export interface MatchResultLocationState {
  result?: MatchResult;
}

export interface ApiErrorResponse {
  message: string;
  statusCode?: number;
  error?: string;
}