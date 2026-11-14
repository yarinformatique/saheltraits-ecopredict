"use client";

import React, { useState } from "react";
import { Header } from "@/components/Header";
import { TaxonExplorer } from "@/components/TaxonExplorer";
import { ClimateSimulator } from "@/components/ClimateSimulator";
import { SurveysDashboard } from "@/components/SurveysDashboard";
import { UserManual } from "@/components/UserManual";
import { ExportModal } from "@/components/ExportModal";
import { Footer } from "@/components/Footer";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<"explorer" | "simulator" | "surveys" | "manual">("explorer");
  const [isExportOpen, setIsExportOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      <Header
        activeTab={activeTab}
        onTabChange={(tab) => setActiveTab(tab)}
        onOpenExport={() => setIsExportOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === "explorer" && <TaxonExplorer />}
        {activeTab === "simulator" && <ClimateSimulator />}
        {activeTab === "surveys" && <SurveysDashboard />}
        {activeTab === "manual" && <UserManual />}
      </main>

      <Footer />

      <ExportModal isOpen={isExportOpen} onClose={() => setIsExportOpen(false)} />
    </div>
  );
}
