/**
 * Simulator for Phase 1 extraction events
 * Generates realistic event sequences for UI testing/demo
 */

const SAMPLE_SECTIONS = [
  'Section 1: Hiring Procedures',
  'Section 2: Employment Agreements',
  'Section 3: Training Requirements',
  'Section 4: Compliance Standards',
  'Section 5: Data Protection',
  'Section 6: Code of Conduct',
  'Section 7: Performance Management',
];

/**
 * Generate a sequence of extraction events that simulate the full Phase 1 pipeline
 * Returns an async generator that yields events over time
 */
export async function* simulateExtractionEvents() {
  const startTime = new Date();

  const createEvent = (event_type, stage, message, progress = null, data = null) => ({
    event_type,
    stage,
    message,
    progress,
    data,
    timestamp: new Date().toISOString(),
  });

  // Stage 1: Parsing
  yield createEvent(
    'parsing_started',
    'parsing',
    'Reading document...'
  );

  await delay(1500);

  yield createEvent(
    'parsing_complete',
    'parsing',
    'Document parsed: 24,586 characters, 12 pages',
    null,
    {
      char_count: 24586,
      page_count: 12,
    }
  );

  // Stage 2: Segmentation
  await delay(800);

  yield createEvent(
    'segmentation_started',
    'segmentation',
    'Analyzing document structure...'
  );

  await delay(2000);

  yield createEvent(
    'segmentation_complete',
    'segmentation',
    'Found 7 logical sections',
    null,
    {
      section_count: 7,
      section_titles: SAMPLE_SECTIONS,
    }
  );

  // Stage 3: Extraction
  await delay(800);

  yield createEvent(
    'extraction_started',
    'extraction',
    'Starting rule extraction from segments...'
  );

  // Simulate extraction per segment
  const segmentCount = 7;
  let totalRulesSoFar = 0;

  for (let i = 1; i <= segmentCount; i++) {
    await delay(2000 + Math.random() * 1000); // 2-3 seconds per segment

    const rulesInSegment = Math.floor(Math.random() * 5) + 2; // 2-6 rules per segment
    totalRulesSoFar += rulesInSegment;

    yield createEvent(
      'extraction_progress',
      'extraction',
      `Processed "${SAMPLE_SECTIONS[i - 1]}"`,
      {
        current: i,
        total: segmentCount,
        percent: Math.round((i / segmentCount) * 100),
      },
      {
        segment_index: i - 1,
        segment_title: SAMPLE_SECTIONS[i - 1],
        rules_in_segment: rulesInSegment,
        total_rules_so_far: totalRulesSoFar,
      }
    );
  }

  // Stage 4: Finalization
  await delay(1000);

  yield createEvent(
    'extraction_complete',
    'finalization',
    'Deduplicating and finalizing rules...',
    { current: 1, total: 1, percent: 100 },
    {
      total_rules: totalRulesSoFar,
      unique_rules: Math.ceil(totalRulesSoFar * 0.85), // Assume 15% duplicates
    }
  );

  await delay(1000);

  yield createEvent(
    'finalization_complete',
    'finalization',
    'Extraction complete! Ready to review rules.',
    { percent: 100 },
    {
      total_rules: totalRulesSoFar,
      unique_rules: Math.ceil(totalRulesSoFar * 0.85),
    }
  );
}

/**
 * Alternative simulator for error scenario
 */
export async function* simulateExtractionError() {
  const createEvent = (event_type, stage, message, progress = null, data = null) => ({
    event_type,
    stage,
    message,
    progress,
    data,
    timestamp: new Date().toISOString(),
  });

  yield createEvent(
    'parsing_started',
    'parsing',
    'Reading document...'
  );

  await delay(1500);

  yield createEvent(
    'parsing_complete',
    'parsing',
    'Document parsed: 24,586 characters',
    null,
    { char_count: 24586 }
  );

  await delay(800);

  yield createEvent(
    'segmentation_started',
    'segmentation',
    'Analyzing document structure...'
  );

  await delay(2000);

  yield createEvent(
    'error',
    'segmentation',
    'Failed to analyze document structure. The document format may be corrupted or unsupported.'
  );
}

/**
 * Play events from a generator, calling onEvent for each
 */
export async function playEvents(eventGenerator, onEvent) {
  for await (const event of eventGenerator) {
    onEvent(event);
  }
}

/**
 * Helper: sleep for N milliseconds
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
