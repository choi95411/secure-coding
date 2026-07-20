const form = document.getElementById("chat-form");
const conversationId = form.dataset.conversationId;
const scheme = location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(`${scheme}://${location.host}/ws/chat/${conversationId}/`);
const input = document.getElementById("chat-input");
const box = document.getElementById("messages");
const error = document.getElementById("chat-error");
const submit = document.getElementById("chat-submit");

socket.onopen = () => {
  submit.disabled = false;
};
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.error) {
    error.textContent = data.error;
    return;
  }
  document.getElementById("empty-message")?.remove();
  const paragraph = document.createElement("p");
  const sender = document.createElement("strong");
  sender.textContent = `${data.sender}: `;
  paragraph.append(sender, document.createTextNode(data.message));
  box.appendChild(paragraph);
  box.scrollTop = box.scrollHeight;
};
socket.onclose = () => {
  submit.disabled = true;
  error.textContent = "채팅 연결이 종료되었습니다.";
};
form.addEventListener("submit", (event) => {
  event.preventDefault();
  error.textContent = "";
  if (socket.readyState !== WebSocket.OPEN) {
    error.textContent = "채팅 서버에 연결되지 않았습니다.";
    return;
  }
  socket.send(JSON.stringify({ message: input.value }));
  input.value = "";
});