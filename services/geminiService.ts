
import { GroundingChunk } from '../types';

interface GeminiResponse {
  text: string;
  sources: GroundingChunk[] | undefined;
}

export async function askGeminiWithSearch(prompt: string): Promise<GeminiResponse> {
  try {
    // This function now calls our own backend API, which will securely call the Gemini API.
    // This endpoint would be implemented in your FastAPI backend.
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      // Try to get a meaningful error message from the backend response body
      const errorData = await response.json().catch(() => ({ message: 'An unknown server error occurred.' }));
      throw new Error(errorData.message || `Server responded with status: ${response.status}`);
    }

    const data: GeminiResponse = await response.json();
    return data;

  } catch (error) {
    console.error("Error fetching from backend API:", error);
    let errorMessage = "Could not connect to the server. Please check your connection and try again.";
    if (error instanceof Error) {
        // Use the error message from the fetch failure or the server's response
        errorMessage = error.message;
    }
    throw new Error(errorMessage);
  }
}
