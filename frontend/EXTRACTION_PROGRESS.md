# Extraction Progress Component

## Overview

A real-time extraction progress component for Phase 1 document processing. Displays multi-stage pipeline progress (Parsing → Segmentation → Extraction → Finalization) with collapsible details panel, metrics, section list, and event timeline.

## Files Created

### Core Component
- **`src/components/ExtractionProgress.jsx`** - Main progress component
  - Receives `events` prop (array of ExtractionEvent objects)
  - Displays current stage with animated icon
  - Overall progress bar (0-100%)
  - Segment-level progress (e.g., "Segment 3 of 7")
  - Collapsible details panel with:
    - Key metrics (document size, sections found, rules extracted)
    - Section titles identified
    - Processing timeline showing all stages
    - Event log with timestamps

### Event Schema
- **`src/types/extraction.ts`** - TypeScript definitions
  - `ExtractionEvent` - event interface
  - `ExtractionEventType` - valid event type union
  - `ExtractionStage` - pipeline stages
  - `ExtractionProgress` - progress tracking
  - `ExtractionEventData` - contextual data

### Demo & Simulator
- **`src/utils/extractionSimulator.js`** - Event stream simulator
  - `simulateExtractionEvents()` - Success scenario generator
  - `simulateExtractionError()` - Error scenario generator
  - `playEvents()` - Play events from generator with callback
  - Realistic timings and data (2-3 seconds per segment, 2-6 rules per segment)

- **`src/pages/ExtractionProgressDemo.jsx`** - Interactive demo page
  - Two scenario buttons (success / error)
  - Real-time event generation
  - Metrics and status display
  - Event structure reference
  - Component feature overview

## Accessing the Demo

After starting the frontend dev server:

```bash
cd frontend
npm run dev
```

Visit:
```
http://localhost:5173/demo/extraction-progress
```

Click "Run Success Scenario" or "Run Error Scenario" to see the component in action.

## Event Schema

```typescript
interface ExtractionEvent {
  event_type: 'parsing_started' | 'parsing_complete' |
              'segmentation_complete' | 'extraction_started' |
              'extraction_progress' | 'extraction_complete' |
              'finalization_started' | 'finalization_complete' | 'error'
  
  stage: 'parsing' | 'segmentation' | 'extraction' | 'finalization'
  
  message: string
  
  progress?: {
    current?: number    // current item index
    total?: number      // total items
    percent?: number    // 0-100
  }
  
  data?: {
    char_count?: number
    page_count?: number
    section_count?: number
    section_titles?: string[]
    segment_index?: number
    segment_title?: string
    rules_in_segment?: number
    total_rules_so_far?: number
    total_rules?: number
    unique_rules?: number
  }
  
  timestamp: string
}
```

## Component Props

```typescript
interface ExtractionProgressProps {
  events: ExtractionEvent[]  // Array of events to render
}
```

Pass events as they arrive from the backend SSE stream.

## Visual Features

- **Color-coded stages** - Each stage has a distinct color (blue/orange/purple/green)
- **Animated progress** - Spinning icon for active stage, checkmark for completed
- **Collapsible design** - Click header to expand/collapse details
- **Error handling** - Different styling and messaging for error events
- **Responsive grid** - Metrics display adapts to screen size
- **Real-time updates** - Component re-renders as new events arrive

## Component Behavior

### Default (Collapsed)
```
[Spinner] Extracting Rules
████████░░ 60%  [Expand ∨]
Segment 3 of 7 • 12 rules found so far
```

### Expanded
Shows:
- Key Metrics (document size, sections, rules found)
- Sections Identified (as chips)
- Processing Timeline (all stages with status)
- Event Log (full event history with timestamps)

### Error State
- Red left border instead of stage color
- Warning icon instead of stage icon
- Red progress bar
- Error message displayed

## Integration with Phase 1

Once the backend SSE endpoint is implemented at `POST /api/v1/extract-rules-stream`, integrate by:

1. In `Phase1.jsx`, create a state for events:
   ```javascript
   const [extractionEvents, setExtractionEvents] = useState([])
   ```

2. When user uploads document, connect to SSE stream:
   ```javascript
   const eventSource = new EventSource('/api/v1/extract-rules-stream')
   eventSource.onmessage = (event) => {
     const extractionEvent = JSON.parse(event.data)
     setExtractionEvents(prev => [...prev, extractionEvent])
   }
   ```

3. Render component during extraction:
   ```javascript
   {isExtracting && <ExtractionProgress events={extractionEvents} />}
   ```

## Demo Scenarios

### Success Scenario
- Parses 24,586 character, 12-page document
- Segments into 7 sections with realistic titles
- Extracts 2-6 rules per segment (total ~25 rules)
- Deduplicates to ~21 unique rules
- Total duration: ~18-20 seconds

### Error Scenario
- Starts parsing successfully
- Fails during segmentation
- Shows error message and styling
- Useful for testing error handling in UI

## Next Steps

1. **Backend SSE Endpoint** - Implement `POST /api/v1/extract-rules-stream` that emits these events in real-time
2. **Phase 1 Integration** - Connect component to actual SSE stream
3. **Event Schema Alignment** - Ensure backend Python events match this TypeScript schema exactly
