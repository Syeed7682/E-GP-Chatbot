import React, { useState, useEffect } from 'react';
import { GovtOfficialHeader } from './components/GovtOfficialHeader';
import { GovtOfficialSidebar } from './components/GovtOfficialSidebar';
import { GovtChatArea } from './components/GovtChatArea';
import { UserGuideModal } from './components/UserGuideModal';
import { AboutModal } from './components/AboutModal';
import { PortalScreenModal } from './components/PortalScreenModal';
import { SyncInspectorModal } from './components/SyncInspectorModal';
import { ChatMessage, SyncState, SyncMutation } from './types/egp';
import { syncService } from './services/syncService';
import { checkBackendHealth, sendChatQuery } from './services/api';
import {
  initOfflineStorage,
  getLocalMessages,
  saveMessageLocally,
  clearAllLocalMessages,
  queueMutation
} from './utils/indexedDBStorage';
import { fastHash } from './utils/crypto';
import { SERVER_DATASET_VERSION, SERVER_DATASET_HASH } from './data/manualChunks';

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'guide' | 'about'>('chat');
  const [language, setLanguage] = useState<'en' | 'bn'>('en');
  const [backendError, setBackendError] = useState<string | null>(null);
  const [uploadedImage, setUploadedImage] = useState<{ base64: string; name: string; mime: string } | null>(null);

  // Modals
  const [isGuideModalOpen, setIsGuideModalOpen] = useState(false);
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);
  const [isSyncModalOpen, setIsSyncModalOpen] = useState(false);
  const [selectedScreenId, setSelectedScreenId] = useState<string | null>(null);

  // Sync state
  const [syncState, setSyncState] = useState<SyncState>({
    is_online: true,
    is_simulated_offline: false,
    is_syncing: false,
    last_synced_at: null,
    server_version: SERVER_DATASET_VERSION,
    local_version: SERVER_DATASET_VERSION,
    pending_count: 0,
    total_synced_count: 1188,
    conflict_count: 0,
    checksum_verified: true,
    server_hash: SERVER_DATASET_HASH,
    local_hash: SERVER_DATASET_HASH,
    conflict_strategy: 'server_wins'
  });

  // Setup app & seed initial state
  useEffect(() => {
    async function setup() {
      await initOfflineStorage();
      syncService.init();

      const unsubscribe = syncService.subscribe((state) => {
        setSyncState(state);
      });

      // Check backend health quietly without blocking UI
      checkBackendHealth().then((health) => {
        if (!health.isHealthy) {
          console.info('Backend check: offline or mock mode active.');
        }
      });

      // Load saved messages from IndexedDB
      const stored = await getLocalMessages();
      if (stored && stored.length > 0) {
        setMessages(stored);
      } else {
        // Seed initial official example
        const seedUser: ChatMessage = {
          id: 'seed-user-1',
          sender: 'user',
          text: 'How to delete a tender?',
          timestamp: Date.now() - 3600000,
          sync_status: 'synced',
          local_revision: 1
        };

        const seedAssistant: ChatMessage = {
          id: 'seed-asst-1',
          sender: 'assistant',
          text: `Based on the official e-GP Procuring Entity User Manual, procedures for deleting or canceling a tender depend on its current status:

1. Draft Status (Unpublished):
   - Navigate to "Tender" > "My Tenders" > Select the draft tender.
   - Click "Edit Tender" and scroll to the bottom action bar.
   - Click the "Delete Draft Tender" button to permanently remove the unissued draft and temporary BOQ tables.

2. Workflow / Published Status:
   - Once a tender has entered the approval workflow or has been published to the portal, direct deletion is strictly disallowed under Public Procurement Rules (PPR).
   - If changes are needed, the PE user must initiate an official "Tender Corrigendum / Amendment" or "Cancellation Notice" under PPR Rule 45.
   - Enter specific cancellation justifications, attach ministerial directives if applicable, and route through the Workflow Approver.

📷 Refer to portal screens: Screen - Q10.4, Screen - D6

📖 Source: e-GP System User Manual (Procuring Entity User 1 February 2026), Page 56, Page 510`,
          timestamp: Date.now() - 3590000,
          portal_screens: ['Screen - Q10.4', 'Screen - D6'],
          sources: [
            {
              source: 'e-GP System User Manual - Procuring Entity User 1 February 2026',
              page: 56,
              chunk_id: 56,
              score: 0.95,
              snippet: 'A tender in Draft status can be deleted by Tender Creator; published tenders require formal Corrigendum notice under PPR.'
            },
            {
              source: 'e-GP System User Manual - Procuring Entity User 1 February 2026',
              page: 510,
              chunk_id: 510,
              score: 0.89,
              snippet: 'Screen - Q10.4 triggers when tender deletion disallowed after tender notice publication.'
            }
          ],
          sync_status: 'synced',
          local_revision: 1
        };

        await saveMessageLocally(seedUser);
        await saveMessageLocally(seedAssistant);
        setMessages([seedUser, seedAssistant]);
      }

      return () => unsubscribe();
    }

    setup();
  }, []);

  // Handle Send Message
  const handleSendMessage = async (text: string) => {
    if (!text.trim() && !uploadedImage) return;

    setBackendError(null);
    const userMsgId = 'msg_user_' + Date.now();
    const isOnline = syncState.is_online;

    const userMessage: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      text: text.trim(),
      timestamp: Date.now(),
      image_url: uploadedImage?.base64,
      image_name: uploadedImage?.name,
      sync_status: isOnline ? 'synced' : 'pending',
      local_revision: 1
    };

    setMessages(prev => [...prev, userMessage]);
    await saveMessageLocally(userMessage);

    // Queue mutation if offline
    if (!isOnline) {
      const mut: SyncMutation = {
        id: 'mut_' + userMsgId,
        type: 'create_message',
        payload: userMessage,
        client_timestamp: Date.now(),
        revision: 1,
        status: 'pending',
        hash: fastHash(JSON.stringify(userMessage))
      };
      await queueMutation(mut);
    }

    setInputQuestion('');
    const attached = uploadedImage;
    setUploadedImage(null);
    setIsLoading(true);

    try {
      const result = await sendChatQuery({
        question: text.trim(),
        image_base64: attached?.base64,
        image_name: attached?.name,
        top_k: 3
      });

      const assistantMessage: ChatMessage = {
        id: 'msg_asst_' + Date.now(),
        sender: 'assistant',
        text: result.answer,
        timestamp: Date.now(),
        sources: result.sources,
        portal_screens: result.portal_screens,
        sync_status: isOnline ? 'synced' : 'pending',
        local_revision: 1,
        answered_offline: result.was_offline
      };

      await saveMessageLocally(assistantMessage);

      if (!isOnline) {
        const asstMut: SyncMutation = {
          id: 'mut_' + assistantMessage.id,
          type: 'create_message',
          payload: assistantMessage,
          client_timestamp: Date.now(),
          revision: 1,
          status: 'pending',
          hash: fastHash(JSON.stringify(assistantMessage))
        };
        await queueMutation(asstMut);
      }

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      setBackendError(err.message || 'Unable to connect to the backend server. Answers are being resolved from local manual index.');
    } finally {
      setIsLoading(false);
      const cur = await syncService.getCurrentState();
      setSyncState(cur);
    }
  };

  const handleSelectSuggestedQuestion = (q: string) => {
    setActiveTab('chat');
    setInputQuestion(q);
    handleSendMessage(q);
  };

  const handleNewChat = () => {
    setActiveTab('chat');
    setInputQuestion('');
    setUploadedImage(null);
  };

  const handleClearConversation = async () => {
    if (confirm('Clear the conversation history? This will delete local chat logs from your browser.')) {
      await clearAllLocalMessages();
      setMessages([]);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F3F6F9] text-[#334155] font-sans">
      {/* 1. Government-Style Header */}
      <GovtOfficialHeader
        syncState={syncState}
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          if (tab === 'guide') setIsGuideModalOpen(true);
          if (tab === 'about') setIsAboutModalOpen(true);
        }}
        language={language}
        onToggleLanguage={() => setLanguage(prev => prev === 'en' ? 'bn' : 'en')}
        onOpenSyncModal={() => setIsSyncModalOpen(true)}
        onNewChat={handleNewChat}
      />

      {/* 2. Main Content Container */}
      <div className="flex-1 flex flex-col md:flex-row max-w-[1750px] w-full mx-auto overflow-hidden shadow-sm border-x border-[#D5DEE7] bg-white">
        {/* Navigation / Sidebar Panel */}
        <GovtOfficialSidebar
          syncState={syncState}
          onSelectSuggestedQuestion={handleSelectSuggestedQuestion}
          onNewChat={handleNewChat}
          onClearConversation={handleClearConversation}
          language={language}
          onOpenSyncModal={() => setIsSyncModalOpen(true)}
        />

        {/* Main Chat Interface */}
        <GovtChatArea
          messages={messages}
          syncState={syncState}
          inputQuestion={inputQuestion}
          setInputQuestion={setInputQuestion}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          uploadedImage={uploadedImage}
          onImageSelected={(img) => setUploadedImage(img)}
          onOpenScreenModal={(screenId) => setSelectedScreenId(screenId)}
          language={language}
          backendError={backendError}
          onRetry={() => {
            setBackendError(null);
            checkBackendHealth();
          }}
          onSelectSuggestedQuestion={handleSelectSuggestedQuestion}
        />
      </div>

      {/* User Guide Modal */}
      <UserGuideModal
        isOpen={isGuideModalOpen}
        onClose={() => setIsGuideModalOpen(false)}
        onSelectQuery={handleSelectSuggestedQuestion}
        language={language}
      />

      {/* About Assistant Modal */}
      <AboutModal
        isOpen={isAboutModalOpen}
        onClose={() => setIsAboutModalOpen(false)}
        language={language}
      />

      {/* Offline Sync Inspector Modal */}
      <SyncInspectorModal
        isOpen={isSyncModalOpen}
        onClose={() => setIsSyncModalOpen(false)}
        syncState={syncState}
        onForceSync={() => syncService.syncNow()}
        onToggleSimulatedOffline={() => syncService.setSimulatedOffline(!syncState.is_simulated_offline)}
      />

      {/* Interactive Portal Screen Viewer Modal */}
      <PortalScreenModal
        screenId={selectedScreenId}
        onClose={() => setSelectedScreenId(null)}
      />
    </div>
  );
}
