// Wyłącznie narzędzia lokalnej makiety. Bez API i bez zapisu rozmowy.
const root = document.documentElement;
const themeButton = document.querySelector("[data-theme-toggle]");
function setTheme(theme) {
  root.dataset.theme = theme;
  if (themeButton) {
    themeButton.textContent = theme === "dark" ? "☀ Jasny" : "◐ Ciemny";
    themeButton.setAttribute("aria-label", `Podgląd: włącz motyw ${theme === "dark" ? "jasny" : "ciemny"}`);
  }
}
// Celowo jasny start, bez pamięci wyboru i bez odczytu ustawień systemu.
// To zachowanie podglądu, nie decyzja dla aplikacji.
setTheme("light");
themeButton?.addEventListener("click", () => setTheme(root.dataset.theme === "dark" ? "light" : "dark"));

const feedback = document.querySelector("[data-feedback]");
function notify(text, kind = "info") {
  if (feedback) { feedback.textContent = text; feedback.dataset.kind = kind; }
}
document.querySelector("[data-download-demo]")?.addEventListener("click", () => {
  const sample = "-- DEMONSTRACJA MAKIETY UI — NIE JEST WYNIKIEM GENEROWANIA\n-- Brak kompletnej paczki i brak rzeczywistej walidacji.\n-- 50 klientów, 30 produktów, 200 zamówień, 600 pozycji to fikcyjny scenariusz ekranu.\n";
  const url = URL.createObjectURL(new Blob([sample], { type: "text/plain;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url; link.download = "demonstracja-makiety-NIE-DANE.sql"; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  notify("Pobrano wyłącznie opis demonstracji, nie paczkę danych. Makieta nie generuje ani nie sprawdza SQL.");
});
document.querySelector("[data-report-button]")?.addEventListener("click", () => {
  const report = document.querySelector("[data-report]");
  report.open = !report.open;
  if (report.open) report.scrollIntoView({ block: "nearest" });
});
document.querySelector("[data-report]")?.addEventListener("toggle", event => {
  document.querySelector("[data-report-button]").setAttribute("aria-expanded", String(event.target.open));
});
document.querySelector("[data-composer]")?.addEventListener("submit", event => {
  event.preventDefault();
  const input = document.querySelector("#prompt");
  if (!input.value.trim()) {
    input.setAttribute("aria-invalid", "true");
    notify("Wpisz polecenie, aby zobaczyć informację o symulacji.", "error");
    input.focus();
    return;
  }
  input.removeAttribute("aria-invalid");
  notify("To demonstracja interfejsu. Polecenie nie zostało wysłane do modelu; dane i wynik pozostają bez zmian.");
});
const dialog = document.querySelector("[data-new-chat-dialog]");
dialog?.addEventListener("keydown", event => {
  if (event.key !== "Tab") return;
  const buttons = [...dialog.querySelectorAll("button:not(:disabled)")];
  const first = buttons[0], last = buttons[buttons.length - 1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
});
document.querySelectorAll("[data-new-chat]").forEach(button => button.addEventListener("click", () => dialog.showModal()));
document.querySelector("[data-stay]")?.addEventListener("click", () => dialog.close());
document.querySelector("[data-confirm-new]")?.addEventListener("click", () => {
  dialog.close();
  document.querySelector("[data-messages]").hidden = true;
  document.querySelector("[data-intro-title]").textContent = "Co chcesz wygenerować?";
  document.querySelector("[data-intro-text]").textContent = "Projekt Sklep internetowy pozostaje wybrany. Opisz dane, których potrzebujesz.";
  document.querySelector("#prompt").value = "";
  document.querySelector("#prompt").removeAttribute("aria-invalid");
  document.querySelector("[data-chat-state]").textContent = "Nowy czat";
  notify("Podgląd pustej rozmowy. Odświeżenie makiety przywraca demonstracyjny wynik — to nie cykl życia docelowej aplikacji.");
  document.querySelector("#prompt").focus();
});
