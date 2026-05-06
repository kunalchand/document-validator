/**
 * Event schema for Phase 1 extraction progress streaming
 * Matches backend Phase1ExtractionEvent structure
 */

export type ExtractionEventType =
  | 'parsing_started'
  | 'parsing_complete'
  | 'segmentation_started'
  | 'segmentation_complete'
  | 'extraction_started'
  | 'extraction_progress'
  | 'extraction_complete'
  | 'finalization_started'
  | 'finalization_complete'
  | 'error';

export type ExtractionStage =
  | 'parsing'
  | 'segmentation'
  | 'extraction'
  | 'finalization';

export interface ExtractionProgress {
  current?: number; // Current item (e.g., segment 3)
  total?: number; // Total items (e.g., out of 7 segments)
  percent?: number; // 0-100
}

export interface ExtractionEventData {
  char_count?: number;
  page_count?: number;
  section_count?: number;
  section_titles?: string[];
  segment_index?: number;
  segment_title?: string;
  rules_in_segment?: number;
  total_rules_so_far?: number;
  failed_segments?: number;
  total_rules?: number;
  unique_rules?: number;
  extracted_rules?: Record<string, unknown>[];
}

export interface ExtractionEvent {
  event_type: ExtractionEventType;
  stage: ExtractionStage;
  message: string;
  progress?: ExtractionProgress;
  data?: ExtractionEventData;
  timestamp: string;
}

/**
 * Processed event for UI rendering with computed fields
 */
export interface ProcessedExtractionEvent extends ExtractionEvent {
  duration?: number; // ms since stage start
  isActive: boolean;
  isComplete: boolean;
}
