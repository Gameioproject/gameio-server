/**
 * The hero handheld: a small screen state machine driven by the drawn D-pad, the keyboard
 * and any connected gamepad, so the page demonstrates the launcher's controller-first
 * navigation instead of describing it.
 */
type Dir = "up" | "down" | "left" | "right";
type Btn = "a" | "b" | "x" | "y" | "select" | "start";

const GAMEPAD_BUTTON: Record<number, Btn | Dir> = {
  0: "a",
  1: "b",
  2: "x",
  3: "y",
  8: "select",
  9: "start",
  12: "up",
  13: "down",
  14: "left",
  15: "right",
};
const AXIS_DEADZONE = 0.5;
const PRESS_FLASH_MS = 140;

export function mountHandheld(root: HTMLElement, onConfirm: () => void): void {
  const slides = Array.from(root.querySelectorAll<HTMLElement>(".slide"));
  const leds = Array.from(root.querySelectorAll<HTMLElement>(".leds i"));
  const status = root.querySelector<HTMLElement>("#status");
  let index = 0;

  function show(next: number): void {
    index = (next + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      const active = i === index;
      slide.classList.toggle("is-active", active);
      slide.setAttribute("aria-hidden", active ? "false" : "true");
    });
    leds.forEach((led, i) => led.classList.toggle("on", i === index));
  }

  function say(text: string): void {
    if (status) status.textContent = text;
  }

  function flash(selector: string): void {
    const el = root.querySelector<HTMLElement>(selector);
    if (!el) return;
    el.classList.add("pressed");
    window.setTimeout(() => el.classList.remove("pressed"), PRESS_FLASH_MS);
  }

  function press(input: Btn | Dir): void {
    switch (input) {
      case "left":
        flash(".arm.left");
        show(index - 1);
        break;
      case "right":
        flash(".arm.right");
        show(index + 1);
        break;
      case "up":
        flash(".arm.up");
        break;
      case "down":
        flash(".arm.down");
        break;
      case "a":
      case "start":
        flash(input === "a" ? ".btn.a" : ".pill[data-btn='start']");
        onConfirm();
        break;
      case "b":
        flash(".btn.b");
        show(0);
        break;
      case "x":
      case "y":
      case "select":
        flash(input === "select" ? ".pill[data-btn='select']" : `.btn.${input}`);
        break;
    }
  }

  root.addEventListener("click", (event) => {
    const target = (event.target as HTMLElement).closest<HTMLElement>("[data-dir], [data-btn]");
    if (!target) return;
    const input = (target.dataset.dir ?? target.dataset.btn) as Btn | Dir;
    press(input);
  });

  const keys: Record<string, Btn | Dir> = {
    ArrowLeft: "left",
    ArrowRight: "right",
    ArrowUp: "up",
    ArrowDown: "down",
    Enter: "a",
    " ": "a",
    Escape: "b",
  };
  window.addEventListener("keydown", (event) => {
    const active = document.activeElement;
    const typing = active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement;
    const input = keys[event.key];
    if (!input || typing || event.metaKey || event.ctrlKey || event.altKey) return;
    if (input === "a" && active instanceof HTMLAnchorElement) return;
    event.preventDefault();
    press(input);
  });

  watchGamepads(press, say);
  show(0);
}

/** Polls the Gamepad API and turns edges (not held buttons) into presses. */
function watchGamepads(press: (input: Btn | Dir) => void, say: (text: string) => void): void {
  if (!("getGamepads" in navigator)) return;
  const held = new Set<string>();
  let announced = false;
  let raf = 0;

  function poll(): void {
    const pads = navigator.getGamepads();
    let any = false;
    for (const pad of pads) {
      if (!pad) continue;
      any = true;
      pad.buttons.forEach((button, i) => {
        const input = GAMEPAD_BUTTON[i];
        if (!input) return;
        const key = `${pad.index}:${i}`;
        if (button.pressed && !held.has(key)) {
          held.add(key);
          press(input);
        } else if (!button.pressed) {
          held.delete(key);
        }
      });
      const x = pad.axes[0] ?? 0;
      const axisKey = `${pad.index}:axis`;
      const dir: Dir | null = x < -AXIS_DEADZONE ? "left" : x > AXIS_DEADZONE ? "right" : null;
      if (dir && !held.has(axisKey)) {
        held.add(axisKey);
        press(dir);
      } else if (!dir) {
        held.delete(axisKey);
      }
    }
    if (any && !announced) {
      announced = true;
      say("CONTROLLER CONNECTED");
    }
    raf = window.requestAnimationFrame(poll);
  }

  window.addEventListener("gamepadconnected", () => {
    if (!raf) poll();
  });
  window.addEventListener("gamepaddisconnected", () => {
    if (navigator.getGamepads().every((pad) => !pad)) {
      window.cancelAnimationFrame(raf);
      raf = 0;
      announced = false;
      say("READY");
    }
  });
  if (navigator.getGamepads().some((pad) => pad)) poll();
}
