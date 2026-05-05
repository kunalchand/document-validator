export const DUMMY_EXTRACTED_RULES = {
  document_id: 'doc_20250505_001',
  extraction_timestamp: '2025-05-05T10:30:00Z',
  total_rules: 5,
  rules: [
    {
      id: 'rule_001',
      title: 'Employee Background Check',
      description: 'All employees must undergo a comprehensive background check before employment',
      conditions: [
        'Check must be completed within 30 days of offer',
        'Must include criminal history verification',
        'Must include employment history verification'
      ],
      expected_evidence: [
        'Background check report from accredited vendor',
        'Employee acknowledgment form',
        'Clearance letter signed by HR'
      ],
      section: 'Section 2: Hiring Procedures',
      severity: 'high',
      status: 'extracted'
    },
    {
      id: 'rule_002',
      title: 'Data Confidentiality Agreement',
      description: 'Every employee must sign a data confidentiality agreement upon joining',
      conditions: [
        'Agreement must be signed before first day of work',
        'Must be on company letterhead',
        'Must include non-disclosure terms'
      ],
      expected_evidence: [
        'Signed confidentiality agreement',
        'Employee signature and date',
        'Witness or HR signature'
      ],
      section: 'Section 3: Employment Agreements',
      severity: 'high',
      status: 'extracted'
    },
    {
      id: 'rule_003',
      title: 'Annual Compliance Training',
      description: 'All employees must complete mandatory compliance training annually',
      conditions: [
        'Training must be completed within 90 days of hire',
        'Refresher training required annually in Q1',
        'Completion certificate must be obtained'
      ],
      expected_evidence: [
        'Training completion certificate',
        'Course completion date',
        'Score of 80% or higher on assessment'
      ],
      section: 'Section 4: Training Requirements',
      severity: 'medium',
      status: 'extracted'
    },
    {
      id: 'rule_004',
      title: 'Code of Conduct Acknowledgment',
      description: 'Employees must acknowledge receipt and understanding of the code of conduct',
      conditions: [
        'Acknowledgment must be documented in writing',
        'Must include employee signature',
        'Must be dated'
      ],
      expected_evidence: [
        'Signed code of conduct form',
        'Employee name and date',
        'Department or manager name'
      ],
      section: 'Section 5: Code of Conduct',
      severity: 'medium',
      status: 'extracted'
    },
    {
      id: 'rule_005',
      title: 'Performance Review Documentation',
      description: 'Each employee must have a documented performance review at least annually',
      conditions: [
        'Review must be conducted by direct manager',
        'Review must be documented in writing',
        'Employee must sign the review'
      ],
      expected_evidence: [
        'Completed performance review form',
        'Manager comments and ratings',
        'Employee signature and date'
      ],
      section: 'Section 6: Performance Management',
      severity: 'low',
      status: 'extracted'
    }
  ]
}
