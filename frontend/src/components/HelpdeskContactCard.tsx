import React, { useState } from 'react';
import { Phone, ChevronDown, ChevronUp } from 'lucide-react';

const HelpdeskContactCard: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="mt-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-800"
      >
        <Phone className="h-3 w-3" />
        <span>For more details, contact helpdesk</span>
        {isOpen ? (
          <ChevronUp className="h-3 w-3" />
        ) : (
          <ChevronDown className="h-3 w-3" />
        )}
      </button>

      {isOpen && (
        <div className="mt-2 rounded-lg border border-emerald-200 bg-emerald-50/70 px-3 py-2.5 text-xs leading-5 text-slate-700 space-y-0.5">
          <p>📞 <strong>e-GP Helpdesk Hotline:</strong> 16575 (from any mobile network in Bangladesh)</p>
          <p>☎️ <strong>Telephone Support:</strong> +880 9609112233 / +880 1762625528–31</p>
          <p>✉️ <strong>Email Support:</strong>{' '}
            <a href="mailto:helpdesk@eprocure.gov.bd" className="text-blue-600 underline">helpdesk@eprocure.gov.bd</a>
            {' / '}
            <a href="mailto:e-gphelpdesk@cptu.gov.bd" className="text-blue-600 underline">e-gphelpdesk@cptu.gov.bd</a>
          </p>
          <p>🌐 <strong>Official Portal:</strong>{' '}
            <a href="https://www.eprocure.gov.bd" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
              https://www.eprocure.gov.bd
            </a>
          </p>
          <p>🏢 <strong>Authority:</strong> Bangladesh Public Procurement Authority (BPPA) / CPTU, IMED, Ministry of Planning</p>
        </div>
      )}
    </div>
  );
};

export default HelpdeskContactCard;
