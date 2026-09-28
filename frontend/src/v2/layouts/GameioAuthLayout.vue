<script setup lang="ts">
// The reset pages are the only web app pages players reach on the hosted
// service, so they wear the landing page's look instead of the web app's.
import "../../../landing/tokens.css";

const FONT_HREF =
  "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;550;600;650&display=swap";

if (!document.querySelector(`link[href="${FONT_HREF}"]`)) {
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = FONT_HREF;
  document.head.appendChild(link);
}
</script>

<template>
  <div class="g-auth">
    <div class="g-auth__ambient" aria-hidden="true" />
    <header class="g-auth__top">
      <a class="g-auth__brand" href="/">
        <img src="/brand/gameio_icon.svg" width="32" height="32" alt="" />
        Gameio
      </a>
    </header>
    <main class="g-auth__stage">
      <div class="g-auth__card">
        <router-view name="v2" />
      </div>
    </main>
    <footer class="g-auth__footer">
      <a class="g-auth__brand g-auth__brand--small" href="/">
        <img src="/brand/gameio_icon.svg" width="24" height="24" alt="" />
        Gameio
      </a>
    </footer>
  </div>
</template>

<style scoped>
.g-auth {
  position: relative;
  isolation: isolate;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-inline: 16px;
  background: var(--bg);
  color: var(--ink);
  font: 15px/1.6 var(--sans);
  -webkit-font-smoothing: antialiased;
  color-scheme: dark;
}

.g-auth__ambient {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  background:
    radial-gradient(ellipse at 50% 8%, rgb(255 255 255 / 8%), transparent 65%),
    var(--bg);
}

.g-auth__ambient::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(90deg, rgb(255 255 255 / 5.5%) 1px, transparent 1px),
    linear-gradient(rgb(255 255 255 / 5.5%) 1px, transparent 1px);
  background-size: 88px 88px;
  opacity: 0.35;
  mask-image: radial-gradient(ellipse at 50% 34%, black 20%, transparent 78%);
}

.g-auth__top {
  margin-top: 18px;
  min-height: 60px;
  padding: 8px 22px 8px 18px;
  display: flex;
  align-items: center;
  background: rgb(24 25 28 / 94%);
  border: 1px solid var(--line);
  border-radius: 999px;
  box-shadow: 0 10px 32px rgb(0 0 0 / 20%);
}

.g-auth__brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--ink);
  font-size: 21px;
  font-weight: 550;
  letter-spacing: -0.7px;
  text-decoration: none;
}

.g-auth__brand--small {
  gap: 10px;
  font-size: 16px;
}

.g-auth__brand:focus-visible {
  outline: 2px solid var(--ink);
  outline-offset: 5px;
  border-radius: 8px;
}

.g-auth__stage {
  flex: 1;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-block: 48px;
}

.g-auth__card {
  width: 100%;
  max-width: 440px;
  padding: 32px 28px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: 0 10px 32px rgb(0 0 0 / 20%);
}

.g-auth__footer {
  padding-block: 27px;
}

.g-auth :deep(.g-title) {
  margin: 0 0 20px;
  font-size: 28px;
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: -0.8px;
}

.g-auth :deep(.g-form) {
  display: grid;
  gap: 16px;
}

.g-auth :deep(.g-field) {
  display: grid;
  gap: 6px;
  font-size: 13px;
  color: var(--muted);
}

.g-auth :deep(.g-field input) {
  padding: 12px 14px;
  background: var(--bg);
  color: var(--ink);
  border: 1px solid var(--line);
  border-radius: 10px;
  font: inherit;
  font-size: 15px;
}

.g-auth :deep(.g-field input:focus-visible) {
  outline: 2px solid var(--ink);
  outline-offset: 1px;
}

.g-auth :deep(.g-btn) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 48px;
  padding: 12px 25px;
  background: var(--ink);
  color: var(--bg);
  border: 1px solid transparent;
  border-radius: 999px;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition:
    background 160ms,
    transform 160ms;
}

.g-auth :deep(.g-btn:hover:not(:disabled)) {
  background: white;
  transform: translateY(-2px);
}

.g-auth :deep(.g-btn:focus-visible) {
  outline: 2px solid var(--ink);
  outline-offset: 3px;
}

.g-auth :deep(.g-btn:disabled) {
  opacity: 0.45;
  cursor: default;
}

.g-auth :deep(.g-btn--quiet) {
  background: var(--surface-raised);
  color: var(--ink);
  border-color: var(--line);
}

.g-auth :deep(.g-btn--quiet:hover:not(:disabled)) {
  background: var(--surface-raised);
  border-color: var(--muted);
}

.g-auth :deep(.g-status) {
  min-height: 1.6em;
  margin: 0;
  font-size: 14px;
}

.g-auth :deep(.g-status[data-kind="error"]) {
  color: var(--error);
}

.g-auth :deep(.g-status[data-kind="done"]) {
  color: var(--success);
}

@media (prefers-reduced-motion: reduce) {
  .g-auth :deep(.g-btn) {
    transition: none;
  }
}

@media (max-width: 480px) {
  .g-auth__card {
    padding: 24px 20px;
  }
}
</style>
