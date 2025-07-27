export interface Tweet {
  id: string;
  text: string;
  user_handle: string;
  created_at: string;
  engagement_score: number;
  url: string;
}

export interface ProductRequest {
  category: string;
  description: string;
  pain_point: string;
  target_audience: string;
  urgency_level: string;
  tweets: Tweet[];
}

export interface AnalysisSummary {
  total_tweets_analyzed: number;
  product_requests_found: number;
  token_usage: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
}

export interface AnalysisData {
  summary: AnalysisSummary;
  product_requests: ProductRequest[];
}

export interface DailyAnalysis {
  date: string;
  data: AnalysisData;
}