// EmulatorJS integration helpers: the EJS_* globals it reads, the settings
// fallback patch, and pushing save data into a running emulator.

/* eslint-disable @typescript-eslint/no-explicit-any */

declare global {
  interface Window {
    EJS_core: string;
    EJS_biosUrl: string;
    EJS_player: string;
    EJS_pathtodata: string;
    EJS_color: string;
    EJS_gameID: number;
    EJS_gameName: string;
    EJS_backgroundImage: string;
    EJS_backgroundColor: string;
    EJS_backgroundBlur: boolean;
    EJS_gameUrl: string | Blob;
    EJS_loadStateURL: string | null;
    EJS_cheats: string;
    EJS_gameParentUrl: string;
    EJS_gamePatchUrl: string;
    EJS_netplayServer: string;
    EJS_netplayICEServers: unknown[];
    EJS_alignStartButton: "top" | "center" | "bottom";
    EJS_startOnLoaded: boolean;
    EJS_fullscreenOnLoaded: boolean;
    EJS_threads: boolean;
    EJS_controlScheme: string | null;
    EJS_defaultOptions: object;
    EJS_defaultControls: object;
    EJS_emulator: any;
    EJS_language: string;
    EJS_disableAutoLang: boolean;
    EJS_DEBUG_XX: boolean;
    EJS_CacheLimit: number;
    EJS_Buttons: Record<string, boolean>;
    EJS_VirtualGamepadSettings: Record<string, unknown>;
    EJS_volume: number;
    EJS_paths: Record<string, string>;
    EJS_startButtonName: string;
    EJS_softLoad: boolean;
    EJS_screenCapture: object;
    EJS_externalFiles: Record<string, string>;
    EJS_videoRotation: number;
    EJS_fixedSaveInterval: number;
    EJS_disableCue: boolean;
    EJS_dontExtractRom: boolean;
    EJS_dontExtractBIOS: boolean;
    EJS_disableDatabases: boolean;
    EJS_disableLocalStorage: boolean;
    EJS_disableAutoUnload: boolean;
    EJS_disableBatchBootup: boolean;
    EJS_onGameStart: () => void;
    EJS_onSaveState: (args: {
      screenshot: ArrayBuffer;
      state: ArrayBuffer;
    }) => void;
    EJS_onLoadState: () => void;
    EJS_onSaveSave: (args: {
      screenshot: ArrayBuffer;
      save: ArrayBuffer;
    }) => void;
    EJS_onLoadSave: () => void;
  }
}

function installDefaultOptionsFallback(emulator: any) {
  if (emulator.__rommSettingsPatched) return;
  emulator.__rommSettingsPatched = true;

  const originalPreGetSetting = emulator.preGetSetting.bind(emulator);
  emulator.preGetSetting = (setting: string) => {
    const value = originalPreGetSetting(setting);
    if (value !== undefined && value !== null) return value;
    const defaults = emulator.config?.defaultOptions ?? {};
    return defaults[setting] !== undefined ? defaults[setting] : null;
  };

  emulator.getCoreSettings = () => {
    const defaults: Record<string, unknown> =
      emulator.config?.defaultOptions ?? {};
    let saved: Record<string, unknown> = {};
    if (window.localStorage && !emulator.config?.disableLocalStorage) {
      try {
        const raw = localStorage.getItem(emulator.getLocalStorageKey());
        const parsed = raw ? JSON.parse(raw) : null;
        if (parsed?.settings instanceof Object) saved = parsed.settings;
      } catch (error) {
        console.warn("Could not load previous settings", error);
      }
    }
    const merged = { ...defaults, ...saved };
    let output = "";
    for (const key in merged) {
      const value = merged[key];
      const formatted = Number.isNaN(Number(value)) ? `"${value}"` : value;
      output += `${key} = ${formatted}\n`;
    }
    return output;
  };

  emulator.rewindEnabled =
    emulator.preGetSetting("rewindEnabled") === "enabled";
  if (![0, 1, 2, 3].includes(emulator.config?.videoRotation)) {
    emulator.videoRotation = emulator.preGetSetting("videoRotation") || 0;
  }
  const webgl2Setting = emulator.preGetSetting("webgl2Enabled");
  if (webgl2Setting === "disabled" || !emulator.supportsWebgl2) {
    emulator.webgl2Enabled = false;
  } else if (webgl2Setting === "enabled") {
    emulator.webgl2Enabled = true;
  } else {
    emulator.webgl2Enabled = null;
  }
}

/** Patch each emulator instance so EJS_defaultOptions act as real defaults. */
export function installEJSDefaultOptionsTrap() {
  let instance: any;
  Object.defineProperty(window, "EJS_emulator", {
    configurable: true,
    get: () => instance,
    set: (value) => {
      instance = value;
      if (value) installDefaultOptionsFallback(value);
    },
  });
}

export function loadEmulatorJSSave(save: Uint8Array) {
  const FS = window.EJS_emulator.gameManager.FS;
  const path = window.EJS_emulator.gameManager.getSaveFilePath();
  const paths = path.split("/");
  let cp = "";
  for (let i = 0; i < paths.length - 1; i++) {
    if (paths[i] === "") continue;
    cp += "/" + paths[i];
    if (!FS.analyzePath(cp).exists) FS.mkdir(cp);
  }
  if (FS.analyzePath(path).exists) FS.unlink(path);
  FS.writeFile(path, save);
  window.EJS_emulator.gameManager.loadSaveFiles();
}

export function loadEmulatorJSState(state: Uint8Array) {
  window.EJS_emulator.gameManager.loadState(state);
}

/** Read the running game's save file, or null when the core has none yet. */
export function readEmulatorJSSave(): Uint8Array | null {
  const FS = window.EJS_emulator.gameManager.FS;
  const path = window.EJS_emulator.gameManager.getSaveFilePath();
  if (!FS.analyzePath(path).exists) return null;
  return FS.readFile(path);
}
