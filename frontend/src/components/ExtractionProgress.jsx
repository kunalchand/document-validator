import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Collapse,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Chip,
  Grid,
  Divider,
  Paper,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

const STAGE_NAMES = {
  parsing: 'Parsing Document',
  segmentation: 'Analyzing Structure',
  extraction: 'Extracting Rules',
  finalization: 'Finalizing Results',
};

const STAGE_COLORS = {
  parsing: '#2196F3',
  segmentation: '#FF9800',
  extraction: '#9C27B0',
  finalization: '#4CAF50',
};

const ExtractionProgress = ({ events = [] }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Get current stage and progress
  const currentEvent = events[events.length - 1];
  const currentStage = currentEvent?.stage || 'parsing';
  const isComplete = currentEvent?.event_type === 'extraction_complete' ||
                     currentEvent?.event_type === 'finalization_complete';
  const isError = currentEvent?.event_type === 'error';

  // Calculate overall progress
  const stageSequence = ['parsing', 'segmentation', 'extraction', 'finalization'];
  const currentStageIndex = stageSequence.indexOf(currentStage);
  const overallPercent = Math.round(((currentStageIndex + 1) / stageSequence.length) * 100);

  // Get metrics from latest events
  const parsingEvent = events.find(e => e.event_type === 'parsing_complete');
  const segmentationEvent = events.find(e => e.event_type === 'segmentation_complete');
  const extractionEvents = events.filter(e => e.event_type === 'extraction_progress');
  const latestExtractionEvent = extractionEvents[extractionEvents.length - 1];
  const finalEvent = events.find(e => e.event_type === 'extraction_complete');

  const charCount = parsingEvent?.data?.char_count;
  const sectionCount = segmentationEvent?.data?.section_count;
  const sectionTitles = segmentationEvent?.data?.section_titles || [];
  const currentSegment = latestExtractionEvent?.progress?.current;
  const totalSegments = latestExtractionEvent?.progress?.total;
  const rulesFoundSoFar = latestExtractionEvent?.data?.total_rules_so_far;
  const totalRules = finalEvent?.data?.total_rules;
  const uniqueRules = finalEvent?.data?.unique_rules;

  const getStageIcon = (stage) => {
    const stageIdx = stageSequence.indexOf(stage);
    const completed = isComplete || stageIdx < currentStageIndex;
    const active = !isComplete && stage === currentStage;

    if (completed) {
      return <CheckCircleIcon sx={{ color: STAGE_COLORS[stage] }} />;
    }
    if (active) {
      return <ScheduleIcon sx={{ color: STAGE_COLORS[stage], animation: 'spin 1s linear infinite' }} />;
    }
    return <ScheduleIcon sx={{ color: '#ccc' }} />;
  };

  return (
    <Card
      sx={{
        backgroundColor: isError ? '#FFEBEE' : '#F5F5F5',
        borderLeft: `4px solid ${isError ? '#F44336' : STAGE_COLORS[currentStage]}`,
      }}
    >
      <CardContent>
        {/* Header with Collapse Toggle */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer',
            userSelect: 'none',
          }}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, marginBottom: 1 }}>
              {isError ? (
                <WarningIcon sx={{ color: '#F44336' }} />
              ) : (
                getStageIcon(currentStage)
              )}
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {isError
                  ? 'Extraction Failed'
                  : isComplete
                  ? 'Extraction Complete'
                  : STAGE_NAMES[currentStage]}
              </Typography>
            </Box>

            {/* Overall Progress Bar */}
            <Box sx={{ marginY: 1 }}>
              <LinearProgress
                variant="determinate"
                value={isError ? 0 : Math.min(overallPercent, 100)}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: isError ? '#FFCDD2' : '#E0E0E0',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: isError ? '#F44336' : STAGE_COLORS[currentStage],
                    borderRadius: 4,
                  },
                }}
              />
            </Box>

            {/* Status Text */}
            <Typography variant="body2" color="textSecondary">
              {isError
                ? currentEvent?.message
                : currentEvent?.message || 'Ready to process...'}
            </Typography>

            {/* Segment Progress for Extraction Stage */}
            {currentStage === 'extraction' && totalSegments && (
              <Typography variant="caption" sx={{ display: 'block', marginTop: 0.5, color: '#666' }}>
                Segment {currentSegment} of {totalSegments}
                {rulesFoundSoFar && ` • ${rulesFoundSoFar} rules found so far`}
              </Typography>
            )}
          </Box>

          {/* Expand/Collapse Button */}
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
          >
            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>

        {/* Expandable Details Section */}
        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
          <Box sx={{ marginTop: 2, paddingTop: 2, borderTop: '1px solid #E0E0E0' }}>
            {/* Key Metrics */}
            <Typography variant="subtitle2" sx={{ fontWeight: 600, marginBottom: 1 }}>
              Key Metrics
            </Typography>
            <Grid container spacing={2} sx={{ marginBottom: 2 }}>
              {charCount && (
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ padding: 1.5, backgroundColor: '#F9F9F9' }}>
                    <Typography variant="caption" color="textSecondary">
                      Document Size
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {charCount.toLocaleString()} characters
                      {parsingEvent?.data?.page_count && ` • ${parsingEvent.data.page_count} pages`}
                    </Typography>
                  </Paper>
                </Grid>
              )}

              {sectionCount && (
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ padding: 1.5, backgroundColor: '#F9F9F9' }}>
                    <Typography variant="caption" color="textSecondary">
                      Sections Found
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {sectionCount} logical sections
                    </Typography>
                  </Paper>
                </Grid>
              )}

              {rulesFoundSoFar && (
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ padding: 1.5, backgroundColor: '#F9F9F9' }}>
                    <Typography variant="caption" color="textSecondary">
                      Rules Found
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {rulesFoundSoFar} candidates
                    </Typography>
                  </Paper>
                </Grid>
              )}

              {uniqueRules && (
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ padding: 1.5, backgroundColor: '#F9F9F9' }}>
                    <Typography variant="caption" color="textSecondary">
                      Unique Rules
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {uniqueRules} final rules
                    </Typography>
                  </Paper>
                </Grid>
              )}
            </Grid>

            {/* Sections Found */}
            {sectionTitles.length > 0 && (
              <>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, marginBottom: 1, marginTop: 2 }}>
                  Sections Identified
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, marginBottom: 2 }}>
                  {sectionTitles.map((title, idx) => (
                    <Chip
                      key={idx}
                      label={title}
                      size="small"
                      variant="outlined"
                      icon={<InfoIcon />}
                    />
                  ))}
                </Box>
              </>
            )}

            {/* Stage Timeline */}
            <Typography variant="subtitle2" sx={{ fontWeight: 600, marginBottom: 1, marginTop: 2 }}>
              Processing Timeline
            </Typography>
            <List sx={{ backgroundColor: '#FAFAFA', borderRadius: 1, padding: 0 }}>
              {stageSequence.map((stage, idx) => {
                const completed = isComplete || stageSequence.indexOf(stage) < currentStageIndex;
                const active = !isComplete && stage === currentStage;
                const stageEvents = events.filter(e => e.stage === stage);
                const lastStageEvent = stageEvents[stageEvents.length - 1];

                return (
                  <ListItem
                    key={stage}
                    sx={{
                      backgroundColor: active ? '#F0F4FF' : completed ? '#F5F5F5' : 'white',
                      borderBottom: idx < stageSequence.length - 1 ? '1px solid #E0E0E0' : 'none',
                      opacity: completed || active ? 1 : 0.5,
                    }}
                  >
                    <ListItemIcon>{getStageIcon(stage)}</ListItemIcon>
                    <ListItemText
                      primary={STAGE_NAMES[stage]}
                      secondary={lastStageEvent?.message || 'Pending'}
                      primaryTypographyProps={{
                        sx: { fontWeight: active ? 600 : 500, color: STAGE_COLORS[stage] },
                      }}
                    />
                    {completed && (
                      <Chip label="Complete" size="small" variant="outlined" />
                    )}
                    {active && (
                      <Chip label="In Progress" size="small" color="info" />
                    )}
                  </ListItem>
                );
              })}
            </List>

            {/* Event Log */}
            {events.length > 0 && (
              <>
                <Divider sx={{ marginY: 2 }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 600, marginBottom: 1 }}>
                  Event Log
                </Typography>
                <List sx={{ maxHeight: 300, overflow: 'auto' }}>
                  {events.map((event, idx) => (
                    <ListItem key={idx} sx={{ paddingY: 0.5, paddingX: 1 }}>
                      <ListItemText
                        primary={`${event.event_type}`}
                        secondary={
                          <Typography variant="caption" component="span" sx={{ display: 'block' }}>
                            {event.message} {event.timestamp && `• ${new Date(event.timestamp).toLocaleTimeString()}`}
                          </Typography>
                        }
                        primaryTypographyProps={{ variant: 'caption', sx: { fontFamily: 'monospace' } }}
                      />
                    </ListItem>
                  ))}
                </List>
              </>
            )}
          </Box>
        </Collapse>
      </CardContent>

      {/* Spinner animation for active extraction */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </Card>
  );
};

export default ExtractionProgress;
