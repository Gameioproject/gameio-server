import "./styles.css";

const form = document.getElementById("delete-form") as HTMLFormElement | null;
const status = document.getElementById("status");

function show(kind: "error" | "done" | "busy", text: string): void {
  if (!status) return;
  status.dataset.kind = kind;
  status.textContent = text;
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const username = (
    document.getElementById("username") as HTMLInputElement
  ).value.trim();
  const password = (document.getElementById("password") as HTMLInputElement)
    .value;
  const confirmed = (document.getElementById("confirm") as HTMLInputElement)
    .checked;
  if (!username || !password) {
    show("error", "Enter your username and password.");
    return;
  }
  if (!confirmed) {
    show("error", "Tick the box to confirm.");
    return;
  }
  const button = form.querySelector("button");
  if (button) button.disabled = true;
  show("busy", "Deleting your account…");
  try {
    const response = await fetch("/api/users/delete-account", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (response.status === 204) {
      form.reset();
      show("done", "Your account has been deleted.");
      return;
    }
    show(
      "error",
      response.status === 401 || response.status === 403
        ? "That username and password don't match an account."
        : "Your account couldn't be deleted. Try again later.",
    );
  } catch {
    show(
      "error",
      "Couldn't reach Gameio. Check your connection and try again.",
    );
  }
  if (button) button.disabled = false;
});
