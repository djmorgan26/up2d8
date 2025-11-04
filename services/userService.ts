
export async function subscribeUser(email: string, topics: string[]): Promise<{ message: string }> {
  try {
    // This function calls our own backend API, which would handle storing the subscription.
    // This endpoint would be implemented in your FastAPI backend.
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, topics }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'An unknown server error occurred.');
    }

    return data;
  } catch (error) {
    console.error("Error subscribing user:", error);
    let errorMessage = "Could not connect to the server. Please try again.";
    if (error instanceof Error) {
        errorMessage = error.message;
    }
    throw new Error(errorMessage);
  }
}
