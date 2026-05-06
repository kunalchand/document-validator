import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Stack,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

import ExtractionProgress from '../components/ExtractionProgress';
import { simulateExtractionEvents, simulateExtractionError, playEvents } from '../utils/extractionSimulator';

const ExtractionProgressDemo = () => {
  const [events, setEvents] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState('success'); // 'success' or 'error'
  const [currentStatus, setCurrentStatus] = useState('idle'); // 'idle', 'running', 'complete'

  const startSimulation = async (scenario) => {
    setEvents([]);
    setIsPlaying(true);
    setCurrentStatus('running');
    setSelectedScenario(scenario);

    try {
      const generator = scenario === 'success'
        ? simulateExtractionEvents()
        : simulateExtractionError();

      await playEvents(generator, (event) => {
        setEvents(prev => [...prev, event]);
      });

      setCurrentStatus('complete');
    } catch (error) {
      console.error('Simulation error:', error);
      setCurrentStatus('error');
    } finally {
      setIsPlaying(false);
    }
  };

  const resetDemo = () => {
    setEvents([]);
    setIsPlaying(false);
    setCurrentStatus('idle');
  };

  return (
    <Container maxWidth="md" sx={{ paddingY: 4 }}>
      {/* Header */}
      <Box sx={{ marginBottom: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, marginBottom: 1 }}>
          Extraction Progress Component Demo
        </Typography>
        <Typography variant="body1" color="textSecondary">
          This demo simulates the Phase 1 document extraction pipeline with realistic event streaming.
          Click a button below to start a simulation scenario.
        </Typography>
      </Box>

      {/* Control Buttons */}
      <Card sx={{ marginBottom: 3, backgroundColor: '#F5F5F5' }}>
        <CardContent>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <Button
              variant="contained"
              color="success"
              startIcon={isPlaying && selectedScenario === 'success' ? <StopIcon /> : <PlayArrowIcon />}
              onClick={() => startSimulation('success')}
              disabled={isPlaying}
              fullWidth
            >
              {isPlaying && selectedScenario === 'success' ? 'Running...' : 'Run Success Scenario'}
            </Button>

            <Button
              variant="contained"
              color="error"
              startIcon={isPlaying && selectedScenario === 'error' ? <StopIcon /> : <ErrorIcon />}
              onClick={() => startSimulation('error')}
              disabled={isPlaying}
              fullWidth
            >
              {isPlaying && selectedScenario === 'error' ? 'Running...' : 'Run Error Scenario'}
            </Button>

            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={resetDemo}
              disabled={isPlaying}
              fullWidth
            >
              Reset
            </Button>
          </Stack>

          {/* Status Info */}
          <Box sx={{ marginTop: 2 }}>
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography variant="body2" color="textSecondary">
                Status:
              </Typography>
              {isPlaying ? (
                <>
                  <CircularProgress size={20} />
                  <Typography variant="body2" sx={{ fontWeight: 500, color: '#1976D2' }}>
                    Simulation running...
                  </Typography>
                </>
              ) : currentStatus === 'complete' ? (
                <Typography variant="body2" sx={{ fontWeight: 500, color: '#4CAF50' }}>
                  ✓ Simulation complete
                </Typography>
              ) : currentStatus === 'error' ? (
                <Typography variant="body2" sx={{ fontWeight: 500, color: '#F44336' }}>
                  ✗ Simulation failed
                </Typography>
              ) : (
                <Typography variant="body2" sx={{ fontWeight: 500, color: '#999' }}>
                  Ready to start
                </Typography>
              )}
            </Stack>
          </Box>
        </CardContent>
      </Card>

      {/* Information Alert */}
      <Alert severity="info" sx={{ marginBottom: 3 }}>
        <Typography variant="body2">
          <strong>Try it:</strong> Click a scenario button to simulate the extraction process. The component
          will update in real-time as events are received. Click the expand button to see details including
          metrics, sections found, and the event log.
        </Typography>
      </Alert>

      {/* Component Under Test */}
      {events.length > 0 && (
        <>
          <ExtractionProgress events={events} />

          {/* Event Count */}
          <Box sx={{ marginTop: 2, textAlign: 'center' }}>
            <Typography variant="caption" color="textSecondary">
              {events.length} events generated • {events[events.length - 1]?.timestamp &&
                `Last event: ${new Date(events[events.length - 1].timestamp).toLocaleTimeString()}`}
            </Typography>
          </Box>
        </>
      )}

      {/* Feature Overview */}
      <Card sx={{ marginTop: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, marginBottom: 2 }}>
            Component Features
          </Typography>
          <Stack spacing={1}>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                ✓ Real-time Event Streaming
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Receives events and updates UI incrementally
              </Typography>
            </Box>

            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                ✓ Multi-stage Progress Tracking
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Shows Parsing → Segmentation → Extraction → Finalization stages
              </Typography>
            </Box>

            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                ✓ Segment-Level Details
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Displays current segment, segment count, and rules found so far
              </Typography>
            </Box>

            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                ✓ Expandable Details Panel
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Collapsible section with metrics, sections, timeline, and event log
              </Typography>
            </Box>

            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                ✓ Error Handling
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Gracefully handles and displays error events with appropriate styling
              </Typography>
            </Box>

            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                ✓ Metrics Display
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Shows document size, section count, rules found, and unique rules
              </Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      {/* Event Structure Reference */}
      <Card sx={{ marginTop: 2 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, marginBottom: 1 }}>
            Event Structure (TypeScript)
          </Typography>
          <Box
            component="pre"
            sx={{
              backgroundColor: '#F5F5F5',
              padding: 2,
              borderRadius: 1,
              overflow: 'auto',
              fontSize: '0.75rem',
              fontFamily: 'monospace',
            }}
          >
{`interface ExtractionEvent {
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
}`}
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default ExtractionProgressDemo;
