/**
 * Official e-GP Portal Screen Catalog.
 * Mapped to official PE manual pages and screen codes.
 */
export interface PortalScreenMetadata {
  id: string;
  code: string;
  name: string;
  page_number: number;
  category: 'authentication' | 'app' | 'tender' | 'evaluation' | 'debarment' | 'cms' | 'troubleshooting';
  description: string;
  fields: string[];
}

export const PORTAL_SCREENS: PortalScreenMetadata[] = [
  {
    id: 'deb-01',
    code: 'Screen - DEB-01',
    name: 'Debarment & Suspension Search Interface',
    page_number: 342,
    category: 'debarment',
    description: 'Statutory verification screen to search ongoing and expired contractor debarments by Ministry, Organization, or Company Name.',
    fields: ['Select Ministry/Division/Organization', 'Search For (Company/Individual)', 'Company Name', 'Debar Period', 'Country', 'Debarment Status (Ongoing/Expired)']
  },
  {
    id: 'deb-02',
    code: 'Screen - DEB-02',
    name: 'Debarment Proposal & HOPE Submission',
    page_number: 347,
    category: 'debarment',
    description: 'Interface for PE Creator/Officer to submit debarment recommendations and evidence to HOPE for electronic approval.',
    fields: ['Contractor License No', 'Allegation Summary', 'Proposed Debarment Period', 'Supporting Documents', 'Send to HOPE']
  },
  {
    id: 'auth-01',
    code: 'Screen - AUTH-01',
    name: 'Procuring Entity Gateway Login',
    page_number: 6,
    category: 'authentication',
    description: 'Official login portal for Procuring Entity officers requiring Email ID and secure system password.',
    fields: ['Email ID', 'Password', 'Security Token', 'Login']
  },
  {
    id: 'app-01',
    code: 'Screen - APP-01',
    name: 'Annual Procurement Plan (APP) Creation Form',
    page_number: 21,
    category: 'app',
    description: 'Entry form for procurement packages, estimated budget in BDT, and statutory procurement nature.',
    fields: ['Financial Year', 'Project Title', 'Package No', 'Procurement Method', 'Approving Authority']
  },
  {
    id: 'd50',
    code: 'Screen - D50',
    name: 'Tender Cancellation Process Screen',
    page_number: 178,
    category: 'tender',
    description: 'Official cancellation interface available until tender closing date, requiring documented justification remarks.',
    fields: ['Tender ID', 'Cancellation Reason', 'Official Remarks', 'Confirm Cancellation']
  },
  {
    id: 'q10.4',
    code: 'Screen - Q10.4',
    name: 'Evaluation Committee Discrepancy Error',
    page_number: 284,
    category: 'troubleshooting',
    description: 'System alert triggered during financial proposal opening when BOQ arithmetic sum mismatches currency format.',
    fields: ['Error Code Q10.4', 'Discrepancy Details', 'Arithmetic Reconciliation']
  }
];

