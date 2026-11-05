import React, { useState } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { ChatWindow } from '../chat/ChatWindow';
import { ManualViewer } from '../manual/ManualViewer';
import { PortalOverview } from '../PortalOverview';
import { SyncInspector } from '../offline/SyncInspector';
import { ChatMessage } from '../../types/egp';
import { submitChatMessage } from '../../services/chatService';

export const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'manual' | 'screens'>('chat');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [targetPage, setTargetPage] = useState<number>(6);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);

  const handleSendMessage = async (text: string, imageBase64?: string, imageName?: string) => {
    const userMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: text,
      image_url: imageBase64,
      timestamp: Date.now()
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      await submitChatMessage(
        {
          question: text,
          image_base64: imageBase64,
          image_name: imageName
        },
        (assistantMsg) => {
          setMessages((prev) => [...prev, assistantMsg]);
        }
      );
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: `Error processing request: ${err.message || 'Please verify connection.'}`,
        timestamp: Date.now()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenPage = (page: number) => {
    setTargetPage(page);
    setActiveTab('manual');
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-100 dark:bg-slate-950">
      {/* Top Navigation */}
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onOpenInspector={() => setIsInspectorOpen(true)}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          onSelectTopic={(topic) => handleSendMessage(topic)}
          onOpenPage={handleOpenPage}
        />

        {/* Dynamic Center Work Area */}
        <main className="flex-1 flex overflow-hidden">
          {activeTab === 'chat' && (
            <div className="flex-1 flex">
              <div className="flex-1">
                <ChatWindow
                  messages={messages}
                  isLoading={isLoading}
                  onSendMessage={handleSendMessage}
                  onOpenPage={handleOpenPage}
                  onSelectPrompt={(p) => handleSendMessage(p)}
                />
              </div>
              {/* Optional Right Pane for Side-by-Side Manual Viewer */}
              <div className="hidden lg:block w-96 border-l border-slate-200 dark:border-slate-800">
                <ManualViewer initialPage={targetPage} />
              </div>
            </div>
          )}

          {activeTab === 'manual' && (
            <div className="flex-1">
              <ManualViewer initialPage={targetPage} />
            </div>
          )}

          {activeTab === 'screens' && (
            <div className="flex-1 overflow-y-auto p-6 bg-slate-50 dark:bg-slate-950">
              <PortalOverview />
            </div>
          )}
        </main>
      </div>

      {/* Sync Inspector Modal */}
      {isInspectorOpen && (
        <SyncInspector isOpen={isInspectorOpen} onClose={() => setIsInspectorOpen(false)} />
      )}
    </div>
  );
};

