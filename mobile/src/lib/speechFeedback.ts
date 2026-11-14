// SahelField - Feedback Vocal via Web Speech API pour confirmation terrain mains-libres

class SpeechFeedbackService {
  private isSupported: boolean = false;
  private isEnabled: boolean = true;
  private synth: SpeechSynthesis | null = null;

  constructor() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.synth = window.speechSynthesis;
      this.isSupported = true;
      // Load preference from localStorage
      const saved = localStorage.getItem('sahelfield_voice_enabled');
      if (saved !== null) {
        this.isEnabled = saved === 'true';
      }
    }
  }

  public setEnabled(enabled: boolean) {
    this.isEnabled = enabled;
    if (typeof window !== 'undefined') {
      localStorage.setItem('sahelfield_voice_enabled', enabled ? 'true' : 'false');
    }
  }

  public getIsEnabled(): boolean {
    return this.isEnabled && this.isSupported;
  }

  public speak(message: string, isAlert: boolean = false) {
    if (!this.isSupported || !this.isEnabled || !this.synth) return;

    try {
      this.synth.cancel(); // Stop any pending utterance
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.lang = 'fr-FR';
      utterance.rate = isAlert ? 1.05 : 1.0;
      utterance.pitch = isAlert ? 1.2 : 1.0;
      this.synth.speak(utterance);
    } catch (e) {
      console.warn('SpeechSynthesis error:', e);
    }
  }

  public notifyPlotSaved(plotId: string, accuracyM?: number) {
    const accText = accuracyM ? ` avec précision ${accuracyM.toFixed(1)} mètres` : '';
    this.speak(`Placette ${plotId} enregistrée avec succès${accText}.`);
  }

  public notifyTreeSaved(speciesName: string, qrCode: string) {
    this.speak(`Individu ${speciesName}, code ${qrCode}, validé.`);
  }

  public notifyTraitSaved(traitName: string, value: number, unit: string) {
    this.speak(`Trait ${traitName} égal à ${value} ${unit} enregistré.`);
  }

  public notifyWarning(warningMessage: string) {
    this.speak(`Attention : ${warningMessage}`, true);
  }

  public notifySyncComplete(count: number) {
    this.speak(`Synchronisation réussie. ${count} éléments transmis à SahelTraits DB.`);
  }
}

export const speechService = new SpeechFeedbackService();
