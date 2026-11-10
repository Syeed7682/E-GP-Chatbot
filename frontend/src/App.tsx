import React, { useState, useEffect } from 'react';
import { GovtOfficialHeader } from './components/GovtOfficialHeader';
import { GovtOfficialSidebar } from './components/GovtOfficialSidebar';
import { GovtChatArea } from './components/GovtChatArea';
import { UserGuideModal } from './components/UserGuideModal';
import { PortalScreenModal } from './components/PortalScreenModal';
import { SyncInspectorModal } from './components/SyncInspectorModal';
import { ChatMessage, SyncState, SyncMutation } from './types/egp';
import { syncService } from './services/syncService';
import { checkBackendHealth, sendChatQuery } from './services/api';
import { isVagueStepsRequest } from './utils/offlineVectorEngine';
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
  const [activeTab, setActiveTab] = useState<'chat' | 'guide'>('chat');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [language, setLanguage] = useState<'en' | 'bn'>('en');
  const [backendError, setBackendError] = useState<string | null>(null);
  const [uploadedImage, setUploadedImage] = useState<{ base64: string; name: string; mime: string } | null>(null);

  // E1 is the grounded text model; E2 selects the Groq multimodal vision model.
  const [useAltModel, setUseAltModel] = useState(false);

  // Modals
  const [isGuideModalOpen, setIsGuideModalOpen] = useState(false);
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

  // Setup app and load the saved conversation
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
        setMessages(stored.filter((message) => !message.id.startsWith('seed-')));
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
      const previousQuestion = [...messages]
        .reverse()
        .find((message) =>
          message.sender === 'user' &&
          message.text.trim() &&
          !isVagueStepsRequest(message.text)
        )
        ?.text;
      const result = await sendChatQuery({
        question: text.trim(),
        previous_question: previousQuestion,
        image_base64: attached?.base64,
        image_mime: attached?.mime,
        image_name: attached?.name,
        top_k: 3,
        use_alt_model: useAltModel
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
    setIsMobileSidebarOpen(false);
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
    <div className="flex h-dvh flex-col overflow-hidden bg-[radial-gradient(ellipse_at_top,_#dcecff_0%,_#eef4f7_45%,_#dfe8ef_100%)] text-[#334155] font-sans">
      {/* 1. Government-Style Header */}
      <GovtOfficialHeader
        syncState={syncState}
        onOpenMobileMenu={() => setIsMobileSidebarOpen(true)}
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          if (tab === 'guide') setIsGuideModalOpen(true);
        }}
        language={language}
        onToggleLanguage={() => setLanguage(prev => prev === 'en' ? 'bn' : 'en')}
        onOpenSyncModal={() => setIsSyncModalOpen(true)}
        onNewChat={handleNewChat}
        useAltModel={useAltModel}
        onToggleAltModel={() => setUseAltModel(prev => !prev)}
      />

      {/* 2. Main Content Container */}
      <div className="mx-auto flex min-h-0 w-full min-w-0 max-w-[1750px] flex-1 flex-col overflow-hidden border-x border-white/60 bg-white/55 shadow-sm backdrop-blur-xl md:flex-row">
        {/* Navigation / Sidebar Panel */}
        <GovtOfficialSidebar
          syncState={syncState}
          isMobileOpen={isMobileSidebarOpen}
          onCloseMobile={() => setIsMobileSidebarOpen(false)}
          onSelectSuggestedQuestion={handleSelectSuggestedQuestion}
          onNewChat={handleNewChat}
          onClearConversation={handleClearConversation}
          language={language}
          onOpenSyncModal={() => setIsSyncModalOpen(true)}
        />

        {/* Main Chat Interface */}
        <GovtChatArea
          messages={messages}
          inputQuestion={inputQuestion}
          setInputQuestion={setInputQuestion}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          uploadedImage={uploadedImage}
          onImageSelected={(img) => {
            setUploadedImage(img);
          }}
          onOpenScreenModal={(screenId) => setSelectedScreenId(screenId)}
          language={language}
          backendError={backendError}
          onRetry={() => {
            setBackendError(null);
            checkBackendHealth();
          }}
        />
      </div>

      {/* User Guide Modal */}
      <UserGuideModal
        isOpen={isGuideModalOpen}
        onClose={() => setIsGuideModalOpen(false)}
        onSelectQuery={handleSelectSuggestedQuestion}
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
