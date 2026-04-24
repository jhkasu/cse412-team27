const CATEGORY_EMOJI = [
  [/baby/i, "🍼"],
  [/yogurt/i, "🥛"],
  [/cheese/i, "🧀"],
  [/dairy|milk/i, "🥛"],
  [/bread|bagel|muffin|biscuit|pastry|doughnut|pancake|waffle/i, "🍞"],
  [/cake|pie|cookie|brownie|dessert|sweet|candy|chocolate/i, "🍰"],
  [/ice cream|sorbet|gelatin/i, "🍦"],
  [/pizza/i, "🍕"],
  [/burger|sandwich/i, "🍔"],
  [/fast food/i, "🍟"],
  [/mexican|tortilla|taco/i, "🌮"],
  [/asian|rice|noodle/i, "🍜"],
  [/soup|broth|gravy|sauce/i, "🍲"],
  [/salad|lettuce|coleslaw/i, "🥗"],
  [/fruit|juice|smoothie|berr/i, "🍎"],
  [/vegetable|veggie/i, "🥦"],
  [/nut|seed|peanut/i, "🥜"],
  [/cereal|oatmeal|grain/i, "🥣"],
  [/poultry|chicken|turkey/i, "🍗"],
  [/beef|pork|meat|sausage/i, "🥩"],
  [/fish|seafood|shrimp/i, "🐟"],
  [/egg/i, "🥚"],
  [/beverage|drink|water|tea|coffee/i, "🥤"],
  [/liquor|cocktail|wine|beer/i, "🍷"],
  [/snack|chip|popcorn|cracker|pretzel/i, "🍿"],
  [/jam|syrup|topping|sugar|spread/i, "🍯"],
  [/oil|dressing|fat/i, "🫒"],
  [/bar/i, "🍫"],
];

function prettifyName(raw, categoryName) {
  let s = String(raw || "").trim();
  const prefixes = [categoryName, "Snacks", "Snack", "Beverages", "Soups",
                    "Cereals", "Cookies", "Candies", "Fast Foods"];
  for (const p of prefixes) {
    if (!p) continue;
    const re = new RegExp("^" + p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\s*,\\s*", "i");
    if (re.test(s)) { s = s.replace(re, ""); break; }
  }
  s = s.replace(/\b[A-Z][A-Z'&]{3,}\b/g, (w) =>
    w.charAt(0) + w.slice(1).toLowerCase()
  );
  const lastComma = s.lastIndexOf(", ");
  if (lastComma > 0 && s.length - lastComma < 40) {
    s = s.slice(0, lastComma) + " — " + s.slice(lastComma + 2);
  }
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function emojiFor(name) {
  for (const [re, emoji] of CATEGORY_EMOJI) {
    if (re.test(name)) return emoji;
  }
  return "🍽️";
}

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

let activeCategoryId = null;
let currentUser = null;
let authMode = "signin";

function getStoredUser() {
  try { return JSON.parse(localStorage.getItem("nc_user") || "null"); }
  catch { return null; }
}
function setStoredUser(u) {
  if (u) localStorage.setItem("nc_user", JSON.stringify(u));
  else localStorage.removeItem("nc_user");
  currentUser = u;
  renderAuthState();
  refreshCompareCount();
}

function renderAuthState() {
  const loggedIn = !!currentUser;
  $("#nav-signin").classList.toggle("hidden", loggedIn);
  $("#nav-signup").classList.toggle("hidden", loggedIn);
  $("#nav-user").classList.toggle("hidden", !loggedIn);
  if (loggedIn) $("#nav-user-email").textContent = currentUser.email;
}

function openModal(id) { $("#" + id).classList.remove("hidden"); }
function closeModal(id) { $("#" + id).classList.add("hidden"); }

function openAuth(mode) {
  authMode = mode;
  $("#auth-title").textContent = mode === "signup" ? "Create account" : "Sign in";
  $("#auth-submit").textContent = mode === "signup" ? "Create account" : "Sign in";
  $("#auth-switch-text").textContent = mode === "signup" ? "Already have an account?" : "New here?";
  $("#auth-switch").textContent = mode === "signup" ? "Sign in" : "Create an account";
  $("#auth-form").reset();
  $("#auth-error").classList.add("hidden");
  openModal("auth-modal");
}

async function loadCategories() {
  const res = await fetch("/api/categories?limit=25");
  const cats = await res.json();
  const grid = $("#category-grid");
  grid.innerHTML = "";
  cats.forEach((c) => {
    const tile = document.createElement("div");
    tile.className = "category-tile";
    tile.dataset.id = c.category_id;
    tile.innerHTML = `
      <div class="icon">${emojiFor(c.name)}</div>
      <div class="label">${escapeHtml(c.name)}</div>
    `;
    tile.addEventListener("click", () => selectCategory(c));
    grid.appendChild(tile);
  });
  if (cats.length) selectCategory(cats[0]);
}

async function selectCategory(cat) {
  activeCategoryId = cat.category_id;
  $$(".category-tile").forEach((t) =>
    t.classList.toggle("active", Number(t.dataset.id) === cat.category_id)
  );
  $("#explore-title").textContent = cat.name;
  $("#search-input").value = "";
  const res = await fetch(`/api/foods?category_id=${cat.category_id}`);
  renderFoods(await res.json(), cat.name);
}

function renderFoods(foods, fallbackCategory) {
  const grid = $("#food-grid");
  if (!foods.length) {
    grid.innerHTML = `<div class="empty">No foods found.</div>`;
    return;
  }
  grid.innerHTML = "";
  foods.forEach((f) => {
    const card = document.createElement("div");
    card.className = "food-card";
    const cat = f.category_name || fallbackCategory || "";
    card.innerHTML = `
      <div class="name">${escapeHtml(prettifyName(f.description, cat))}</div>
      <div class="meta">${escapeHtml(cat)}</div>
      <div class="emoji">${emojiFor(cat)}</div>
    `;
    card.addEventListener("click", () => openFoodDetail(f.fdc_id));
    grid.appendChild(card);
  });
}

async function openFoodDetail(fdc_id) {
  $("#modal-body").innerHTML = `<div class="loading">Loading...</div>`;
  openModal("modal");
  const res = await fetch(`/api/food/${fdc_id}`);
  const data = await res.json();
  const rows = data.nutrients
    .filter((n) => n.amount && n.amount > 0)
    .map((n) => `<tr><td>${escapeHtml(n.nutrient)}</td><td>${formatAmount(n.amount)}</td></tr>`)
    .join("");
  $("#modal-body").innerHTML = `
    <h3>${escapeHtml(prettifyName(data.description, data.category_name))}</h3>
    <div class="modal-meta">${escapeHtml(data.category_name || "")} · ${escapeHtml(data.data_type)} · FDC ID ${data.fdc_id}</div>
    <div class="modal-action-row">
      <button class="btn-primary" id="add-to-compare-btn">Add to comparison</button>
    </div>
    <h4>Nutrients</h4>
    <table class="nutrient-table"><tbody>${rows || '<tr><td colspan="2" class="empty">No nutrient data.</td></tr>'}</tbody></table>
  `;
  $("#add-to-compare-btn").addEventListener("click", () => addToCompare(data.fdc_id));
}

async function addToCompare(fdc_id) {
  if (!currentUser) {
    closeModal("modal");
    openAuth("signin");
    return;
  }
  const btn = $("#add-to-compare-btn");
  btn.disabled = true;
  btn.textContent = "Adding...";
  try {
    const res = await fetch("/api/comparison", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fdc_id, user_id: currentUser.user_id }),
    });
    if (!res.ok) throw new Error(await res.text());
    btn.textContent = "Added ✓";
    refreshCompareCount();
  } catch (e) {
    btn.disabled = false;
    btn.textContent = "Add to comparison";
    alert("Failed to add: " + e.message);
  }
}

async function refreshCompareCount() {
  const badge = $("#compare-count");
  if (!currentUser) { badge.classList.add("hidden"); badge.textContent = "0"; return; }
  try {
    const res = await fetch(`/api/comparison?user_id=${currentUser.user_id}`);
    if (!res.ok) throw new Error();
    const items = await res.json();
    if (items.length) {
      badge.textContent = items.length;
      badge.classList.remove("hidden");
    } else {
      badge.classList.add("hidden");
    }
  } catch {
    badge.classList.add("hidden");
  }
}

async function openCompare() {
  openModal("compare-modal");
  const body = $("#compare-body");
  if (!currentUser) {
    body.innerHTML = `<div class="empty">Sign in to save and compare foods.</div>`;
    return;
  }
  body.innerHTML = `<div class="loading">Loading...</div>`;
  try {
    const res = await fetch(`/api/comparison?user_id=${currentUser.user_id}`);
    if (!res.ok) throw new Error("failed");
    const items = await res.json();
    if (!items.length) {
      body.innerHTML = `<div class="empty">No foods saved yet. Open a food and click "Add to comparison".</div>`;
      return;
    }
    renderCompareTable(items);
  } catch {
    body.innerHTML = `<div class="empty">Could not load comparison.</div>`;
  }
}

function renderCompareTable(items) {
  const nutrientSet = new Set();
  items.forEach((f) => (f.nutrients || []).forEach((n) => nutrientSet.add(n.nutrient)));
  const nutrients = [...nutrientSet].sort();

  const headers = items.map((f) => `
    <th class="numeric">
      <div>${escapeHtml(prettifyName(f.description, f.category_name))}</div>
      <button class="compare-remove" data-fdc="${f.fdc_id}">Remove</button>
    </th>
  `).join("");

  const rows = nutrients.map((name) => {
    const cells = items.map((f) => {
      const n = (f.nutrients || []).find((x) => x.nutrient === name);
      return `<td class="numeric">${n && n.amount ? formatAmount(n.amount) : "—"}</td>`;
    }).join("");
    return `<tr><td>${escapeHtml(name)}</td>${cells}</tr>`;
  }).join("");

  $("#compare-body").innerHTML = `
    <table class="compare-table">
      <thead><tr><th>Nutrient</th>${headers}</tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
  $$(".compare-remove").forEach((b) =>
    b.addEventListener("click", () => removeFromCompare(b.dataset.fdc))
  );
}

async function removeFromCompare(fdc_id) {
  try {
    const res = await fetch(`/api/comparison/${fdc_id}?user_id=${currentUser.user_id}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error();
    openCompare();
    refreshCompareCount();
  } catch {
    alert("Failed to remove");
  }
}

async function openSettings() {
  if (!currentUser) { openAuth("signin"); return; }
  openModal("settings-modal");
  $("#settings-error").classList.add("hidden");
  $("#settings-form").reset();
  try {
    const res = await fetch(`/api/preferences?user_id=${currentUser.user_id}`);
    if (!res.ok) return;
    const prefs = await res.json();
    const map = {};
    prefs.forEach((p) => (map[p.preference_key] = p.preference_value));
    const form = $("#settings-form");
    if (map.calorie_target) form.calorie_target.value = map.calorie_target;
    if (map.diet) form.diet.value = map.diet;
    if (map.allergies) form.allergies.value = map.allergies;
  } catch {}
}

async function submitAuth(e) {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = { email: fd.get("email"), password: fd.get("password") };
  const url = authMode === "signup" ? "/api/signup" : "/api/signin";
  const errBox = $("#auth-error");
  errBox.classList.add("hidden");
  $("#auth-submit").disabled = true;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(txt || "Request failed");
    }
    const user = await res.json();
    setStoredUser(user);
    closeModal("auth-modal");
  } catch (err) {
    errBox.textContent = err.message;
    errBox.classList.remove("hidden");
  } finally {
    $("#auth-submit").disabled = false;
  }
}

async function submitSettings(e) {
  e.preventDefault();
  const fd = new FormData(e.target);
  const prefs = [
    { preference_key: "calorie_target", preference_value: fd.get("calorie_target") || "" },
    { preference_key: "diet", preference_value: fd.get("diet") || "" },
    { preference_key: "allergies", preference_value: fd.get("allergies") || "" },
  ].filter((p) => p.preference_value !== "");
  const errBox = $("#settings-error");
  errBox.classList.add("hidden");
  try {
    const res = await fetch(`/api/preferences?user_id=${currentUser.user_id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preferences: prefs }),
    });
    if (!res.ok) throw new Error(await res.text() || "Save failed");
    closeModal("settings-modal");
  } catch (err) {
    errBox.textContent = err.message;
    errBox.classList.remove("hidden");
  }
}

function signOut() {
  setStoredUser(null);
  $("#nav-user-menu").classList.add("hidden");
}

function formatAmount(n) {
  if (n >= 100) return n.toFixed(0);
  if (n >= 1) return n.toFixed(2);
  return n.toFixed(3);
}

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

let searchTimer = null;
$("#search-input").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  const q = e.target.value.trim();
  searchTimer = setTimeout(async () => {
    if (!q) {
      if (activeCategoryId) {
        const res = await fetch(`/api/foods?category_id=${activeCategoryId}`);
        renderFoods(await res.json());
      }
      return;
    }
    $("#explore-title").textContent = `Search results for "${q}"`;
    $$(".category-tile").forEach((t) => t.classList.remove("active"));
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    renderFoods(await res.json());
  }, 200);
});

$("#modal-close").addEventListener("click", () => closeModal("modal"));
$$("[data-close]").forEach((b) =>
  b.addEventListener("click", () => closeModal(b.dataset.close))
);
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-backdrop")) {
    e.target.parentElement.classList.add("hidden");
  }
});

$("#nav-signin").addEventListener("click", () => openAuth("signin"));
$("#nav-signup").addEventListener("click", () => openAuth("signup"));
$("#auth-switch").addEventListener("click", () =>
  openAuth(authMode === "signup" ? "signin" : "signup")
);
$("#auth-form").addEventListener("submit", submitAuth);
$("#settings-form").addEventListener("submit", submitSettings);
$("#nav-compare").addEventListener("click", openCompare);
$("#nav-settings").addEventListener("click", () => {
  $("#nav-user-menu").classList.add("hidden");
  openSettings();
});
$("#nav-signout").addEventListener("click", signOut);
$("#nav-user-button").addEventListener("click", (e) => {
  e.stopPropagation();
  $("#nav-user-menu").classList.toggle("hidden");
});
document.addEventListener("click", (e) => {
  if (!e.target.closest("#nav-user")) {
    $("#nav-user-menu").classList.add("hidden");
  }
});

currentUser = getStoredUser();
renderAuthState();
refreshCompareCount();
loadCategories();
