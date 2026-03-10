"use client";

import { ChatPanel } from "@/components/chat/ChatPanel";
import { InspectorPanel } from "@/components/editor/InspectorPanel";
import { Navbar } from "@/components/layout/Navbar";
import { ResizeHandle } from "@/components/layout/ResizeHandle";
import { Sidebar } from "@/components/layout/Sidebar";
import { AppProvider, useAppStore } from "@/lib/store";

function Workspace() {
  const { sidebarWidth, inspectorWidth, setSidebarWidth, setInspectorWidth } = useAppStore();

  return (
    <main className="min-h-screen p-4 md:p-6">
      <div className="mx-auto flex max-w-[1800px] flex-col gap-4">
        <Navbar />
        <div className="flex min-h-[calc(100vh-146px)] gap-0">
          <div style={{ width: sidebarWidth }}>
            <Sidebar />
          </div>
          <ResizeHandle onResize={(delta) => setSidebarWidth(Math.max(260, sidebarWidth + delta))} />
          <ChatPanel />
          <ResizeHandle
            onResize={(delta) => setInspectorWidth(Math.max(320, inspectorWidth - delta))}
          />
          <div style={{ width: inspectorWidth }}>
            <InspectorPanel />
          </div>
        </div>
      </div>
    </main>
  );
}

export default function Page() {
  return (
    <AppProvider>
      <Workspace />
    </AppProvider>
  );
}
