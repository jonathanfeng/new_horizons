// @ts-check
(() => {
  "use strict";

  const root = document.documentElement;
  const CAUGHT_KEY = "critter-catcher:caught";
  const PREFS_KEY = "critter-catcher:prefs";
  const ISLAND_OPEN_KEY = "critter-catcher:island-open";
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  /** @typedef {"available" | "all"} View */
  /** @typedef {"value" | "leaving" | "name" | "number"} SortKey */
  /** @typedef {"" | "new" | "leaving"} Focus */
  /** @typedef {{ view: View, sort: SortKey, hideCaught: boolean }} Prefs */
  /**
   * @typedef {object} CardInfo
   * @property {HTMLElement} card
   * @property {number} index
   * @property {number} number
   * @property {string} name
   * @property {string} search
   * @property {number} price
   * @property {boolean} available
   * @property {boolean} isNew
   * @property {boolean} leaving
   * @property {number} monthsLeft
   * @property {string[]} tags
   * @property {HTMLElement} nameEl
   * @property {string} displayName
   * @property {HTMLButtonElement} catchButton
   */

  /** @type {Record<SortKey, (a: CardInfo, b: CardInfo) => number>} */
  const COMPARE = {
    value: (a, b) => b.price - a.price || a.number - b.number,
    leaving: (a, b) => (a.monthsLeft || 99) - (b.monthsLeft || 99) || b.price - a.price || a.number - b.number,
    name: (a, b) => a.name.localeCompare(b.name),
    number: (a, b) => a.number - b.number,
  };

  /** @param {string} key */
  function readJSON(key) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? /** @type {unknown} */ (JSON.parse(raw)) : null;
    } catch {
      return null;
    }
  }

  /** @param {string} key @param {unknown} value */
  function writeJSON(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Private browsing or storage disabled: caught state just won't persist.
    }
  }

  /** @returns {Record<string, number[]>} */
  function loadAllCaught() {
    const data = readJSON(CAUGHT_KEY);
    /** @type {Record<string, number[]>} */
    const result = {};
    if (data && typeof data === "object") {
      for (const [kind, numbers] of Object.entries(data)) {
        if (Array.isArray(numbers)) result[kind] = numbers.filter((value) => Number.isInteger(value));
      }
    }
    return result;
  }

  /** @param {string} kind */
  const loadCaught = (kind) => new Set(loadAllCaught()[kind] || []);

  /** @param {string} kind @param {Set<number>} numbers */
  function saveCaught(kind, numbers) {
    const all = loadAllCaught();
    all[kind] = [...numbers].sort((a, b) => a - b);
    writeJSON(CAUGHT_KEY, all);
  }

  /** @returns {Prefs} */
  function loadPrefs() {
    const data = /** @type {Partial<Record<keyof Prefs, unknown>> | null} */ (readJSON(PREFS_KEY)) || {};
    return {
      view: data.view === "all" ? "all" : "available",
      sort: typeof data.sort === "string" && data.sort in COMPARE ? /** @type {SortKey} */ (data.sort) : "value",
      hideCaught: data.hideCaught === true,
    };
  }

  /** @param {number} hour */
  const formatHour = (hour) => `${hour % 12 || 12} ${hour < 12 ? "AM" : "PM"}`;

  /** @param {string} name */
  function iconElement(name) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "icon");
    svg.setAttribute("aria-hidden", "true");
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", `#i-${name}`);
    svg.append(use);
    return svg;
  }

  /**
   * @param {string} message
   * @param {{ icon?: string, action?: string, onAction?: () => void, timeout?: number }} [options]
   */
  function toast(message, options = {}) {
    const region = document.querySelector("[data-toasts]");
    if (!region) return;
    const element = document.createElement("div");
    element.className = "toast";
    element.setAttribute("role", "status");
    const dismiss = () => {
      element.classList.add("is-leaving");
      window.setTimeout(() => element.remove(), 320);
    };
    if (options.icon) element.append(iconElement(options.icon));
    const text = document.createElement("span");
    text.textContent = message;
    element.append(text);
    if (options.action) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "button";
      button.textContent = options.action;
      button.addEventListener("click", () => {
        dismiss();
        options.onAction?.();
      });
      element.append(button);
    }
    region.append(element);
    if (options.timeout) window.setTimeout(dismiss, options.timeout);
  }

  /** @param {Element} element @param {number} target */
  function countUp(element, target) {
    if (reducedMotion.matches || target <= 0) {
      element.textContent = String(target);
      return;
    }
    const duration = 900;
    const start = performance.now();
    /** @param {number} now */
    const step = (now) => {
      const progress = Math.min(1, (now - start) / duration);
      element.textContent = String(Math.round(target * (1 - Math.pow(1 - progress, 3))));
      if (progress < 1) requestAnimationFrame(step);
    };
    element.textContent = "0";
    requestAnimationFrame(step);
  }

  /** @param {string} kind @param {number} count @param {boolean} animate */
  function renderDex(kind, count, animate) {
    document.querySelectorAll(`[data-dex="${kind}"]`).forEach((element) => {
      if (!(element instanceof HTMLElement)) return;
      const total = Number(element.dataset.total) || 1;
      const counter = element.querySelector("[data-dex-count]");
      if (counter) {
        if (animate) countUp(counter, count);
        else counter.textContent = String(count);
      }
      element.style.setProperty("--dex-progress", String(Math.min(100, (count / total) * 100)));
      element.classList.toggle("has-progress", count > 0);
      if (element.classList.contains("kind-card__dex")) element.hidden = count === 0;
    });
  }

  function startClock() {
    const zone = root.dataset.timezone;
    const timeElements = document.querySelectorAll('[data-clock="time"]');
    const dateElements = document.querySelectorAll('[data-clock="date"]');
    if (!zone) return;
    /** @type {Intl.DateTimeFormat} */ let timeFormat;
    /** @type {Intl.DateTimeFormat} */ let dateFormat;
    /** @type {Intl.DateTimeFormat} */ let partsFormat;
    try {
      timeFormat = new Intl.DateTimeFormat("en-US", { timeZone: zone, hour: "numeric", minute: "2-digit" });
      dateFormat = new Intl.DateTimeFormat("en-US", { timeZone: zone, weekday: "short", month: "short", day: "numeric" });
      partsFormat = new Intl.DateTimeFormat("en-US", { timeZone: zone, hour: "numeric", hourCycle: "h23", month: "numeric" });
    } catch {
      return;
    }
    const renderedHour = Number(root.dataset.islandHour);
    const renderedMonth = Number(root.dataset.islandMonth);
    const planning = root.hasAttribute("data-planning");
    let notified = false;

    const tick = () => {
      const now = new Date();
      const time = timeFormat.format(now);
      const date = dateFormat.format(now);
      timeElements.forEach((element) => {
        if (element.textContent !== time) element.textContent = time;
      });
      dateElements.forEach((element) => {
        if (element.textContent !== date) element.textContent = date;
      });
      if (planning || notified || Number.isNaN(renderedHour)) return;
      const parts = partsFormat.formatToParts(now);
      const hour = Number(parts.find((part) => part.type === "hour")?.value);
      const month = Number(parts.find((part) => part.type === "month")?.value);
      if (hour !== renderedHour || month !== renderedMonth) {
        notified = true;
        toast(`It's ${formatHour(hour)} on your island. New critters may be out.`, {
          icon: "clock",
          action: "Refresh",
          onAction: () => location.reload(),
        });
      }
    };

    tick();
    window.setTimeout(() => {
      tick();
      window.setInterval(tick, 1000);
    }, 1000 - (Date.now() % 1000));
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden) tick();
    });
  }

  function initIslandForm() {
    const details = document.querySelector("[data-island-bar]");
    const form = document.querySelector("[data-island-form]");
    if (!(details instanceof HTMLDetailsElement) || !(form instanceof HTMLFormElement)) return;

    try {
      if (sessionStorage.getItem(ISLAND_OPEN_KEY)) {
        details.open = true;
        sessionStorage.removeItem(ISLAND_OPEN_KEY);
      }
    } catch {
      // sessionStorage unavailable; the panel just starts closed.
    }

    let pending = 0;
    const submit = (delay = 0) => {
      window.clearTimeout(pending);
      pending = window.setTimeout(() => {
        const data = new FormData(form);
        const params = new URLSearchParams();
        for (const key of ["hemisphere", "timezone"]) {
          const value = data.get(key);
          if (typeof value === "string" && value) params.set(key, value);
        }
        if (data.get("when") === "plan") {
          for (const key of ["month", "hour"]) {
            const value = data.get(key);
            if (typeof value === "string") params.set(key, value);
          }
        }
        try {
          sessionStorage.setItem(ISLAND_OPEN_KEY, "1");
        } catch {
          // Ignore: only affects whether the panel reopens.
        }
        location.assign(`${form.getAttribute("action") || location.pathname}?${params}`);
      }, delay);
    };

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      submit();
    });
    form.addEventListener("change", (event) => {
      const target = event.target;
      if (target instanceof HTMLInputElement && target.name === "when" && target.value === "plan") {
        const month = form.elements.namedItem("month");
        if (month instanceof HTMLSelectElement) month.focus();
        return;
      }
      submit(target instanceof HTMLSelectElement ? 350 : 0);
    });

    const select = form.elements.namedItem("timezone");
    const deviceButton = form.querySelector("[data-device-timezone]");
    let deviceZone = "";
    try {
      deviceZone = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    } catch {
      return;
    }
    if (!(select instanceof HTMLSelectElement) || !(deviceButton instanceof HTMLButtonElement)) return;
    if (!deviceZone || deviceZone === select.value) return;
    deviceButton.hidden = false;
    deviceButton.addEventListener("click", () => {
      if (![...select.options].some((option) => option.value === deviceZone)) {
        select.add(new Option(deviceZone.replace(/_/g, " "), deviceZone), 0);
      }
      select.value = deviceZone;
      submit();
    });
  }

  /** @param {HTMLElement} button */
  function celebrate(button) {
    button.classList.remove("is-popping");
    void button.offsetWidth;
    button.classList.add("is-popping");
    if (reducedMotion.matches) return;
    const colors = ["var(--leaf)", "var(--bell)", "var(--sky)", "var(--rose)", "var(--violet)"];
    for (let i = 0; i < 12; i += 1) {
      const piece = document.createElement("span");
      const angle = (Math.PI * 2 * i) / 12 + Math.random() * 0.4;
      const distance = 28 + Math.random() * 22;
      piece.className = "confetti";
      piece.style.background = colors[i % colors.length];
      piece.style.setProperty("--x", `${Math.cos(angle) * distance}px`);
      piece.style.setProperty("--y", `${Math.sin(angle) * distance}px`);
      piece.style.setProperty("--r", `${Math.round(Math.random() * 360)}deg`);
      button.append(piece);
      window.setTimeout(() => piece.remove(), 800);
    }
  }

  /** @param {string} value */
  const normalizeQuery = (value) => value.trim().toLowerCase().replace(/[‘’]/g, "'");

  /** @param {EventTarget | null} target */
  const isTypingTarget = (target) =>
    target instanceof HTMLElement && (target.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName));

  function initCritterPage() {
    const grid = document.querySelector("[data-critter-grid]");
    if (!(grid instanceof HTMLElement)) return;
    const kind = grid.dataset.kind || "";
    const singular = grid.dataset.singular || "critter";
    const plural = grid.dataset.plural || "critters";
    const planning = root.hasAttribute("data-planning");

    const search = document.querySelector("[data-search]");
    const searchClear = document.querySelector("[data-search-clear]");
    const sortSelect = document.querySelector("[data-sort]");
    const hideCaughtInput = document.querySelector("[data-hide-caught]");
    const counter = document.querySelector("[data-count]");
    const empty = document.querySelector("[data-empty]");
    const emptyTitle = document.querySelector("[data-empty-title]");
    const emptyText = document.querySelector("[data-empty-text]");
    const resetButton = document.querySelector("[data-reset]");
    const viewInputs = [...document.querySelectorAll("input[data-view]")].filter(
      /** @returns {input is HTMLInputElement} */ (input) => input instanceof HTMLInputElement,
    );
    const tagButtons = [...document.querySelectorAll("button[data-tag]")].filter(
      /** @returns {button is HTMLButtonElement} */ (button) => button instanceof HTMLButtonElement,
    );
    const focusButtons = [...document.querySelectorAll("button[data-focus]")].filter(
      /** @returns {button is HTMLButtonElement} */ (button) => button instanceof HTMLButtonElement,
    );
    if (
      !(search instanceof HTMLInputElement) ||
      !(searchClear instanceof HTMLButtonElement) ||
      !(sortSelect instanceof HTMLSelectElement) ||
      !(hideCaughtInput instanceof HTMLInputElement) ||
      !(empty instanceof HTMLElement)
    ) {
      return;
    }

    /** @type {CardInfo[]} */
    const infos = [];
    grid.querySelectorAll("[data-critter]").forEach((card, index) => {
      const nameEl = card.querySelector("[data-critter-name]");
      const catchButton = card.querySelector("[data-catch]");
      if (!(card instanceof HTMLElement) || !(nameEl instanceof HTMLElement) || !(catchButton instanceof HTMLButtonElement)) return;
      infos.push({
        card,
        index,
        number: Number(card.dataset.number),
        name: card.dataset.name || "",
        search: card.dataset.search || "",
        price: Number(card.dataset.price),
        available: card.dataset.available === "1",
        isNew: card.dataset.new === "1",
        leaving: card.dataset.leaving === "1",
        monthsLeft: Number(card.dataset.monthsLeft) || 0,
        tags: (card.dataset.tags || "").split(" ").filter(Boolean),
        nameEl,
        displayName: nameEl.textContent || "",
        catchButton,
      });
    });
    const byElement = new Map(infos.map((info) => [info.card, info]));
    const prefs = loadPrefs();
    /** @type {{ query: string, view: View, sort: SortKey, hideCaught: boolean, tag: string, focus: Focus }} */
    const state = { query: "", view: prefs.view, sort: prefs.sort, hideCaught: prefs.hideCaught, tag: "", focus: "" };
    let caught = loadCaught(kind);

    const savePrefs = () => writeJSON(PREFS_KEY, { view: state.view, sort: state.sort, hideCaught: state.hideCaught });

    /** @param {CardInfo} info @param {boolean} [ignoreCaught] */
    const matches = (info, ignoreCaught = false) =>
      (state.view === "all" || info.available) &&
      (ignoreCaught || !state.hideCaught || !caught.has(info.number)) &&
      (!state.tag || info.tags.includes(state.tag)) &&
      (state.focus !== "new" || info.isNew) &&
      (state.focus !== "leaving" || info.leaving) &&
      (!state.query || info.search.includes(state.query));

    /** @param {CardInfo} a @param {CardInfo} b */
    const order = (a, b) => {
      const grouped = state.view === "all" && state.sort !== "number";
      return (grouped ? Number(b.available) - Number(a.available) : 0) || COMPARE[state.sort](a, b);
    };

    /** @param {CardInfo} info */
    const highlight = (info) => {
      const text = info.displayName;
      const lower = text.toLowerCase();
      let index = state.query ? lower.indexOf(state.query) : -1;
      if (index === -1) {
        if (info.nameEl.childElementCount || info.nameEl.textContent !== text) info.nameEl.textContent = text;
        return;
      }
      const fragment = document.createDocumentFragment();
      let last = 0;
      while (index !== -1) {
        fragment.append(text.slice(last, index));
        const mark = document.createElement("mark");
        mark.textContent = text.slice(index, index + state.query.length);
        fragment.append(mark);
        last = index + state.query.length;
        index = lower.indexOf(state.query, last);
      }
      fragment.append(text.slice(last));
      info.nameEl.replaceChildren(fragment);
    };

    /** @param {CardInfo} info */
    const applyCaught = (info) => {
      const isCaught = caught.has(info.number);
      info.card.classList.toggle("is-caught", isCaught);
      info.catchButton.setAttribute("aria-pressed", String(isCaught));
      info.catchButton.title = isCaught ? "Caught! Click to undo" : "Mark as caught";
    };

    const caughtCount = () => infos.filter((info) => caught.has(info.number)).length;

    /** @param {number} shown */
    const updateEmpty = (shown) => {
      empty.hidden = shown > 0;
      if (shown > 0 || !(emptyTitle instanceof HTMLElement) || !(emptyText instanceof HTMLElement)) return;
      const moment = planning ? "then" : "right now";
      if (state.query) {
        emptyTitle.textContent = `No ${plural} match “${search.value.trim()}”`;
        emptyText.textContent = "Check the spelling, or search for a place like “river” or “trees”.";
      } else if (state.hideCaught && infos.some((info) => matches(info, true))) {
        emptyTitle.textContent = `You've caught every ${singular} that's out ${moment}!`;
        emptyText.textContent = "Nice work. Turn off “Hide caught” to see them again, or check back next hour.";
      } else {
        emptyTitle.textContent = `No ${plural} here ${moment}`;
        emptyText.textContent = "Try another filter, or switch to All to browse the whole Critterpedia.";
      }
    };

    /** @param {{ animate?: boolean }} [options] */
    const render = ({ animate = true } = {}) => {
      const visible = infos.filter((info) => matches(info)).sort(order);
      const shown = new Set(visible);
      const hidden = infos.filter((info) => !shown.has(info)).sort((a, b) => a.index - b.index);
      const fragment = document.createDocumentFragment();
      visible.forEach((info, position) => {
        info.card.style.setProperty("--i", String(position));
        info.card.hidden = false;
        fragment.append(info.card);
      });
      hidden.forEach((info) => {
        info.card.hidden = true;
        fragment.append(info.card);
      });
      grid.append(fragment);
      infos.forEach(highlight);
      if (counter) counter.textContent = `${visible.length} ${visible.length === 1 ? singular : plural}`;
      updateEmpty(visible.length);
      if (animate && !reducedMotion.matches) {
        grid.classList.remove("is-reshuffled");
        void grid.offsetWidth;
        grid.classList.add("is-reshuffled");
      }
    };

    const syncControls = () => {
      viewInputs.forEach((input) => {
        input.checked = input.value === state.view;
      });
      sortSelect.value = state.sort;
      hideCaughtInput.checked = state.hideCaught;
      tagButtons.forEach((button) => button.setAttribute("aria-pressed", String((button.dataset.tag || "") === state.tag)));
      focusButtons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.focus === state.focus)));
      searchClear.hidden = !search.value;
    };

    /** @param {string} hash */
    const spotlight = (hash) => {
      const target = hash.startsWith("#critter-") ? document.getElementById(hash.slice(1)) : null;
      const info = target ? byElement.get(target) : undefined;
      if (!info) return;
      if (!matches(info)) {
        Object.assign(state, { query: "", tag: "", focus: "", hideCaught: false, view: "all" });
        search.value = "";
        syncControls();
        render({ animate: false });
      }
      requestAnimationFrame(() => {
        info.card.scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth", block: "center" });
        info.card.classList.remove("is-spotlit");
        void info.card.offsetWidth;
        info.card.classList.add("is-spotlit");
        window.setTimeout(() => info.card.classList.remove("is-spotlit"), 2700);
      });
    };

    grid.removeAttribute("data-view");
    infos.forEach(applyCaught);
    syncControls();
    render({ animate: false });
    renderDex(kind, caughtCount(), true);
    if (location.hash) spotlight(location.hash);

    search.addEventListener("input", () => {
      state.query = normalizeQuery(search.value);
      searchClear.hidden = !search.value;
      render({ animate: false });
    });
    search.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && search.value) {
        event.preventDefault();
        searchClear.click();
      }
    });
    searchClear.addEventListener("click", () => {
      search.value = "";
      state.query = "";
      searchClear.hidden = true;
      render({ animate: false });
      search.focus();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "/" && !event.metaKey && !event.ctrlKey && !event.altKey && !isTypingTarget(event.target)) {
        event.preventDefault();
        search.focus();
      }
    });
    viewInputs.forEach((input) =>
      input.addEventListener("change", () => {
        state.view = input.value === "all" ? "all" : "available";
        savePrefs();
        render();
      }),
    );
    sortSelect.addEventListener("change", () => {
      state.sort = sortSelect.value in COMPARE ? /** @type {SortKey} */ (sortSelect.value) : "value";
      savePrefs();
      render();
    });
    hideCaughtInput.addEventListener("change", () => {
      state.hideCaught = hideCaughtInput.checked;
      savePrefs();
      render();
    });
    tagButtons.forEach((button) =>
      button.addEventListener("click", () => {
        state.tag = button.dataset.tag || "";
        syncControls();
        render();
      }),
    );
    focusButtons.forEach((button) =>
      button.addEventListener("click", () => {
        const focus = button.dataset.focus === "new" || button.dataset.focus === "leaving" ? button.dataset.focus : "";
        state.focus = state.focus === focus ? "" : focus;
        if (state.focus) state.view = "all";
        syncControls();
        render();
      }),
    );
    resetButton?.addEventListener("click", () => {
      Object.assign(state, { query: "", tag: "", focus: "", hideCaught: false });
      search.value = "";
      savePrefs();
      syncControls();
      render();
    });

    grid.addEventListener("click", (event) => {
      const button = event.target instanceof Element ? event.target.closest("[data-catch]") : null;
      const card = button?.closest("[data-critter]");
      const info = card instanceof HTMLElement ? byElement.get(card) : undefined;
      if (!info) return;
      const nowCaught = !caught.has(info.number);
      if (nowCaught) caught.add(info.number);
      else caught.delete(info.number);
      saveCaught(kind, caught);
      applyCaught(info);
      renderDex(kind, caughtCount(), false);
      if (nowCaught) celebrate(info.catchButton);
      if (state.hideCaught && nowCaught) {
        window.setTimeout(() => {
          const next = infos.filter((other) => matches(other)).sort(order).find((other) => other !== info && order(other, info) > 0);
          render({ animate: false });
          if (document.activeElement === document.body || document.activeElement === info.catchButton) next?.catchButton.focus();
        }, reducedMotion.matches ? 0 : 480);
      }
    });

    window.addEventListener("hashchange", () => spotlight(location.hash));
    window.addEventListener("storage", (event) => {
      if (event.key !== CAUGHT_KEY) return;
      caught = loadCaught(kind);
      infos.forEach(applyCaught);
      renderDex(kind, caughtCount(), false);
      if (state.hideCaught) render({ animate: false });
    });
  }

  function initHome() {
    document.querySelectorAll(".kind-card__dex[data-dex]").forEach((element) => {
      if (element instanceof HTMLElement && element.dataset.dex) renderDex(element.dataset.dex, loadCaught(element.dataset.dex).size, false);
    });
    document.querySelectorAll("[data-count-to]").forEach((element) => {
      if (element instanceof HTMLElement) countUp(element, Number(element.dataset.countTo) || 0);
    });
  }

  startClock();
  initIslandForm();
  initCritterPage();
  initHome();
})();
