const API_URL = import.meta.env.PUBLIC_API_URL;

async function handleResponse(res: Response) {
  if (!res.ok) {
    let errorMessage = `Error ${res.status}: ${res.statusText}`;
    try {
      const errorData = await res.json();
      if (errorData && errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch (e) {
      // Ignorar errores al parsear JSON de error
    }
    throw new Error(errorMessage);
  }
  return res.json();
}

export async function sendMessageToChat(message: string) {
  const res = await fetch(`${API_URL}/journal/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: message }),
  });
  return handleResponse(res);
}

export async function getStats() {
  try {
    const res = await fetch(`${API_URL}/journal/stats`);
    return await handleResponse(res);
  } catch (error) {
    console.error("Error fetching stats:", error);
    return null;
  }
}

export async function getDiaryEntry(date: string) {
  const res = await fetch(`${API_URL}/journal/diary/${date}`);
  return handleResponse(res);
}

export async function saveDiaryEntry(text: string, date?: string) {
  const res = await fetch(`${API_URL}/journal/diary/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, date }),
  });
  return handleResponse(res);
}