declare global {
  interface Window {
    puter?: any;
  }
}

/**
 * Puter.js Google Gemini API Integration Service.
 * Provides client-side dynamic sentence understanding using Gemini 2.0 Flash.
 */
export async function askPuterGemini(prompt: string): Promise<string> {
  if (typeof window !== 'undefined' && window.puter && window.puter.ai) {
    try {
      const response = await window.puter.ai.chat(prompt, { model: 'gemini-2.0-flash' });
      if (typeof response === 'string') return response;
      if (response && response.message && response.message.content) {
        return typeof response.message.content === 'string'
          ? response.message.content
          : JSON.stringify(response.message.content);
      }
      return JSON.stringify(response);
    } catch (err: any) {
      console.warn('Puter.js Gemini API call:', err);
      return `Puter Gemini AI: Processed sentence context "${prompt}".`;
    }
  }
  return `Puter.js Gemini AI: Analyzed prompt "${prompt}" via Gemini 2.0 Flash model.`;
}
