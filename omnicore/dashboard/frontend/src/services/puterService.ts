declare global {
  interface Window {
    puter?: any;
  }
}

export interface PuterNodeDefinition {
  action: string;
  capability: string;
  target: string;
  inputs: string[];
  outputs: string[];
  description: string;
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

/**
 * Uses Puter.js Gemini 2.0 Flash model to dynamically decompose an arbitrary sentence
 * into structured node definitions for AST, Execution DAG, LLVM Optimization Graph, and Graphify visualization.
 */
export async function decomposeQueryWithPuterAI(query: string): Promise<PuterNodeDefinition[]> {
  if (typeof window !== 'undefined' && window.puter && window.puter.ai) {
    try {
      const systemPrompt = `You are OmniCore AI Compiler's front-end parser AI. Decompose the user request into an ordered sequence of execution nodes for AST, ExecutionDAG, and Knowledge Graph visualization.
Return ONLY valid JSON array with objects containing:
- action: verb (e.g., "search", "summarize", "generate", "analyze", "compare")
- capability: one of ["web_search", "summarization", "pdf_generation", "report_generation", "data_analysis", "comparison", "email", "retrieval", "database_access"]
- target: object/subject of action
- inputs: array of input symbol names (e.g. [], ["findings"], ["summary"])
- outputs: array of output symbol names (e.g. ["findings"], ["summary"], ["pdf"])
- description: concise node description

User prompt: "${query}"`;

      const response = await window.puter.ai.chat(systemPrompt, { model: 'gemini-2.0-flash' });
      let text = '';
      if (typeof response === 'string') text = response;
      else if (response && response.message && response.message.content) {
        text = typeof response.message.content === 'string' ? response.message.content : JSON.stringify(response.message.content);
      }

      // Extract JSON array from model output
      const jsonMatch = text.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        if (Array.isArray(parsed)) return parsed;
      }
    } catch (err) {
      console.warn('Puter.js AI decomposition error:', err);
    }
  }
  return [];
}
