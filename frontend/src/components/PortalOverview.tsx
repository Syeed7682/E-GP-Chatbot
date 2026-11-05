import React from 'react';
import { ExternalLink, Bot, ArrowRight, ShieldCheck, FileCheck, Layers, BookOpen } from 'lucide-react';

interface PortalOverviewProps {
  onAskQuestion: (q: string) => void;
  onOpenAssistant: () => void;
}

export const PortalOverview: React.FC<PortalOverviewProps> = ({
  onAskQuestion,
  onOpenAssistant
}) => {
  return (
    <div className="flex-1 bg-[#ffffff] p-5 overflow-y-auto space-y-5 text-gray-800 text-xs">
      {/* 1. Public Procurement Rules (PPR), 2025 / 2026 Section */}
      <div className="space-y-1.5 border-b border-gray-200 pb-3">
        <h2 className="text-sm font-bold text-govt-green tracking-tight flex items-center justify-between">
          <span>Public Procurement Rules (PPR), 2025</span>
          <button
            onClick={onOpenAssistant}
            className="text-xs bg-govt-button text-white font-semibold px-2.5 py-0.5 rounded shadow-xs flex items-center gap-1 cursor-pointer"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Open Manual Chatbot</span>
          </button>
        </h2>

        <p className="text-gray-700 leading-relaxed text-xs">
          With an aim of strengthening governance and ensuring transparency, efficiency and competition in public procurement practices, the Public Procurement Rules (PPR), 2025, formulated through a participatory process by the Bangladesh Public Procurement Authority (BPPA), has been made effective. To align the corresponding rules with the amended PPA, 2006, the PPR, 2025 has been formulated and made effective simultaneously on 28 September 2025. The new PPR, 2025 consists of 154 Rules and 21 Schedules. Major changes to both the law and the rules include:
        </p>

        <button
          onClick={() => onAskQuestion('Explain the major changes in Public Procurement Rules PPR 2025 for Procuring Entity users')}
          className="text-govt-green font-semibold hover:underline cursor-pointer inline-flex items-center gap-1"
        >
          <span>Ask Assistant about PPR 2025 Changes</span>
          <ArrowRight className="w-3 h-3" />
        </button>
      </div>

      {/* 2. About e-Government Procurement (e-GP) System */}
      <div className="space-y-1.5 border-b border-gray-200 pb-3">
        <h2 className="text-sm font-bold text-govt-green tracking-tight">
          About e-Government Procurement (e-GP) System
        </h2>

        <p className="text-gray-700 leading-relaxed text-xs">
          National e-Government Procurement (e-GP) portal ( i.e. <a href="http://eprocure.gov.bd" target="_blank" rel="noreferrer" className="text-blue-700 hover:underline">http://eprocure.gov.bd</a> ) of the Government of the People's Republic of Bangladesh is developed, owned and being operated by the Bangladesh Public Procurement Authority (BPPA), IME Division of Ministry of Planning. The e-GP system provides an on-line platform to carry out the procurement activities by the Public Agencies - Procuring Agencies (PAs) and Procuring Entities (PEs).
        </p>

        <p className="text-gray-700 leading-relaxed text-xs">
          The e-GP system is a single web portal from where and through which PAs and PEs will be able to perform their procurement related activities using a dedicated secured web based dashboard. The e-GP system is hosted in e-GP Data Center at BPPA, and the e-GP web portal is accessible by the PAs and PEs through internet for their use.
        </p>

        <p className="text-gray-700 leading-relaxed text-xs">
          The e-Government Procurement solution introduced under the Public Procurement Reform (PPR) Process is being supported by the World Bank and being used by all the government organizations which will help in ensuring equal access to the Bidders/Tenderers, efficiency, transparency and accountability in the public procurement process in the country.
        </p>
      </div>

      {/* 3. Two Columns: News & Events vs Important Messages */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left Column: News and Events */}
        <div className="border border-[#b7d598] rounded bg-[#ffffff] p-3 shadow-xs space-y-2">
          <h3 className="font-bold text-govt-green border-b border-dotted border-gray-300 pb-1 text-xs">
            News and Events
          </h3>

          <ul className="space-y-2 text-[11px] text-gray-700">
            <li className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>
                Gazette of Bangladesh e-Government Procurement Guidelines (revised) 2025 published - <em className="text-red-600 font-semibold not-italic">Important</em>
              </span>
            </li>
            <li className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>World Password Day observed: Keep your e-GP account strong and safe</span>
            </li>
            <li className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>South Asia procurement innovation awards &amp; national recognition</span>
            </li>
            <li className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>24/7 e-GP Help Desk at CPTU enhanced with AI Assistant Integration</span>
            </li>
            <li className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>Format for organizations about sending info for e-GP registration</span>
            </li>
            <li className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>South Asia regional conference on public procurement in Dhaka Nov 1-3</span>
            </li>
            <li className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>New Delegation of Financial Power (DOFP) issued by Finance Division</span>
            </li>
            <li className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>Flyer about e-GP registration and tendering released</span>
            </li>
          </ul>
        </div>

        {/* Right Column: Important Messages and Support Details */}
        <div className="border border-[#b7d598] rounded bg-[#ffffff] p-3 shadow-xs space-y-2">
          <h3 className="font-bold text-govt-green border-b border-dotted border-gray-300 pb-1 text-xs">
            Important Messages and Support Details
          </h3>

          <div className="space-y-2 text-[11px] text-gray-700 leading-relaxed">
            <p className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>
                The e-GP guidelines were approved by the Government of the People's Republic of Bangladesh in pursuant to Section 65 of the Public Procurement Act, 2006. As per the approved guidelines, e-GP system has been introduced and implemented in two phases.
              </span>
            </p>

            <p className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>
                In the first phase, e-Tendering has been developed and rolled out across all PEs of the government up to District and sub-District level. e-Tendering is an electronic procurement process which provides an online platform for centralized user registration, preparation of Annual Procurement Plan (APP), preparation of Tender/Proposal document, invitation of Tender, sale of Tender Documents (e-TD), conducting online pre-tender meeting, preparation of Tender/Proposal, collection of Tender/Proposal security, on-line Tender/Proposal submission, Tender opening &amp; evaluation, negotiation (where applicable) and contract award.
              </span>
            </p>

            <p className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>
                In the second phase, e-Contract Management System (e-CMS) has been developed, introduced and implemented. e-CMS is a complete electronic contract management system which provides a pure platform for preparation of work plan and its submission; defining milestones, tracking and monitoring progress, variation orders, generating reports, ensure quality, generation of running bills, supplier/contractor rating and generating completion certificate.
              </span>
            </p>

            <p className="flex items-start gap-1.5">
              <span className="text-govt-green font-bold">◈</span>
              <span>
                To improve the e-GP System towards Sustainable Public Procurement, the integration with some other government services such as National Identification System (NID), iBAS++ system, A-Challan and e-PMIS has been completed.
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
