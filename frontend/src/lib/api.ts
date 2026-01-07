const API_URL = import.meta.env.PUBLIC_API_URL;

export async function sendMessageToChat(message: string) {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    throw new Error(`Error al comunicarse con el backend: ${res.statusText}`);
  }

  return res.json();
}