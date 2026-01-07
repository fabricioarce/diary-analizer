const API_URL = import.meta.env.PUBLIC_API_URL;

export async function sendMessageToChat(message: string) {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: message }),
  });

  if (!res.ok) {
    throw new Error(`Error al comunicarse con el backend: ${res.statusText}`);
  }

  return res.json();
}

export async function getStats() {
  const res = await fetch(`${API_URL}/stats`);
  
  if (!res.ok) {
    console.error("Error fetching stats:", res.statusText);
    return null;
  }
  
  return res.json();
}